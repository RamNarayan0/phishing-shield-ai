import os
import time
import uuid
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb import (
    init_db,
    close_db,
    check_health,
    is_connected,
    generate_fingerprint,
    save_alert,
    get_recent_alerts,
    get_collection,
    _client,
    MONGODB_DATABASE
)

from app.db.cleanup import clean_duplicates
from app.core.security import rate_limiter, sanitize_for_log

client = TestClient(app)

@pytest.fixture(autouse=True)
def ensure_db_ready():
    """Ensures MongoDB connection is active before each test, and resets rate limiter."""
    init_db()
    rate_limiter.reset()
    yield

# =====================================================================
# 1. Successful MongoDB Connection & Health Check
# =====================================================================
def test_mongodb_connection_and_health():
    health = check_health()
    assert health is not None
    assert "status" in health
    assert "database" in health
    if is_connected():
        assert health["status"] == "connected"
        assert "ping_latency_ms" in health
        assert health["ping_latency_ms"] >= 0

def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "status" in data["database"]

# =====================================================================
# 2. Database Unavailable / Connection Timeout Fallback
# =====================================================================
def test_mongodb_unavailable_fallback():
    # Attempt connecting to invalid unreachable port with short timeout
    fallback_ok = init_db(uri="mongodb://127.0.0.1:27999")
    assert fallback_ok is False
    assert is_connected() is False

    # Verify fallback health report
    health = check_health()
    assert health["status"] == "disconnected"
    assert health["backend_storage"] == "in-memory-fallback"

    # In-memory save should still work without throwing exceptions
    test_record = {
        "id": "fallback-test",
        "raw_text": "Testing fallback mode",
        "result": {"verdict": "SAFE", "risk_score": 0}
    }
    saved = save_alert(test_record)
    assert saved["id"] == "fallback-test"

    # Restore healthy connection
    init_db()

# =====================================================================
# 3. Saving Valid Analysis Record with Explanation
# =====================================================================
def test_save_valid_analysis_record():
    test_id = str(uuid.uuid4())[:8]
    record = {
        "id": test_id,
        "source_platform": "web_test",
        "raw_text": f"Security alert test for user account {test_id}",
        "sender_id": "security@test-bank.com",
        "result": {
            "verdict": "CRITICAL",
            "risk_score": 90,
            "explanation": {
                "summary": "Flagged as CRITICAL risk (90/100).",
                "signals": [],
                "categories": {},
                "recommended_action": "DO NOT INTERACT"
            }
        }
    }
    saved = save_alert(record)
    assert "fingerprint" in saved
    assert len(saved["fingerprint"]) == 64  # SHA-256 hex string

    recent = get_recent_alerts(10)
    found = next((r for r in recent if r.get("id") == test_id), None)
    assert found is not None
    assert found["result"]["verdict"] == "CRITICAL"

# =====================================================================
# 4. Detecting Duplicate Submissions & Idempotent Behavior
# =====================================================================
def test_detect_duplicate_submissions_and_idempotency():
    unique_text = f"Duplicate test payload {uuid.uuid4()}"
    rec1 = {
        "id": "first-run",
        "source_platform": "web",
        "sender_id": "alert@corp.com",
        "raw_text": unique_text,
        "result": {"verdict": "SAFE", "risk_score": 0}
    }
    rec2 = {
        "id": "second-run",
        "source_platform": "web",
        "sender_id": "alert@corp.com",
        "raw_text": unique_text,
        "result": {"verdict": "SAFE", "risk_score": 0}
    }

    res1 = save_alert(rec1)
    assert res1["is_duplicate"] is False
    assert res1["duplicate_count"] == 1

    res2 = save_alert(rec2)
    assert res2["is_duplicate"] is True
    assert res2["duplicate_count"] >= 2
    assert res1["fingerprint"] == res2["fingerprint"]

    # Verify that in database, only 1 record exists with this fingerprint
    coll = get_collection()
    if is_connected() and coll is not None:
        count = coll.count_documents({"fingerprint": res1["fingerprint"]})
        assert count == 1

