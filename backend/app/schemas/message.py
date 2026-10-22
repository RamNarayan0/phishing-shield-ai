from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class MessagePayload(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_platform: str = Field(default="web", description="web, android, chrome")
    sender_id: Optional[str] = None
    raw_text: str
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    urls: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
