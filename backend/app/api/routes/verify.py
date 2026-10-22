from fastapi import APIRouter, HTTPException
from ...schemas.message import MessagePayload
from ...schemas.verdict import FinalVerdict
from ...extraction.url_extractor import URLExtractor
from ...extraction.phone_extractor import PhoneExtractor
from ...extraction.email_extractor import EmailExtractor
from ...detectors.text_detector import TextDetector
from ...detectors.url_detector import URLDetector
from ...detectors.sender_detector import SenderDetector
from ...detectors.phone_detector import PhoneDetector
from ...detectors.email_detector import EmailDetector
from ...core.risk_engine import RiskEngine

router = APIRouter()

@router.post("/verify-message", response_model=FinalVerdict)
def verify_message(payload: MessagePayload):
    try:
        # 1. Extract and analyze URLs
        extracted_urls = URLExtractor.extract_urls(payload.raw_text)
        if payload.urls:
            extracted_urls.extend(payload.urls)
        unique_urls = list(dict.fromkeys(extracted_urls))
        
        url_analyses = []
        for url in unique_urls:
            url_analyses.append(URLDetector.analyze(url))
            
        # 2. Extract and analyze Phone Numbers (callback traps, smishing, toll fraud)
        extracted_phones = PhoneExtractor.extract_phones(payload.raw_text)
        # If sender_id is a phone number, include it
        if payload.sender_id and any(c.isdigit() for c in payload.sender_id) and "@" not in payload.sender_id:
            extracted_phones.append(payload.sender_id.strip())
        unique_phones = list(dict.fromkeys(extracted_phones))
        
        phone_analyses = []
        for phone in unique_phones:
            phone_analyses.append(PhoneDetector.analyze(phone, context_text=payload.raw_text))
            
        # 3. Extract and analyze Email Addresses (brand spoofing, disposable burners)
        extracted_emails = EmailExtractor.extract_emails(payload.raw_text)
        if payload.sender_id and "@" in payload.sender_id:
            parsed = EmailExtractor.parse_sender_header(payload.sender_id)
            if parsed["email"]:
                extracted_emails.append(parsed["email"])
        unique_emails = list(dict.fromkeys(extracted_emails))
        
        email_analyses = []
        for email in unique_emails:
            email_analyses.append(EmailDetector.analyze(email))

        # 4. Analyze Text Heuristics
        text_analysis = TextDetector.analyze(payload.raw_text)
        
        # 5. Analyze Sender Metadata
        sender_analysis = SenderDetector.analyze(payload.sender_id or "", context_text=payload.raw_text)
        
        # 6. ML Prediction
        from ...core.ml_engine import MLEngine
        ml_analysis = MLEngine.predict(payload.raw_text)
        
        # 7. Calculate Comprehensive Risk Verdict
        verdict = RiskEngine.calculate_verdict(
            text_analysis=text_analysis,
            url_analyses=url_analyses,
            sender_analysis=sender_analysis,
            ml_analysis=ml_analysis,
            phone_analyses=phone_analyses,
            email_analyses=email_analyses
        )
        
        # 8. Save alert to MongoDB and live dashboard store
        import uuid
        import datetime
        from ...db.mongodb import save_alert
        event_record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p"),
            "source_platform": payload.source_platform,
            "application_name": "Chrome Extension" if "Chrome" in payload.source_platform else "Android App",
            "sender_id": payload.sender_id or "Unknown",
            "raw_text": payload.raw_text,
            "result": verdict
        }
        save_alert(event_record)

        return verdict
        
    except Exception as e:
        print(f"Error in verify-message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/events")
def get_events():
    from ...db.mongodb import get_recent_alerts
    return {"events": get_recent_alerts(50)}

@router.post("/verify-url", response_model=FinalVerdict)
def verify_url(url: str):
    try:
        url_a = URLDetector.analyze(url)
        verdict = RiskEngine.calculate_verdict(
            text_analysis={"risk_score": 0, "signals": []},
            url_analyses=[url_a],
            sender_analysis={"risk_score": 0, "signals": []}
        )
        return verdict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
