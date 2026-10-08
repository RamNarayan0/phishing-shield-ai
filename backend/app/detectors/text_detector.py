import re

class TextDetector:
    URGENCY_WORDS = [
        "urgent", "immediately", "act now", "within 24 hours", 
        "last warning", "action required", "alert", "pending", "failed"
    ]
    ACCOUNT_THREATS = [
        "account blocked", "account suspended", "account disabled", 
        "security violation", "locked", "unauthorized access",
        "frozen", "restricted", "limited"
    ]
    CREDENTIALS = [
        "password", "otp", "pin", "login", "verify", "identity", 
        "kyc", "ssn", "credentials", "claim"
    ]
    FINANCIAL = [
        "bank", "payment", "refund", "lottery", "winner", "won",
        "prize", "investment", "invoice", "transfer", "fee", "crypto", "wallet"
    ]
    SOCIAL_ENGINEERING = [
        "verify now", "click here", "confirm", "reschedule",
        "avoid account closure", "update your details", "package", "delivery"
    ]

    @classmethod
    def analyze(cls, text: str) -> dict:
        if not text:
            return {"risk_score": 0, "signals": []}
            
        lower_text = text.lower()
        signals = []
        score = 0
        
        # Urgency check
        if any(word in lower_text for word in cls.URGENCY_WORDS):
            signals.append("Urgent language")
            score += 20
            
        # Account threat check
        if any(word in lower_text for word in cls.ACCOUNT_THREATS):
            signals.append("Account suspension threat")
            score += 30
            
        # Credentials check
        if any(word in lower_text for word in cls.CREDENTIALS):
            signals.append("Credential request")
            score += 25
            
        # Financial check
        if any(word in lower_text for word in cls.FINANCIAL):
            signals.append("Financial manipulation attempt")
            score += 15
            
        # Social engineering check
        if any(word in lower_text for word in cls.SOCIAL_ENGINEERING):
            signals.append("Social engineering tactics")
            score += 20
            
        return {
            "risk_score": min(100, score),
            "signals": signals
        }
