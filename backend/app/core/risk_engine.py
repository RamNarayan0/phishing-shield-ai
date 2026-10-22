from typing import Dict, Any, List

class RiskEngine:
    
    @classmethod
    def calculate_verdict(
        cls,
        text_analysis: Dict,
        url_analyses: List[Dict],
        sender_analysis: Dict,
        ml_analysis: Dict = None,
        phone_analyses: List[Dict] = None,
        email_analyses: List[Dict] = None
    ) -> Dict[str, Any]:
        if ml_analysis is None:
            ml_analysis = {"ml_score": 0, "active": False}
        if phone_analyses is None:
            phone_analyses = []
        if email_analyses is None:
            email_analyses = []
            
        max_url_risk = max([u.get("risk_score", 0) for u in url_analyses]) if url_analyses else 0
        max_phone_risk = max([p.get("risk_score", 0) for p in phone_analyses]) if phone_analyses else 0
        max_email_risk = max([e.get("risk_score", 0) for e in email_analyses]) if email_analyses else 0
        
        text_risk = text_analysis.get("risk_score", 0)
        sender_risk = max(sender_analysis.get("risk_score", 0), max_email_risk)
        ml_score = ml_analysis.get("ml_score", 0)
        
        # Combined contact vector risk (Phone call / Email callback / URL visit)
        contact_vector_risk = max(max_url_risk, max_phone_risk, max_email_risk)
        
        # HYBRID MODEL CALCULATION
        if ml_analysis.get("active") and ml_score >= 35:
            hybrid_text_score = max(text_risk, ml_score)
        else:
            hybrid_text_score = text_risk
            
        base_risk = max(hybrid_text_score, contact_vector_risk)
        
        if url_analyses:
            raw_score = base_risk + (min(hybrid_text_score, max_url_risk) * 0.8) + (sender_risk * 0.3)
            if hybrid_text_score >= 20 and max_url_risk >= 20:
                raw_score += 35
        elif phone_analyses and max_phone_risk >= 50:
            # Dangerous callback smishing (Electricity cut, fake lottery call, toll trap)
            raw_score = max_phone_risk + (hybrid_text_score * 0.4)
        else:
            raw_score = hybrid_text_score * 0.5 + (sender_risk * 0.4)
            # Cap purely benign text without suspicious links, phones, or senders at 59
            if raw_score > 59 and ml_score < 95 and contact_vector_risk < 40 and sender_risk < 50:
                raw_score = 59

        # Direct Overrides for high-confidence indicators
        if sender_risk >= 80:
            raw_score = max(raw_score, sender_risk)
        if max_phone_risk >= 70:
            raw_score = max(raw_score, max_phone_risk)
            
        # Cap at 100
        final_score = int(min(100, max(0, raw_score)))
        
        reasons = []
        if ml_analysis.get("active") and ml_score > 60:
            reasons.append(f"AI Model classified text as malicious (Confidence: {ml_score}%)")
            
        reasons.extend(text_analysis.get("signals", []))
        for analysis in url_analyses:
            reasons.extend(analysis.get("signals", []))
        for analysis in phone_analyses:
            reasons.extend(analysis.get("signals", []))
        for analysis in email_analyses:
            reasons.extend(analysis.get("signals", []))
        reasons.extend(sender_analysis.get("signals", []))
        
        # Deduplicate reasons preserving order
        reasons = list(dict.fromkeys(reasons))
        
        verdict = "SAFE"
        recommended_action = "SAFE_TO_OPEN"
        if final_score >= 80:
            verdict = "CRITICAL"
            recommended_action = "DO_NOT_OPEN"
        elif final_score >= 60:
            verdict = "HIGH RISK"
            recommended_action = "PROCEED_WITH_CAUTION"
        elif final_score >= 30:
            verdict = "SUSPICIOUS"
            recommended_action = "VERIFY_SOURCE"
            
        return {
            "risk_score": final_score,
            "ml_score": ml_score / 100.0,
            "heuristic_score": text_risk,
            "url_score": max_url_risk,
            "sender_score": sender_risk,
            "verdict": verdict,
            "confidence": min(1.0, final_score / 100.0 + 0.1),
            "reasons": reasons,
            "recommended_action": recommended_action,
            "extracted_urls": [u.get("url") for u in url_analyses if "url" in u],
            "extracted_phones": [p.get("phone") for p in phone_analyses if "phone" in p],
            "extracted_emails": [e.get("email") for e in email_analyses if "email" in e]
        }
