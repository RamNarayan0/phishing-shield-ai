from pydantic import BaseModel
from typing import List, Optional

class URLVerdict(BaseModel):
    url: str
    risk: int

class FinalVerdict(BaseModel):
    verdict: str
    risk_score: int
    ml_score: float = 0.0
    heuristic_score: int = 0
    url_score: int = 0
    confidence: float
    reasons: List[str]
    extracted_urls: List[str]
    recommended_action: str