# =====================================================================
# 5. Unique Index Enforcement Under Concurrent Submissions
# =====================================================================
def test_concurrent_submissions_unique_index():
    concurrent_text = f"Concurrent blast test {uuid.uuid4()}"

    def worker(worker_id):
        return save_alert({
            "id": f"worker-{worker_id}",
            "source_platform": "load_test",
            "raw_text": concurrent_text,
            "result": {"verdict": "HIGH RISK", "risk_score": 75}
        })

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(worker, range(5)))

    assert len(results) == 5
    fp = results[0]["fingerprint"]

    # Exactly 1 record should be stored in collection
    coll = get_collection()
    if is_connected() and coll is not None:
        count = coll.count_documents({"fingerprint": fp})
        assert count == 1

# =====================================================================
# 6. Fingerprint Normalization Logic
# =====================================================================
def test_fingerprint_normalization():
    # Spacing and casing variations of the same content must produce the identical fingerprint
    fp1 = generate_fingerprint("  URGENT: Verify   Account! ", sender_id="ALERTS@BANK.COM", source_platform="WEB")
    fp2 = generate_fingerprint("urgent: verify account!", sender_id="alerts@bank.com", source_platform="web")
    assert fp1 == fp2

    # Different text must produce distinct fingerprints
    fp3 = generate_fingerprint("Normal benign conversation tomorrow", sender_id="alerts@bank.com", source_platform="web")
    assert fp1 != fp3

# =====================================================================
# 7. Input Validation and Malformed Payloads
# =====================================================================
def test_input_validation_missing_raw_text():
    response = client.post("/api/verify-message", json={"source_platform": "web"})
    assert response.status_code == 422  # Pydantic validation error

def test_input_validation_excessive_length():
    huge_text = "A" * 50001  # Exceeds max 50,000 chars limit
    response = client.post("/api/verify-message", json={"raw_text": huge_text})
    assert response.status_code == 422

# =====================================================================
# 8. NoSQL Injection Prevention
# =====================================================================
def test_nosql_injection_rejection():
    # Attempting to supply object with MongoDB operator keys in metadata
    injection_payload = {
        "raw_text": "Verify account now",
        "metadata": {"$where": "this.password == 'secret'"}
    }
    response = client.post("/api/verify-message", json=injection_payload)
    assert response.status_code == 422
    assert "MongoDB operator injection" in response.text

def test_nosql_dot_key_rejection():
    dot_payload = {
        "raw_text": "Verify account now",
        "metadata": {"user.admin": "true"}
    }
    response = client.post("/api/verify-message", json=dot_payload)
    assert response.status_code == 422

# =====================================================================
# 9. Request Size Limits (ContentLengthLimitMiddleware)
# =====================================================================
def test_request_size_limit():
    # Client specifies Content-Length exceeding 256 KB
    oversized_headers = {
        "Content-Type": "application/json",
        "Content-Length": "300000"
    }
    response = client.post("/api/verify-message", data="{}", headers=oversized_headers)
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()

# =====================================================================
# 10. Rate Limiting (check_rate_limit)
# =====================================================================
def test_rate_limiting():
    rate_limiter.reset()
    # Fill up the rate limiter quota for client IP
    for _ in range(60):
        assert rate_limiter.is_allowed("192.168.1.100") is True

    # 61st request should be rejected
    assert rate_limiter.is_allowed("192.168.1.100") is False

    # Other IP addresses remain unaffected
    assert rate_limiter.is_allowed("192.168.1.101") is True
    rate_limiter.reset()

# =====================================================================
# 11. Authentication & Authorization for Protected Endpoints
# =====================================================================
def test_admin_authentication_when_configured(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "super-secret-admin-key-2026")

    # Request without key
    resp_no_key = client.get("/api/events")
    assert resp_no_key.status_code == 401

    # Request with invalid key
    resp_bad_key = client.get("/api/events", headers={"X-API-Key": "wrong-key"})
    assert resp_bad_key.status_code == 401

    # Request with valid key
    resp_valid = client.get("/api/events", headers={"X-API-Key": "super-secret-admin-key-2026"})
    assert resp_valid.status_code == 200

# =====================================================================
# 12. Safe Error Responses & Log Sanitization
# =====================================================================
def test_safe_error_response_no_traceback_leakage(monkeypatch):
    from app.detectors.text_detector import TextDetector

    # Simulate an unexpected internal explosion inside TextDetector
    def broken_analyze(text):
        raise RuntimeError("SensitiveDatabaseException: secret_conn_str_leaked@mongodb.internal:27017")

    monkeypatch.setattr(TextDetector, "analyze", broken_analyze)

    response = client.post("/api/verify-message", json={"raw_text": "Test message"})
    assert response.status_code == 500
    detail = response.json().get("detail", "")
    assert "secret_conn_str_leaked" not in detail
    assert "RuntimeError" not in detail
    assert detail == "Analysis failed due to an internal processing error."

def test_log_sanitizer():
    long_msg = "A" * 150
    sanitized = sanitize_for_log(long_msg, max_chars=50)
    assert len(sanitized) < 100
    assert "[TRUNCATED]" in sanitized

# =====================================================================
# 13. Preservation of Verdicts and Explanation Breakdown
# =====================================================================
def test_preservation_of_verdicts_and_explanation():
    payload = {
        "raw_text": "URGENT: Your account has been suspended! Verify immediately at https://secure-bank-login.fake.org",
        "sender_id": "Security Team <security@fake-bank.org>"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert data["risk_score"] >= 60

    # Ensure explanation breakdown is fully intact
    expl = data.get("explanation")
    assert expl is not None
    assert "summary" in expl
    assert "signals" in expl
    assert "categories" in expl
    assert "recommended_action" in expl

    # Check evidence states
    for sig in expl["signals"]:
        assert sig["status"] in ["detected", "not_detected", "unavailable"]

# =====================================================================
# 14. Duplicate Cleanup Dry-Run and Apply Behavior
# =====================================================================
def test_duplicate_cleanup_dry_run_and_apply():
    if not is_connected() or _client is None:
        pytest.skip("MongoDB not connected for cleanup test")

    test_db = _client[MONGODB_DATABASE]
    coll = test_db["test_cleanup_sandbox"]
    coll.drop()  # Clean slate

    # Insert 3 duplicates with identical fingerprint
    fp = generate_fingerprint("Cleanup test email message", "sender@test.com", "web")
    doc1 = {"_id": uuid.uuid4().hex, "fingerprint": fp, "raw_text": "Cleanup test email message", "created_at": "2026-10-22T10:00:00Z", "duplicate_count": 1}
    doc2 = {"_id": uuid.uuid4().hex, "fingerprint": fp, "raw_text": "Cleanup test email message", "created_at": "2026-10-22T10:05:00Z", "duplicate_count": 1}
    doc3 = {"_id": uuid.uuid4().hex, "fingerprint": fp, "raw_text": "Cleanup test email message", "created_at": "2026-10-22T10:10:00Z", "duplicate_count": 1}
    # And 1 unique doc
    fp_unique = generate_fingerprint("Completely distinct message", "sender@test.com", "web")
    doc4 = {"_id": uuid.uuid4().hex, "fingerprint": fp_unique, "raw_text": "Completely distinct message", "created_at": "2026-10-22T10:12:00Z", "duplicate_count": 1}

    coll.insert_many([doc1, doc2, doc3, doc4])
    assert coll.count_documents({}) == 4

    # 1. Dry run: should detect duplicates but delete 0
    dry_report = clean_duplicates(coll, dry_run=True)
    assert dry_report["status"] == "success"
    assert dry_report["dry_run"] is True
    assert dry_report["total_records"] == 4
    assert dry_report["duplicate_groups"] == 1
    assert dry_report["redundant_records_identified"] == 2
    assert dry_report["redundant_records_removed"] == 0
    assert coll.count_documents({}) == 4  # Untouched

    # 2. Apply: should delete 2 redundant records and keep 1 canonical + 1 unique = 2 docs
    apply_report = clean_duplicates(coll, dry_run=False)
    assert apply_report["status"] == "success"
    assert apply_report["dry_run"] is False
    assert apply_report["redundant_records_removed"] == 2
    assert coll.count_documents({}) == 2

    # Verify canonical doc was preserved and duplicate_count merged
    remaining_canonical = coll.find_one({"fingerprint": fp})
    assert remaining_canonical is not None
    assert remaining_canonical["duplicate_count"] == 3

    # Cleanup sandbox collection
    coll.drop()
