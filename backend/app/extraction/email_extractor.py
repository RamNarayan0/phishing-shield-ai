import re
from typing import List, Dict

class EmailExtractor:
    # Standard email regex pattern
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    )
    
    # Display name + email header format, e.g.: "PayPal Support" <support@fake-domain.com>
    HEADER_PATTERN = re.compile(
        r'(?:["\']?([^"\'<>]+)["\']?\s+)?<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>'
    )

    @classmethod
    def extract_emails(cls, text: str) -> List[str]:
        if not text:
            return []
        found = set()
        for match in cls.EMAIL_PATTERN.finditer(text):
            found.add(match.group(0).lower().strip())
        return sorted(list(found))

    @classmethod
    def parse_sender_header(cls, sender_str: str) -> Dict[str, str]:
        if not sender_str:
            return {"display_name": "", "email": ""}
            
        header_match = cls.HEADER_PATTERN.search(sender_str)
        if header_match:
            display_name = (header_match.group(1) or "").strip()
            email = header_match.group(2).lower().strip()
            return {"display_name": display_name, "email": email}
            
        # Standalone email
        standalone = cls.EMAIL_PATTERN.search(sender_str)
        if standalone:
            return {"display_name": "", "email": standalone.group(0).lower().strip()}
            
        # Raw name / identifier
        return {"display_name": sender_str.strip(), "email": ""}
