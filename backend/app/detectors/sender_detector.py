import re

class SenderDetector:
    # High-value targets often spoofed
    PROTECTED_BRANDS = ["paypal", "apple", "amazon", "google", "microsoft", "netflix", "facebook", "bank", "whatsapp"]
    
    # Common spam/scam country codes (Example subset for prototype)
    HIGH_RISK_COUNTRY_CODES = ["+234", "+44", "+92", "+371"]

    @classmethod
    def analyze(cls, sender: str) -> dict:
        if not sender or sender == "Unknown":
            return {"risk_score": 0, "signals": []}
            
        score = 0
        signals = []
        lower_sender = sender.lower().strip()
        
        # -----------------------------------------------------
        # 1. EMAIL ANALYSIS (Spoofing & DMARC/SPF Heuristics)
        # -----------------------------------------------------
        if "@" in lower_sender:
            local_part, domain = lower_sender.split("@", 1)
            
            # Check for Free Providers
            free_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
            if domain in free_providers:
                # If a free provider is using a protected brand name in the local part (e.g. paypal.support@gmail.com)
                if any(brand in local_part for brand in cls.PROTECTED_BRANDS):
                    signals.append("CRITICAL: Official brand impersonation using a free email provider!")
                    score += 80
                else:
                    signals.append("Uses a free public email provider")
                    score += 10
            else:
                # Check for Typosquatting / Lookalike domains (e.g. amaz0n.com, paypaI.com)
                for brand in cls.PROTECTED_BRANDS:
                    if brand in domain and domain != f"{brand}.com" and domain != f"{brand}.net" and domain != f"{brand}.org":
                        signals.append(f"CRITICAL: Lookalike / Typosquatting domain spoofing '{brand}'")
                        score += 85
                
            # Random string domain check (e.g. support@xkjhfksdjhf.com)
            if re.match(r'^[a-z0-9]{12,}\.[a-z]{2,}$', domain):
                signals.append("Suspicious randomly-generated email domain")
                score += 30
                
        # -----------------------------------------------------
        # 2. PHONE NUMBER ANALYSIS (WhatsApp / SMS)
        # -----------------------------------------------------
        elif re.match(r'^\+?\d[\d\s\-]{7,15}$', sender):
            cleaned_num = re.sub(r'[\s\-]', '', sender)
            
            # Check High-Risk Country Codes
            if any(cleaned_num.startswith(code) for code in cls.HIGH_RISK_COUNTRY_CODES):
                signals.append("Originates from a high-risk international country code")
                score += 40
                
            # Verify if it claims to be a business but uses a standard unverified number
            if len(cleaned_num) > 13:
                signals.append("Suspicious unusual phone number length")
                score += 15
                
        # -----------------------------------------------------
        # 3. GENERIC NAME IMPERSONATION
        # -----------------------------------------------------
        else:
            impersonation_keywords = ["support", "admin", "billing", "security", "customer service"]
            if any(keyword in lower_sender for keyword in impersonation_keywords):
                signals.append("Sender name claims to be official Support/Admin but is unverified")
                score += 35

        return {
            "risk_score": min(100, score),
            "signals": signals
        }
