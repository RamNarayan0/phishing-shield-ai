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

