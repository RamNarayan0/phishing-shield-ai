import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class MessagePayload(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), max_length=128)
    source_platform: str = Field(default="web", max_length=100, description="web, chrome, api")
    sender_id: Optional[str] = Field(default=None, max_length=500, description="Sender address or phone number")
    raw_text: str = Field(..., max_length=50000, description="Raw message text to analyze (max 50,000 characters)")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    urls: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text_type(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("raw_text must be a valid string")
        return v

    @field_validator("metadata")
    @classmethod
    def prevent_nosql_injection(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not v:
            return v
        for key in v.keys():
            if not isinstance(key, str) or key.startswith("$") or "." in key:
                raise ValueError(f"Invalid metadata key '{key}': MongoDB operator injection disallowed.")
        return v
