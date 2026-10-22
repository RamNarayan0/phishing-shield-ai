import re
import math
import os
import joblib
from typing import Dict, Any, List

class EmailDetector:
    _ml_model = None
    _ml_loaded = False

    # Authoritative trusted brand domains: {brand_name: authoritative_domain}
    TRUSTED_BRAND_DOMAINS = {
        "paypal": "paypal.com",
        "apple": "apple.com",
        "amazon": "amazon.com",
        "google": "google.com",
        "microsoft": "microsoft.com",
        "netflix": "netflix.com",
        "facebook": "facebook.com",
        "sbi": "onlinesbi.sbi",
        "hdfc": "hdfcbank.com",
        "icici": "icicibank.com",
        "fedex": "fedex.com",
        "dhl": "dhl.com",
        "chase": "chase.com",
        "wellsfargo": "wellsfargo.com",
        "binance": "binance.com",
        "coinbase": "coinbase.com"
    }

    # Free webmail providers
    FREE_WEBMAIL_PROVIDERS = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com",
        "proton.me", "protonmail.com", "yandex.com", "zoho.com", "mail.ru",
        "aol.com", "icloud.com", "gmx.com", "fastmail.com", "rediffmail.com"
    }

    # Disposable / temporary burner email domains
    DISPOSABLE_EMAIL_PROVIDERS = {
        "tempmail.com", "guerrillamail.com", "10minutemail.com", "mailinator.com",
        "yopmail.com", "throwawaymail.com", "trashmail.com", "sharklasers.com",
        "dispostable.com", "burnermail.io", "getairmail.com", "fakemailgenerator.com",
        "temp-mail.org", "nada.ltd", "mohmal.com", "crazymailing.com"
    }

    # High-Risk Abuse TLDs commonly seen in phishing infrastructure
    HIGH_RISK_TLDS = {
        "xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "rest", "icu",
        "work", "click", "cam", "kim", "monster", "quest", "online", "site"
    }

    # Sensitive brand and institutional keywords that trigger spoofing alerts
    BRAND_KEYWORDS = [
        "paypal", "apple", "amazon", "google", "microsoft", "netflix",
        "facebook", "instagram", "sbi", "hdfc", "icici", "axis", "paytm",
        "phonepe", "binance", "coinbase", "irs", "incometax", "fedex", "dhl",
        "support", "security", "billing", "verification", "helpdesk", "itdesk",
        "compliance", "customs", "chase", "wellsfargo", "bankofamerica"
    ]

    @classmethod
    def _get_ml_model(cls):
        if not cls._ml_loaded:
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(base_dir, '..', 'ml', 'email_pattern_model.pkl')
                if os.path.exists(model_path):
                    cls._ml_model = joblib.load(model_path)
            except Exception:
                cls._ml_model = None
            cls._ml_loaded = True
        return cls._ml_model

    @classmethod
    def extract_features(cls, email: str, display_name: str = "") -> list:
        lower_e = email.lower().strip()
        lower_d = display_name.lower().strip()
        
        if "@" not in lower_e:
            return [0]*10
            
        local, domain = lower_e.split("@", 1)
        parts = domain.split(".")
        tld = parts[-1] if len(parts) > 1 else ""
        domain_root = parts[0] if parts else ""
        
        # 1. Brand in local part
        brand_in_local = 1 if any(b in local for b in cls.BRAND_KEYWORDS) else 0
        
        # 2. Free webmail
        is_free = 1 if domain in cls.FREE_WEBMAIL_PROVIDERS else 0
        
        # 3. Disposable
        is_disposable = 1 if (domain in cls.DISPOSABLE_EMAIL_PROVIDERS or any(domain.endswith("." + d) for d in cls.DISPOSABLE_EMAIL_PROVIDERS)) else 0
        
        # 4. Brand in non-official domain (Lookalike)
        is_lookalike = 0
        for brand, auth_domain in cls.TRUSTED_BRAND_DOMAINS.items():
            if domain != auth_domain and (brand in domain or brand in domain.replace('0','o').replace('1','l')):
                is_lookalike = 1
                break
                
        # 5. Display name spoofing
        display_spoof = 0
        if lower_d:
            for brand, auth_domain in cls.TRUSTED_BRAND_DOMAINS.items():
                if brand in lower_d and not (domain == auth_domain or domain.endswith("." + auth_domain)):
                    display_spoof = 1
                    break
                    
        # 6. High risk TLD
        is_bad_tld = 1 if tld in cls.HIGH_RISK_TLDS else 0
        
        # 7. Entropy of domain
        entropy = cls._calculate_entropy(domain_root)
        
        # 8. Digits in domain ratio
        digit_ratio = sum(c.isdigit() for c in domain_root) / max(1, len(domain_root))
        
        # 9. Subdomain nesting count
        subdomains = len(parts)
        
        # 10. Local-to-free mismatch
        free_brand_clash = 1 if (is_free and brand_in_local) else 0
        
        return [brand_in_local, is_free, is_disposable, is_lookalike, display_spoof, is_bad_tld, entropy, digit_ratio, subdomains, free_brand_clash]

    @classmethod
    def analyze(cls, email_str: str, display_name: str = "") -> Dict[str, Any]:
        if not email_str:
            return {"email": "", "risk_score": 0, "signals": [], "is_fake": False}

        score = 0
        signals = []
        lower_email = email_str.lower().strip()
        lower_display = (display_name or "").lower().strip()

        # Parse local-part and domain
        if "@" not in lower_email:
            return {"email": email_str, "risk_score": 25, "signals": ["Malformed email format"], "is_fake": False}

        local_part, domain = lower_email.split("@", 1)
        domain_parts = domain.split(".")
        tld = domain_parts[-1] if len(domain_parts) > 1 else ""

        # -------------------------------------------------------------
        # 1. Free Webmail Impersonation of High-Value Brands
        # -------------------------------------------------------------
        if domain in cls.FREE_WEBMAIL_PROVIDERS:
            matched_brands = [b for b in cls.BRAND_KEYWORDS if b in local_part]
            if matched_brands:
                signals.append(f"CRITICAL: Official brand impersonation ('{matched_brands[0]}') using free public webmail (@{domain})!")
                score += 85
            else:
                signals.append(f"Public free email provider (@{domain})")
                score += 5

        # -------------------------------------------------------------
        # 2. Disposable / Burner Email Detection
        # -------------------------------------------------------------
        if domain in cls.DISPOSABLE_EMAIL_PROVIDERS or any(domain.endswith("." + d) for d in cls.DISPOSABLE_EMAIL_PROVIDERS):
            signals.append(f"High-Risk: Originates from a disposable/temporary burner email provider (@{domain})")
            score += 75

        # -------------------------------------------------------------
        # 3. Lookalike / Typosquatting / Homoglyph Domain Detection
        # -------------------------------------------------------------
        for brand, auth_domain in cls.TRUSTED_BRAND_DOMAINS.items():
            if domain != auth_domain:
                normalized_domain = domain.replace('0', 'o').replace('1', 'l').replace('-', '')
                if brand in normalized_domain or brand in domain:
                    signals.append(f"CRITICAL: Lookalike domain spoofing '{brand}' (Auth: {auth_domain}, Found: {domain})")
                    score += 85
                    break
                domain_root = domain_parts[0] if domain_parts else ""
                auth_root = auth_domain.split(".")[0]
                if cls._levenshtein_distance(domain_root, auth_root) == 1 and len(domain_root) >= 4:
                    signals.append(f"CRITICAL: Typosquatting domain spoofing '{brand}' (1-char mutation: {domain})")
                    score += 85
                    break

        # -------------------------------------------------------------
        # 4. Display Name Spoofing
        # -------------------------------------------------------------
        if lower_display:
            for brand, auth_domain in cls.TRUSTED_BRAND_DOMAINS.items():
                if brand in lower_display:
                    if not (domain == auth_domain or domain.endswith("." + auth_domain)):
                        signals.append(f"CRITICAL: Display Name Spoofing! Claims to be '{display_name}' but sent from unauthorized domain '{domain}'")
                        score += 80
                        break

        # -------------------------------------------------------------
        # 5. High-Risk TLD Abuse
        # -------------------------------------------------------------
        if tld in cls.HIGH_RISK_TLDS:
            signals.append(f"High-risk top-level domain (. {tld}) frequently leveraged in spam campaigns")
            score += 35

        # -------------------------------------------------------------
        # 6. High-Entropy / DGA (Random Alphanumeric Domain)
        # -------------------------------------------------------------
        domain_name_only = domain_parts[0] if domain_parts else ""
        if len(domain_name_only) >= 8 and cls._calculate_entropy(domain_name_only) > 3.2:
            signals.append("High-entropy / randomly generated domain name (possible DGA infrastructure)")
            score += 40

        # Excessive Subdomains
        if len(domain_parts) > 3:
            signals.append("Excessive domain nesting / suspicious subdomain chaining")
            score += 20

        # -------------------------------------------------------------
        # 7. Machine Learning Pattern Model Inference
        # -------------------------------------------------------------
        model = cls._get_ml_model()
        if model:
            try:
                feats = cls.extract_features(email_str, display_name)
                proba = float(model.predict_proba([feats])[0][1])
                if proba >= 0.70:
                    ml_pts = int(round(proba * 60))
                    score = max(score, ml_pts)
                    signals.append(f"AI Email Classifier: Spoofed/Malicious sender pattern identified (Confidence: {int(proba*100)}%)")
            except Exception:
                pass

        final_score = min(100, score)
        return {
            "email": email_str,
            "display_name": display_name,
            "risk_score": final_score,
            "signals": list(dict.fromkeys(signals)),
            "is_fake": final_score >= 40
        }

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return EmailDetector._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy
