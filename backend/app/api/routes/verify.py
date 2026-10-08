from fastapi import APIRouter, HTTPException
from ...schemas.message import MessagePayload
from ...schemas.verdict import FinalVerdict
from ...extraction.url_extractor import URLExtractor
from ...detectors.text_detector import TextDetector
from ...detectors.url_detector import URLDetector
from ...detectors.sender_detector import SenderDetector
from ...core.risk_engine import RiskEngine

router = APIRouter()

# In-memory store for the Live Dashboard prototype
GLOBAL_EVENTS = []

@router.post("/verify-message", response_model=FinalVerdict)
def verify_message(payload: MessagePayload):
    try:
        # Extract URLs
        extracted_urls = URLExtractor.extract_urls(payload.raw_text)
        
        # Also include any URLs passed in the payload explicitly
        if payload.urls:
            extracted_urls.extend(payload.urls)
            
        # Deduplicate
        unique_urls = list(set(extracted_urls))
        
        # Analyze Text
        text_analysis = TextDetector.analyze(payload.raw_text)
        
        # Analyze URLs
        url_analyses = []
        for url in unique_urls:
            url_a = URLDetector.analyze(url)
            url_analyses.append(url_a)
            
        # Analyze Sender
        sender_analysis = SenderDetector.analyze(payload.sender_id or "")
        
        # ML Prediction
        from ...core.ml_engine import MLEngine
        ml_analysis = MLEngine.predict(payload.raw_text)
        
        # Calculate Risk
        verdict = RiskEngine.calculate_verdict(
            text_analysis=text_analysis,
            url_analyses=url_analyses,
            sender_analysis=sender_analysis,
            ml_analysis=ml_analysis
        )
        
        # Save alert to MongoDB and memory store for the dashboard
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
            "result": verdict.dict() if hasattr(verdict, "dict") else verdict
        }
        save_alert(event_record)

        return verdict
        
    except Exception as e:
        print(f"Error in verify-message: {e}")
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
