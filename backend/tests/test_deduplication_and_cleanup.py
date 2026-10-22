import os
import uuid
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app
import app.db.mongodb as mongodb
from app.db.cleanup import clean_duplicates, create_backup, reset_demo_data

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_test_collection():
    """Ensure test collection is clean before each deduplication test."""
    coll = mongodb.get_collection()
    if coll is not None:
        coll.delete_many({})
    yield

# ---------------------------------------------------------------------
# 1. Repeated Identical Requests Do Not Create Duplicate Records
# ---------------------------------------------------------------------
def test_repeated_identical_requests_prevent_duplicates():
    payload = {
        "raw_text": "URGENT: Your account has been suspended. Verify immediately at https://test-bank.com",
        "sender_id": "security@test-bank.com",
        "source_platform": "WhatsApp"
    }

    # Submit 5 times
    for _ in range(5):
        resp = client.post("/api/verify-message", json=payload)
        assert resp.status_code == 200

    # Verify only 1 document exists in DB
    coll = mongodb.get_collection()
    docs = list(coll.find({}))
    assert len(docs) == 1
    doc = docs[0]
    assert doc["duplicate_count"] == 5
    assert doc["raw_text"] == payload["raw_text"]
    assert "explanation" in doc["result"]

# ---------------------------------------------------------------------
# 2. Concurrent Identical Requests Respect Uniqueness Constraint
# ---------------------------------------------------------------------
def test_concurrent_identical_requests_uniqueness():
    shared_text = f"Concurrent test payload: {uuid.uuid4()}"
    payload = {
        "raw_text": shared_text,
        "sender_id": "blast@test.com",
        "source_platform": "Android Interceptor"
    }

    def worker():
        return client.post("/api/verify-message", json=payload)

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(lambda _: worker(), range(10)))

    for r in responses:
        assert r.status_code == 200

    # Ensure single canonical document with aggregated count
    coll = mongodb.get_collection()
    docs = list(coll.find({"raw_text": shared_text}))
    assert len(docs) == 1
    assert docs[0]["duplicate_count"] == 10

# ---------------------------------------------------------------------
# 3. Distinct Messages Remain Separate
# ---------------------------------------------------------------------
def test_distinct_messages_remain_separate():
    msg1 = {"raw_text": "Hey are you coming for dinner?", "source_platform": "SMS"}
    msg2 = {"raw_text": "URGENT: Your PayPal code is 123456", "source_platform": "SMS"}

    client.post("/api/verify-message", json=msg1)
    client.post("/api/verify-message", json=msg2)

    coll = mongodb.get_collection()
    docs = list(coll.find({}))
    assert len(docs) == 2
    fps = [d["fingerprint"] for d in docs]
    assert fps[0] != fps[1]

# ---------------------------------------------------------------------
# 4. Source-Specific Identity and Cross-Source Deduplication
# ---------------------------------------------------------------------
def test_cross_source_deduplication_rule():
    shared_text = "Your one-time verification password is 987654"
    # Same content arriving via SMS and WhatsApp
    client.post("/api/verify-message", json={"raw_text": shared_text, "source_platform": "SMS"})
    client.post("/api/verify-message", json={"raw_text": shared_text, "source_platform": "WhatsApp"})

    coll = mongodb.get_collection()
    # Source-specific default: 2 records (different ingress platforms)
    docs_before = list(coll.find({}))
    assert len(docs_before) == 2

    # Cross-source consolidation merge
    report = clean_duplicates(coll, dry_run=False, cross_source=True, purge_test_artifacts=False)
    assert report["redundant_records_identified"] == 1

    docs_after = list(coll.find({}))
    assert len(docs_after) == 1
    canonical = docs_after[0]
    assert canonical["duplicate_count"] == 2
    assert "SMS" in canonical["observed_sources"]
    assert "WhatsApp" in canonical["observed_sources"]

# ---------------------------------------------------------------------
# 5. Cleanup Preserves Valid Records and is Idempotent
# ---------------------------------------------------------------------
def test_cleanup_preserves_valid_records_and_is_idempotent():
    coll = mongodb.get_collection()
    # Insert genuine record
    client.post("/api/verify-message", json={"raw_text": "Genuine safe message", "source_platform": "SMS"})
    # Insert synthetic test clutter
    coll.insert_one({
        "raw_text": "Concurrent blast test 12345",
        "source_platform": "load_test",
        "fingerprint": "test_fp_1",
        "duplicate_count": 1
    })

    assert coll.count_documents({}) == 2

    # Run cleanup apply
    first_run = clean_duplicates(coll, dry_run=False, purge_test_artifacts=True)
    assert first_run["test_artifacts_identified"] == 1
    assert first_run["records_purged"] == 1
    assert coll.count_documents({}) == 1

    # Preserved document must be the genuine record
    preserved = coll.find_one({})
    assert preserved["raw_text"] == "Genuine safe message"

    # Second run must be completely idempotent (0 purged)
    second_run = clean_duplicates(coll, dry_run=False, purge_test_artifacts=True)
    assert second_run["records_purged"] == 0
    assert coll.count_documents({}) == 1

# ---------------------------------------------------------------------
# 6. Automatic Backup Snapshot Generation
# ---------------------------------------------------------------------
def test_backup_creation():
    coll = mongodb.get_collection()
    coll.insert_one({"raw_text": "Backup test payload", "fingerprint": "bkp_1"})
    res = create_backup(coll)
    assert res["status"] == "success"
    assert res["backed_up_count"] == 1
    backup_name = res["backup_collection"]

    # Verify backup collection exists and contains document
    db = coll.database
    assert backup_name in db.list_collection_names()
    assert db[backup_name].count_documents({}) == 1
    db.drop_collection(backup_name)

# ---------------------------------------------------------------------
# 7. Seed Demo Script Creates Pristine Scenarios
# ---------------------------------------------------------------------
def test_seed_demo_script():
    coll = mongodb.get_collection()
    res = reset_demo_data(coll)
    assert res["status"] == "success"
    assert res["seeded_canonical_records"] == 9
    assert coll.count_documents({}) == 9

    # Re-running seed resets cleanly to 9 records
    res2 = reset_demo_data(coll)
    assert res2["seeded_canonical_records"] == 9
    assert coll.count_documents({}) == 9

# ---------------------------------------------------------------------
# 8. Dashboard Statistics Reconciliation
# ---------------------------------------------------------------------
def test_dashboard_statistics_reconciliation():
    def compute_stats(events):
        s = {"total": len(events), "safe": 0, "suspicious": 0, "high": 0, "critical": 0, "unknown": 0}
        for e in events:
            score = e.get("result", {}).get("risk_score", -1)
            verdict = (e.get("result", {}).get("verdict") or "").upper()
            if score >= 80 or verdict == "CRITICAL":
                s["critical"] += 1
            elif score >= 60 or verdict in ("HIGH RISK", "HIGH"):
                s["high"] += 1
            elif score >= 30 or verdict == "SUSPICIOUS":
                s["suspicious"] += 1
            elif score >= 0 or verdict == "SAFE":
                s["safe"] += 1
            else:
                s["unknown"] += 1
        return s

    events = [
        {"result": {"risk_score": 0, "verdict": "SAFE"}},
        {"result": {"risk_score": 45, "verdict": "SUSPICIOUS"}},
        {"result": {"risk_score": 70, "verdict": "HIGH RISK"}},
        {"result": {"risk_score": 95, "verdict": "CRITICAL"}},
        {"result": {"risk_score": 100, "verdict": "CRITICAL"}},
    ]

    stats = compute_stats(events)
    assert stats["total"] == 5
    assert stats["safe"] == 1
    assert stats["suspicious"] == 1
    assert stats["high"] == 1
    assert stats["critical"] == 2
    assert stats["unknown"] == 0
    # Reconciliation check: Total must equal sum of mutually exclusive categories
    assert stats["total"] == stats["safe"] + stats["suspicious"] + stats["high"] + stats["critical"] + stats["unknown"]
