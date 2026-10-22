import re
from typing import Dict, Any
from app.extraction.email_extractor import EmailExtractor
from app.extraction.phone_extractor import PhoneExtractor
from app.detectors.email_detector import EmailDetector
from app.detectors.phone_detector import PhoneDetector

class SenderDetector:
    IMPERSONATION_KEYWORDS = [
        "support", "admin", "billing", "security", "customer service",
        "helpdesk", "fraud department", "it department", "account team",
        "electricity board", "sbi", "hdfc", "paypal", "apple", "amazon"
    ]

    @classmethod
    def analyze(cls, sender: str, context_text: str = "") -> Dict[str, Any]:
        if not sender or sender.strip() in ("", "Unknown", "unknown", "None"):
            return {
                "sender": sender or "",
                "risk_score": 0,
                "signals": [],
                "sender_type": "unknown"
            }

        sender_str = sender.strip()
        signals = []
        max_score = 0
        sender_type = "name"

        # -------------------------------------------------------------
        # 1. Parse for Email Address in Sender
        # -------------------------------------------------------------
        parsed_header = EmailExtractor.parse_sender_header(sender_str)
        if parsed_header["email"]:
            sender_type = "email"
            email_res = EmailDetector.analyze(
                parsed_header["email"],
                display_name=parsed_header["display_name"]
            )
            max_score = max(max_score, email_res["risk_score"])
            signals.extend(email_res["signals"])

        # -------------------------------------------------------------
        # 2. Check for Phone Number in Sender (WhatsApp / SMS)
        # -------------------------------------------------------------
        # If not an email, check if it matches a phone number
        elif re.search(r'^\+?[0-9\s\-\(\)\.]{7,18}$', sender_str):
            sender_type = "phone"
            phone_res = PhoneDetector.analyze(sender_str, context_text=context_text)
            max_score = max(max_score, phone_res["risk_score"])
            signals.extend(phone_res["signals"])

        # -------------------------------------------------------------
        # 3. Text Name Impersonation (Sender is a Display Name only)
        # -------------------------------------------------------------
        else:
            lower_name = sender_str.lower()
            matched = [k for k in cls.IMPERSONATION_KEYWORDS if k in lower_name]
            if matched:
                signals.append(f"Sender name claims to be official '{matched[0]}' but lacks verified digital signatures/headers")
                max_score = max(max_score, 40)

        # Deduplicate signals
        signals = list(dict.fromkeys(signals))
        return {
            "sender": sender_str,
            "risk_score": min(100, max_score),
            "signals": signals,
            "sender_type": sender_type
        }
