from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class URLVerdict(BaseModel):
    url: str
    risk: int

class EvidenceSignal(BaseModel):
    signal_id: str
    category: str  # message_content, url_structure, ml_evidence, sender_identity, contact_pattern
    label: str
    status: str    # detected, not_detected, unavailable
    severity: str  # critical, high, medium, low, info
    description: str
    contribution: int = 0

class CategorySummary(BaseModel):
    category: str
    title: str
    detected_count: int
    evaluated_count: int
    status: str    # detected, clean, unavailable

class RiskExplanation(BaseModel):
    summary: str
    signals: List[EvidenceSignal]
    categories: Dict[str, CategorySummary]
    recommended_action: str

class FinalVerdict(BaseModel):
    verdict: str
    risk_score: int
    ml_score: float = 0.0
    heuristic_score: int = 0
    url_score: int = 0
    sender_score: int = 0
    confidence: float
    reasons: List[str]
    extracted_urls: List[str] = []
    extracted_phones: List[str] = []
    extracted_emails: List[str] = []
    recommended_action: str
    explanation: Optional[RiskExplanation] = None
