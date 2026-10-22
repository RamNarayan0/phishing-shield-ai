from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...db.mongodb import check_health, is_connected, MONGODB_DATABASE

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    database: Optional[Dict[str, Any]] = None

@router.get("/")
def root():
    return {"message": "Phishing Shield AI Backend is running", "docs": "/docs", "status": "ONLINE"}

@router.get("/health", response_model=HealthResponse)
def health_check():
    db_health = check_health()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        database=db_health
    )

@router.get("/api/system-status")
def system_status():
    db_health = check_health()
    db_connected = is_connected()
    return {
        "status": "ONLINE",
        "version": "1.0 Cloud Ready",
        "components": {
            "backend": "ok",
            "ml_engine": "ok",
            "url_engine": "ok",
            "risk_engine": "ok",
            "event_ingestion": "ok",
            "database": f"connected (MongoDB: {MONGODB_DATABASE})" if db_connected else "fallback (in-memory)"
        },
        "database_metrics": db_health
    }
