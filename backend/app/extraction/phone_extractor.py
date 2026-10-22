import re
from typing import List

class PhoneExtractor:
    # International format with plus, e.g. +91 9876543210, +234 802 123 4567, +44 7911 123456
    INTL_PATTERN = re.compile(r'\+(?:[0-9][\s\-\.]?){7,15}[0-9]')
    
    # Standard 10-digit Indian mobile numbers (starts with 6, 7, 8, or 9)
    # Match with optional +91, 91, or 0 prefix
    INDIAN_MOBILE_PATTERN = re.compile(r'(?:(?:\+91|91|0)[\s\-\.]?)?([6-9]\d{4}[\s\-\.]?\d{5})\b')
    
    # UK Premium rate and non-geographic numbers (090x, 087x, 070x)
    UK_PREMIUM_PATTERN = re.compile(r'\b(?:09[0-9]{2}|087[0-9]|070[0-9])[\s\-\.]?[0-9]{3}[\s\-\.]?[0-9]{3,4}\b')
    
    # US/North American Toll-Free & 900 numbers (1-800, 1-888, 1-900)
    US_TOLL_PATTERN = re.compile(r'(?:\+?1[\s\-\.]?)?\(?(800|888|877|866|855|844|833|900)\)?[\s\-\.]?[0-9]{3}[\s\-\.]?[0-9]{4}\b')
    
    # SMS Premium Shortcodes (5-6 digits, often preceded by text/txt/send)
    SHORTCODE_PATTERN = re.compile(r'(?:text|txt|send|to|code)\s+([0-9]{5,6})\b', re.IGNORECASE)

    @classmethod
    def extract_phones(cls, text: str) -> List[str]:
        if not text:
            return []
            
        found = set()
        
        # 1. International patterns
        for match in cls.INTL_PATTERN.finditer(text):
            p = cls._clean_number(match.group(0))
            if len(p) >= 8:
                found.add(p)
                
        # 2. Indian Mobile patterns
        for match in cls.INDIAN_MOBILE_PATTERN.finditer(text):
            raw = match.group(0)
            cleaned = cls._clean_number(raw)
            # Only add if it's a valid 10-digit mobile length
            digits_only = re.sub(r'\D', '', cleaned)
            if digits_only.startswith('91') and len(digits_only) == 12:
                found.add('+' + digits_only)
            elif len(digits_only) == 10 and digits_only[0] in '6789':
                found.add('+91' + digits_only)
                
        # 3. UK Premium / Toll patterns
        for match in cls.UK_PREMIUM_PATTERN.finditer(text):
            p = cls._clean_number(match.group(0))
            found.add(p)
            
        # 4. US 900 / Toll Free patterns
        for match in cls.US_TOLL_PATTERN.finditer(text):
            p = cls._clean_number(match.group(0))
            found.add(p)
            
        # 5. Shortcodes
        for match in cls.SHORTCODE_PATTERN.finditer(text):
            code = match.group(1).strip()
            found.add(f"Shortcode:{code}")
            
        return sorted(list(found))
        
    @staticmethod
    def _clean_number(s: str) -> str:
        # Standardize spaces and hyphens
        cleaned = re.sub(r'[\(\)\.\s\-]+', '', s)
        if s.startswith('+') and not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return cleaned
