import re
from urllib.parse import urlparse

class URLDetector:
    TYPOSQUATTING_PATTERNS = [
        r'0', r'1', r'--', r'paypa1', r'micros0ft', r'faceb00k'
    ]

    @classmethod
    def analyze(cls, url: str) -> dict:
        if not url:
            return {"url": "", "risk_score": 0, "signals": []}
            
        score = 0
        signals = []
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # HTTPS check
        if parsed.scheme == "http":
            signals.append("Insecure connection (HTTP)")
            score += 20
            
        # Subdomains check
        if domain.count('.') > 3:
            signals.append("Excessive subdomains")
            score += 20
            
        # IP address check
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if ip_pattern.match(domain):
            signals.append("IP address instead of domain")
            score += 40
            
        # Suspicious length check
        if len(url) > 100:
            signals.append("Suspiciously long URL")
            score += 10
            
        # Typosquatting/Suspicious characters
        for pattern in cls.TYPOSQUATTING_PATTERNS:
            if pattern in domain:
                signals.append(f"Suspicious character pattern in domain")
                score += 30
                break
                
        # Path and Domain analysis for credential words
        path_lower = parsed.path.lower()
        credential_words = ["login", "verify", "signin", "secure", "account", "update"]
        
        if any(word in path_lower for word in credential_words):
            signals.append("Credential-oriented URL path")
            score += 20
            
        if any(word in domain for word in credential_words):
            signals.append("Credential-oriented URL domain")
            score += 30
            
        return {
            "url": url,
            "risk_score": min(100, score),
            "signals": signals
        }
