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
