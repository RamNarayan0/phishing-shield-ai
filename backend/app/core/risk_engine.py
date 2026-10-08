from app.detectors.text_detector import TextDetector
from app.detectors.url_detector import URLDetector
from app.detectors.sender_detector import SenderDetector
from app.core.ml_engine import MLEngine
from typing import Dict, Any, List

class RiskEngine:
    
    @classmethod
    def calculate_verdict(cls, text_analysis: Dict, url_analyses: List[Dict], sender_analysis: Dict, ml_analysis: Dict = None) -> Dict[str, Any]:
        if ml_analysis is None:
            ml_analysis = {"ml_score": 0, "active": False}
            
        max_url_risk = max([u["risk_score"] for u in url_analyses]) if url_analyses else 0
        
        text_risk = text_analysis.get("risk_score", 0)
        sender_risk = sender_analysis.get("risk_score", 0)
        ml_score = ml_analysis.get("ml_score", 0)
        
        # HYBRID MODEL CALCULATION
        # Only use ML score if it indicates at least suspicious behavior
        if ml_analysis.get("active") and ml_score >= 40:
            hybrid_text_score = max(text_risk, ml_score)
        else:
            hybrid_text_score = text_risk
            
        base_risk = max(hybrid_text_score, max_url_risk)
        
        if url_analyses:
            raw_score = base_risk + (min(hybrid_text_score, max_url_risk) * 0.8) + (sender_risk * 0.3)
            # Boost score heavily if multiple risk categories are triggered
            if hybrid_text_score >= 20 and max_url_risk >= 20:
                raw_score += 35
        else:
            # If there is NO URL, it's highly unlikely to be a critical phishing attack unless it explicitly requests money/passwords.
            raw_score = hybrid_text_score * 0.5 + (sender_risk * 0.4)
            # Cap text-only threats at 59 (Suspicious, not High/Critical) unless ML is extremely confident (95%+)
            if raw_score > 59 and ml_score < 95:
                raw_score = 59

        # Direct Sender Override: If the sender is definitively spoofing a protected brand, it is CRITICAL.
        if sender_risk >= 80:
            raw_score = max(raw_score, sender_risk)
            
        # Cap at 100
        final_score = int(min(100, max(0, raw_score)))
        
        reasons = []
        if ml_analysis.get("active") and ml_score > 60:
            reasons.append(f"AI Model classified as malicious (Confidence: {ml_score}%)")
            
        reasons.extend(text_analysis.get("signals", []))
        for analysis in url_analyses:
            reasons.extend(analysis.get("signals", []))
        reasons.extend(sender_analysis.get("signals", []))
        
        # Deduplicate reasons
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
            "verdict": verdict,
            "confidence": min(1.0, final_score / 100.0 + 0.1),
            "reasons": reasons,
            "recommended_action": recommended_action,
            "extracted_urls": [u.get("url") for u in url_analyses if "url" in u]
        }
