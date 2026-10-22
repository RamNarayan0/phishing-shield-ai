import uuid
import datetime
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
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
from ...core.security import check_rate_limit, verify_admin_access, sanitize_for_log
from ...db.mongodb import save_alert, get_recent_alerts
from ...db.cleanup import clean_duplicates

logger = logging.getLogger("phishing_shield.api")
router = APIRouter()

@router.post("/verify-message", response_model=FinalVerdict, dependencies=[Depends(check_rate_limit)])
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

        # 8. Save alert to MongoDB and live dashboard store with atomic deduplication
        event_record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p"),
            "source_platform": payload.source_platform,
            "application_name": "Chrome Extension" if "Chrome" in payload.source_platform else "Android App",
            "sender_id": payload.sender_id or "Unknown",
            "raw_text": payload.raw_text,
            "result": verdict
        }

        try:
            save_alert(event_record)
        except Exception as db_err:
            logger.error(f"Failed to persist alert to database: {db_err}")
            # Non-blocking: analysis verdict is preserved even if database write fails

        return verdict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during message analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal processing error.")

@router.get("/events", dependencies=[Depends(verify_admin_access)])
def get_events(limit: int = Query(default=50, ge=1, le=100)):
    """Retrieves recent unique threat events, protected by API key when configured."""
    return {"events": get_recent_alerts(limit)}

@router.post("/verify-url", response_model=FinalVerdict, dependencies=[Depends(check_rate_limit)])
def verify_url(url: str = Query(..., max_length=2048, description="URL to verify")):
    """Verifies a single target URL and idempotently stores the analysis record."""
    try:
        url_a = URLDetector.analyze(url)
        verdict = RiskEngine.calculate_verdict(
            text_analysis={"risk_score": 0, "signals": []},
            url_analyses=[url_a],
            sender_analysis={"risk_score": 0, "signals": []}
        )

        event_record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p"),
            "source_platform": "URL Scan",
            "application_name": "Browser Link Scanner",
            "sender_id": "URL",
            "raw_text": f"Direct link scan: {url}",
            "result": verdict
        }
        try:
            save_alert(event_record)
        except Exception as db_err:
            logger.error(f"Failed to persist URL scan alert: {db_err}")

        return verdict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during URL analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal processing error.")

@router.post("/admin/cleanup-duplicates", dependencies=[Depends(verify_admin_access)])
def admin_cleanup_duplicates(
    dry_run: bool = Query(default=True, description="When true, audits duplicates without deleting"),
    cross_source: bool = Query(default=False, description="When true, consolidates duplicate message content across sources"),
    purge_test_artifacts: bool = Query(default=True, description="When true, purges automated test artifacts")
):
    """Admin endpoint to safely audit or purge redundant duplicate database records and test clutter."""
    report = clean_duplicates(dry_run=dry_run, cross_source=cross_source, purge_test_artifacts=purge_test_artifacts)
    return report

@router.post("/admin/backup", dependencies=[Depends(verify_admin_access)])
def admin_create_backup():
    """Admin endpoint to create an immediate point-in-time snapshot of the database collection."""
    from ...db.cleanup import create_backup
    return create_backup()

@router.post("/admin/reset-demo-data", dependencies=[Depends(verify_admin_access)])
def admin_reset_demo_data():
    """Admin endpoint to cleanly seed canonical demo scenarios, backing up first."""
    from ...db.cleanup import reset_demo_data
    return reset_demo_data()
