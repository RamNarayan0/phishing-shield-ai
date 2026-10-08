from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/")
def root():
    return {"message": "Phishing Shield AI Backend is running", "docs": "/docs", "status": "ONLINE"}

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", version="1.0.0")

@router.get("/api/system-status")
def system_status():
    from ...db.mongodb import is_connected, MONGODB_DB_NAME
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
            "database": "connected (MongoDB: " + MONGODB_DB_NAME + ")" if db_connected else "fallback (in-memory)"
        }
    }
