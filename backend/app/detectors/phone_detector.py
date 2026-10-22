import re
import math
import os
import joblib
from typing import Dict, Any, List

class PhoneDetector:
    _ml_model = None
    _ml_loaded = False

    # High-Risk Country Codes frequently associated with international cyber scams & smishing
    HIGH_RISK_COUNTRY_CODES = {
        "+234": ("Nigeria", "Advance fee fraud, Telegram task scam & romance scam hub", 55),
        "+92":  ("Pakistan", "WhatsApp lottery scam (KBC fraud) & impersonation calls", 55),
        "+855": ("Cambodia", "Southeast Asian cyber scam compounds & pig-butchering syndicates", 60),
        "+95":  ("Myanmar", "Cybercrime scam parks & forced labor call-center operations", 60),
        "+856": ("Laos", "Special economic zone cyber scam operations", 55),
        "+254": ("Kenya", "Mobile money social engineering & phishing rings", 40),
        "+233": ("Ghana", "Cryptocurrency & impersonation fraud rings", 40),
        "+27":  ("South Africa", "Boiler room & lottery phishing syndicates", 35),
        "+371": ("Latvia", "Disposable bulletproof VoIP routing", 35),
        "+370": ("Lithuania", "Disposable VoIP rerouting", 30),
        "+4470":("UK PNS", "UK Personal Numbering Service (premium callback redirect)", 50)
    }

    # Institutional keywords that NEVER legitimately use personal 10-digit mobile numbers for alerts
    INSTITUTIONAL_KEYWORDS = [
        "electricity", "power supply", "disconnected", "bill unpaid",
        "sbi", "hdfc", "icici", "axis", "bank account", "net banking",
        "kyc", "pan card", "aadhaar", "trai", "sim blocked",
        "customs", "parcel held", "fedex parcel", "police", "cbi", "court"
    ]

    # Scam Call-to-Action phrases
    SUSPICIOUS_CTA_PHRASES = [
        "call electricity officer", "call officer", "call manager", 
        "contact lottery manager", "call immediately", "whatsapp hr",
        "call now to claim", "call to claim", "text to claim",
        "dial to activate", "contact customer care on"
    ]

    @classmethod
    def _get_ml_model(cls):
        if not cls._ml_loaded:
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(base_dir, '..', 'ml', 'phone_pattern_model.pkl')
                if os.path.exists(model_path):
                    cls._ml_model = joblib.load(model_path)
            except Exception:
                cls._ml_model = None
            cls._ml_loaded = True
        return cls._ml_model

    @classmethod
    def extract_features(cls, phone: str, context: str = "") -> list:
        clean = re.sub(r'\D', '', phone)
        length = len(clean)
        
        # 1. Country code risk
        code_risk = 0
        for code, (_, _, weight) in cls.HIGH_RISK_COUNTRY_CODES.items():
            if phone.startswith(code):
                code_risk = weight
                break
                
        # 2. Premium rate
        is_premium = 1 if (clean.startswith("090") or clean.startswith("091") or clean.startswith("4490") or clean.startswith("1900") or phone.startswith("Shortcode:")) else 0
        
        # 3. Digit entropy
        if length > 0:
            prob = [clean.count(c)/length for c in set(clean)]
            entropy = -sum([p * math.log2(p) for p in prob])
        else:
            entropy = 0.0
            
        # 4. Repeated digits ratio
        repeat_ratio = (max([clean.count(c) for c in set(clean)]) / length) if length > 0 else 0.0
        
        # 5. Context threats
        lower_ctx = (context or "").lower()
        has_inst_threat = 1 if any(kw in lower_ctx for kw in cls.INSTITUTIONAL_KEYWORDS) else 0
        has_call_cta = 1 if any(cta in lower_ctx for cta in cls.SUSPICIOUS_CTA_PHRASES) else 0
        
        # 6. Indian mobile flag
        is_indian = 1 if ((clean.startswith("91") and length == 12) or (length == 10 and clean and clean[0] in '6789')) else 0
        
        return [code_risk, is_premium, length, entropy, repeat_ratio, has_inst_threat, has_call_cta, is_indian]

    @classmethod
    def analyze(cls, phone: str, context_text: str = "") -> Dict[str, Any]:
        if not phone:
            return {"phone": "", "risk_score": 0, "signals": [], "is_spam": False}

        score = 0
        signals = []
        lower_context = (context_text or "").lower()
        clean_num = re.sub(r'[\s\-\(\)\.]', '', phone)

        # -------------------------------------------------------------
        # 1. Premium Shortcodes Check (e.g. Shortcode:87121)
        # -------------------------------------------------------------
        if phone.startswith("Shortcode:"):
            code = phone.split(":", 1)[1]
            signals.append(f"SMS Premium Rate Shortcode detected ({code}) - often triggers recurring billing")
            score += 45

        # -------------------------------------------------------------
        # 2. UK Premium Rate & Toll Fraud (090x, 091x, 0871x, +4490x)
        # -------------------------------------------------------------
        if clean_num.startswith("090") or clean_num.startswith("091") or clean_num.startswith("+4490"):
            signals.append("UK Premium Rate Number (exorbitant per-minute callback charge)")
            score += 65
        elif clean_num.startswith("0871") or clean_num.startswith("0872") or clean_num.startswith("0870"):
            signals.append("UK Non-Geographic High-Rate Business Number")
            score += 35

        # -------------------------------------------------------------
        # 3. US/Canada 900 Pay-Per-Call
        # -------------------------------------------------------------
        if clean_num.startswith("+1900") or (clean_num.startswith("1900") and len(clean_num) == 11) or (clean_num.startswith("900") and len(clean_num) == 10):
            signals.append("US 900 Pay-Per-Call Premium Service (toll-fraud risk)")
            score += 65

        # -------------------------------------------------------------
        # 4. High-Risk International Country Codes
        # -------------------------------------------------------------
        for code, (country, description, risk_weight) in cls.HIGH_RISK_COUNTRY_CODES.items():
            if clean_num.startswith(code):
                signals.append(f"High-risk international origin: {country} ({code}) - {description}")
                score += risk_weight
                break

        # -------------------------------------------------------------
        # 5. Institutional Smishing via Personal Mobile Number
        # -------------------------------------------------------------
        is_indian_mobile = (clean_num.startswith("+91") and len(clean_num) == 13 and clean_num[3] in '6789') or \
                           (len(clean_num) == 10 and clean_num[0] in '6789')

        if is_indian_mobile:
            has_institution_threat = any(kw in lower_context for kw in cls.INSTITUTIONAL_KEYWORDS)
            has_urgent_call_cta = any(cta in lower_context for cta in cls.SUSPICIOUS_CTA_PHRASES)

            if has_institution_threat:
                signals.append("CRITICAL: Institutional impersonation! Official utility/bank threats never use personal mobile numbers")
                score += 70
            elif has_urgent_call_cta:
                signals.append("Suspicious: Unsolicited message instructs immediate direct call to private mobile number")
                score += 35

        # -------------------------------------------------------------
        # 6. Structural & Spoofing Anomalies (Repetitive / Dummy Digits)
        # -------------------------------------------------------------
        digits_only = re.sub(r'\D', '', clean_num)
        if len(digits_only) >= 7:
            for digit in "0123456789":
                if digit * 6 in digits_only:
                    signals.append("Anomalous phone number structure (repetitive dummy digits)")
                    score += 40
                    break
            if "123456" in digits_only or "987654" in digits_only:
                signals.append("Sequential dummy phone number detected")
                score += 40

        # -------------------------------------------------------------
        # 7. Machine Learning Pattern Model Inference
        # -------------------------------------------------------------
        model = cls._get_ml_model()
        if model:
            try:
                feats = cls.extract_features(phone, context_text)
                proba = float(model.predict_proba([feats])[0][1])
                if proba >= 0.70:
                    ml_pts = int(round(proba * 60))
                    score = max(score, ml_pts)
                    signals.append(f"AI Phone Classifier: Spam/fraud pattern identified (Confidence: {int(proba*100)}%)")
            except Exception:
                pass

        # Cap score at 100
        final_score = min(100, score)
        return {
            "phone": phone,
            "risk_score": final_score,
            "signals": list(dict.fromkeys(signals)),
            "is_spam": final_score >= 40
        }
