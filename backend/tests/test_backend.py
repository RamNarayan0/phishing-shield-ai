from fastapi.testclient import TestClient
from app.main import app
from app.extraction.url_extractor import URLExtractor

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_url_extraction():
    text = "Visit https://example.com and http://test.org/login"
    urls = URLExtractor.extract_urls(text)
    assert len(urls) == 2
    assert "https://example.com" in urls
    assert "http://test.org/login" in urls

def test_safe_message():
    payload = {
        "raw_text": "Hey bro are you coming tomorrow?",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SAFE"

def test_suspicious_message():
    payload = {
        "raw_text": "Your account requires verification. Please verify your information immediately.",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SUSPICIOUS" or data["verdict"] == "HIGH RISK"

def test_phishing_message():
    payload = {
        "raw_text": "URGENT: Your bank account has been suspended. Verify immediately at: https://example-bank-login.com",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert len(data["reasons"]) > 0

def test_kyc_scam():
    payload = {
        "raw_text": "KYC VERIFICATION PENDING: Your crypto wallet will be frozen. Verify KYC now: https://binance-kyc-verify.io",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    
def test_delivery_scam():
    payload = {
        "raw_text": "FedEx: Your package delivery failed. Pay the $2.99 fee to reschedule: https://fedex-redelivery.net",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["SUSPICIOUS", "HIGH RISK", "CRITICAL"]

def test_lottery_scam():
    payload = {
        "raw_text": "Congratulations! You've won $1,000,000! Claim your prize here: https://lottery-winner-claim.net",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL", "SUSPICIOUS"]

def test_empty_input():
    payload = {
        "raw_text": "",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SAFE"

def test_malformed_url():
    # URL extractor shouldn't crash on this
    text = "Check this out: http://"
    urls = URLExtractor.extract_urls(text)
    assert len(urls) == 0

def test_phone_extraction_and_smishing():
    from app.extraction.phone_extractor import PhoneExtractor
    text = "Power supply will be disconnected tonight. Call officer immediately: +919876543210"
    phones = PhoneExtractor.extract_phones(text)
    assert len(phones) >= 1
    assert "+919876543210" in phones[0] or "9876543210" in phones[0]

    payload = {
        "raw_text": text,
        "sender_id": "+919876543210"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert any("Institutional impersonation" in r for r in data["reasons"])

def test_high_risk_country_phone_lottery():
    payload = {
        "raw_text": "Congratulations! You won 25 Lakhs in WhatsApp Lottery. Contact +923001234567",
        "sender_id": "+923001234567"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert any("+92" in r for r in data["reasons"])

def test_uk_premium_toll_shortcode():
    payload = {
        "raw_text": "WINNER!! Claim £900 cash reward. Call 09061701461 now or text WIN to 87121",
        "sender_id": "CLAIM-PRIZE"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert any("Premium Rate" in r for r in data["reasons"])

def test_email_brand_webmail_impersonation():
    payload = {
        "raw_text": "Your PayPal transaction was declined. Confirm identity immediately.",
        "sender_id": "paypal.support@gmail.com"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert any("brand impersonation" in r.lower() for r in data["reasons"])

def test_email_display_name_spoofing():
    payload = {
        "raw_text": "URGENT: Your SBI net banking account is blocked. Mandatory update.",
        "sender_id": "State Bank of India <alerts@sbi-kyc-update.top>"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["HIGH RISK", "CRITICAL"]
    assert any("spoofing" in r.lower() for r in data["reasons"])

def test_explainable_breakdown_structure_and_safe_message():
    payload = {
        "raw_text": "Hey bro, let's catch up tomorrow for lunch at the usual spot.",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    expl = data["explanation"]
    assert expl is not None
    assert "summary" in expl
    assert "signals" in expl
    assert "categories" in expl
    assert "recommended_action" in expl

    # Check categories
    cats = expl["categories"]
    assert "message_content" in cats
    assert "url_structure" in cats
    assert "ml_evidence" in cats
    assert "sender_identity" in cats

    # In safe text without URL, url_structure is unavailable and message_content is clean
    assert cats["url_structure"]["status"] == "unavailable"
    assert cats["message_content"]["status"] == "clean"

    # Signals structure
    for sig in expl["signals"]:
        assert "signal_id" in sig
        assert "category" in sig
        assert "label" in sig
        assert "status" in sig
        assert sig["status"] in ["detected", "not_detected", "unavailable"]
        assert "severity" in sig
        assert "description" in sig
        assert "contribution" in sig

def test_explainable_breakdown_phishing_with_url():
    payload = {
        "raw_text": "URGENT: Your bank account has been suspended. Verify immediately at: https://example-bank-login.com",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    expl = data.get("explanation")
    assert expl is not None
    cats = expl["categories"]

    # Should detect urgency and url structure
    assert cats["message_content"]["status"] == "detected"
    assert cats["url_structure"]["status"] == "detected"
    assert cats["message_content"]["detected_count"] >= 1
    assert cats["url_structure"]["detected_count"] >= 1

    # Check that at least one signal in url_structure has status 'detected'
    url_signals = [s for s in expl["signals"] if s["category"] == "url_structure" and s["status"] == "detected"]
    assert len(url_signals) > 0
    assert "CRITICAL" in expl["summary"] or "HIGH RISK" in expl["summary"]

def test_explainable_breakdown_sender_unavailable_when_missing():
    payload = {
        "raw_text": "Test message without sender header.",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    expl = data.get("explanation")
    assert expl is not None
    sender_sig = next((s for s in expl["signals"] if s["signal_id"] == "sender_impersonation"), None)
    assert sender_sig is not None
    assert sender_sig["status"] == "unavailable"

def test_explainable_breakdown_empty_input():
    payload = {
        "raw_text": "",
        "source_platform": "web"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SAFE"
    expl = data.get("explanation")
    assert expl is not None
    assert "SAFE" in expl["summary"]
    assert expl["categories"]["url_structure"]["status"] == "unavailable"

def test_explainable_breakdown_ml_inactive():
    from app.core.risk_engine import RiskEngine
    text_analysis = {"risk_score": 0, "signals": []}
    sender_analysis = {"sender": "", "risk_score": 0, "signals": []}
    result = RiskEngine.calculate_verdict(
        text_analysis=text_analysis,
        url_analyses=[],
        sender_analysis=sender_analysis,
        ml_analysis={"active": False, "ml_score": 0}
    )
    assert "explanation" in result
    ml_sig = next((s for s in result["explanation"]["signals"] if s["signal_id"] == "ml_text_classifier"), None)
    assert ml_sig is not None
    assert ml_sig["status"] == "unavailable"
    assert result["explanation"]["categories"]["ml_evidence"]["status"] == "unavailable"

def test_explainable_breakdown_score_consistency():
    payload = {
        "raw_text": "URGENT: Your PayPal account is frozen. Pay fee immediately: https://paypa1-security.com",
        "sender_id": "service@paypa1-security.com"
    }
    response = client.post("/api/verify-message", json=payload)
    assert response.status_code == 200
    data = response.json()
    expl = data["explanation"]
    assert str(data["risk_score"]) in expl["summary"]
    assert data["verdict"] in expl["summary"]
