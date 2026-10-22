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
            
        # Generate Explainable Phishing Risk Breakdown
        explanation = cls.build_explanation(
            final_score=final_score,
            verdict=verdict,
            text_analysis=text_analysis,
            url_analyses=url_analyses,
            sender_analysis=sender_analysis,
            ml_analysis=ml_analysis,
            phone_analyses=phone_analyses,
            email_analyses=email_analyses
        )

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
            "extracted_emails": [e.get("email") for e in email_analyses if "email" in e],
            "explanation": explanation
        }

    @classmethod
    def build_explanation(
        cls,
        final_score: int,
        verdict: str,
        text_analysis: Dict,
        url_analyses: List[Dict],
        sender_analysis: Dict,
        ml_analysis: Dict,
        phone_analyses: List[Dict],
        email_analyses: List[Dict]
    ) -> Dict[str, Any]:
        signals = []
        text_signals = text_analysis.get("signals", [])

        # -------------------------------------------------------------
        # Category A: Message Content
        # -------------------------------------------------------------
        is_urg = "Urgent language" in text_signals
        signals.append({
            "signal_id": "urgency_language",
            "category": "message_content",
            "label": "Urgency & Artificial Time Pressure",
            "status": "detected" if is_urg else "not_detected",
            "severity": "high" if is_urg else "info",
            "description": "Message pressures immediate action to bypass critical thinking." if is_urg else "No aggressive urgency keywords or time-pressure tactics detected.",
            "contribution": 20 if is_urg else 0
        })

        is_threat = "Account suspension threat" in text_signals
        signals.append({
            "signal_id": "account_threat",
            "category": "message_content",
            "label": "Account Threat / Suspension Warning",
            "status": "detected" if is_threat else "not_detected",
            "severity": "critical" if is_threat else "info",
            "description": "Threatens service cutoff, account suspension, or security penalty." if is_threat else "No account termination or penalty threats observed.",
            "contribution": 30 if is_threat else 0
        })

        is_cred = "Credential request" in text_signals
        signals.append({
            "signal_id": "credential_request",
            "category": "message_content",
            "label": "Credential & Sensitive Data Request",
            "status": "detected" if is_cred else "not_detected",
            "severity": "critical" if is_cred else "info",
            "description": "Directly requests credentials, OTP, password, PIN, or personal identity details." if is_cred else "No explicit solicitation of credentials, OTPs, or passwords detected.",
            "contribution": 25 if is_cred else 0
        })

        is_fin = "Financial manipulation attempt" in text_signals
        signals.append({
            "signal_id": "financial_manipulation",
            "category": "message_content",
            "label": "Financial Manipulation",
            "status": "detected" if is_fin else "not_detected",
            "severity": "high" if is_fin else "info",
            "description": "Promises prizes/refunds or demands unauthorized transaction fees." if is_fin else "No fraudulent fee demands, fake prizes, or refund lures detected.",
            "contribution": 15 if is_fin else 0
        })

        is_se = "Social engineering tactics" in text_signals
        signals.append({
            "signal_id": "social_engineering",
            "category": "message_content",
            "label": "Social Engineering Traps",
            "status": "detected" if is_se else "not_detected",
            "severity": "medium" if is_se else "info",
            "description": "Uses deceptive lures such as delivery rescheduling or mandatory verification links." if is_se else "No generic delivery or click-trap social engineering found.",
            "contribution": 20 if is_se else 0
        })

        # -------------------------------------------------------------
        # Category B: URL Structure
        # -------------------------------------------------------------
        if url_analyses:
            all_url_signals = []
            for u in url_analyses:
                all_url_signals.extend(u.get("signals", []))

            has_http = any("Insecure connection (HTTP)" in s for s in all_url_signals)
            signals.append({
                "signal_id": "insecure_http",
                "category": "url_structure",
                "label": "Insecure Connection (Unencrypted HTTP)",
                "status": "detected" if has_http else "not_detected",
                "severity": "high" if has_http else "info",
                "description": "URL uses unencrypted HTTP instead of HTTPS, exposing transmitted data." if has_http else "All analyzed URLs use HTTPS encrypted transport.",
                "contribution": 20 if has_http else 0
            })

            has_ip = any("IP address instead of domain" in s for s in all_url_signals)
            signals.append({
                "signal_id": "ip_address_host",
                "category": "url_structure",
                "label": "Direct IP Address Host",
                "status": "detected" if has_ip else "not_detected",
                "severity": "critical" if has_ip else "info",
                "description": "Host uses a raw numerical IP address to conceal registration identity." if has_ip else "No raw IP address destinations detected.",
                "contribution": 40 if has_ip else 0
            })

            has_sub = any("Excessive subdomains" in s for s in all_url_signals)
            signals.append({
                "signal_id": "excessive_subdomains",
                "category": "url_structure",
                "label": "Excessive Subdomains",
                "status": "detected" if has_sub else "not_detected",
                "severity": "medium" if has_sub else "info",
                "description": "Deep subdomain chain frequently used to disguise the true root domain." if has_sub else "Subdomain hierarchy is standard and within normal bounds.",
                "contribution": 20 if has_sub else 0
            })

            has_typo = any("Suspicious character pattern" in s for s in all_url_signals)
            signals.append({
                "signal_id": "typosquatting_pattern",
                "category": "url_structure",
                "label": "Brand Typosquatting / Visual Mimicry",
                "status": "detected" if has_typo else "not_detected",
                "severity": "critical" if has_typo else "info",
                "description": "Domain mimics reputable brand names using homoglyphs, substitutions, or hyphens." if has_typo else "No brand typosquatting or character substitution patterns found.",
                "contribution": 30 if has_typo else 0
            })

            has_cred_path = any("Credential-oriented URL" in s for s in all_url_signals)
            signals.append({
                "signal_id": "credential_url_target",
                "category": "url_structure",
                "label": "Credential Target Path/Domain",
                "status": "detected" if has_cred_path else "not_detected",
                "severity": "high" if has_cred_path else "info",
                "description": "URL directs to login, verification, or account credential capture endpoints." if has_cred_path else "No sensitive login or credential-harvesting paths identified in link.",
                "contribution": 25 if has_cred_path else 0
            })
        else:
            signals.append({
                "signal_id": "url_analysis_unavailable",
                "category": "url_structure",
                "label": "URL Inspection",
                "status": "unavailable",
                "severity": "info",
                "description": "No URLs were detected in the input; link verification was not applicable.",
                "contribution": 0
            })

        # -------------------------------------------------------------
        # Category C: Machine Learning Evidence
        # -------------------------------------------------------------
        if ml_analysis.get("active"):
            proba = ml_analysis.get("probability", 0.0)
            score = ml_analysis.get("ml_score", 0)
            is_mal = score >= 50
            signals.append({
                "signal_id": "ml_text_classifier",
                "category": "ml_evidence",
                "label": "NLP Threat Probability Model",
                "status": "detected" if is_mal else "not_detected",
                "severity": "critical" if score >= 80 else ("high" if score >= 50 else "info"),
                "description": f"TF-IDF Logistic Regression model classified text as malicious with {proba:.1%} probability." if is_mal else f"ML model assessed text as benign ({1.0 - proba:.1%} benign probability).",
                "contribution": score if is_mal else 0
            })
        else:
            signals.append({
                "signal_id": "ml_text_classifier",
                "category": "ml_evidence",
                "label": "NLP Threat Probability Model",
                "status": "unavailable",
                "severity": "info",
                "description": "Machine learning model weights were inactive or unavailable during analysis.",
                "contribution": 0
            })

        # -------------------------------------------------------------
        # Category D: Sender Identity & Contact Patterns
        # -------------------------------------------------------------
        sender_signals = sender_analysis.get("signals", [])
        sender_val = (sender_analysis.get("sender") or "").strip()
        has_real_sender = bool(sender_val and sender_val.lower() not in ("", "unknown", "none", "unknown contact"))

        if has_real_sender:
            is_spoof = len(sender_signals) > 0
            signals.append({
                "signal_id": "sender_impersonation",
                "category": "sender_identity",
                "label": "Sender Address & Origin Check",
                "status": "detected" if is_spoof else "not_detected",
                "severity": "high" if is_spoof else "info",
                "description": "; ".join(sender_signals) if is_spoof else "Sender identity format is standard with no brand spoofing indicators.",
                "contribution": sender_analysis.get("risk_score", 0) if is_spoof else 0
            })
        else:
            signals.append({
                "signal_id": "sender_impersonation",
                "category": "sender_identity",
                "label": "Sender Address & Origin Check",
                "status": "unavailable",
                "severity": "info",
                "description": "No explicit sender header or address was supplied for origin verification.",
                "contribution": 0
            })

        if phone_analyses:
            phone_sigs = []
            for p in phone_analyses:
                phone_sigs.extend(p.get("signals", []))
            if phone_sigs:
                signals.append({
                    "signal_id": "phone_callback_trap",
                    "category": "contact_pattern",
                    "label": "Phone Number & Callback Verification",
                    "status": "detected",
                    "severity": "high",
                    "description": "; ".join(phone_sigs),
                    "contribution": max([p.get("risk_score", 0) for p in phone_analyses])
                })
            else:
                signals.append({
                    "signal_id": "phone_callback_trap",
                    "category": "contact_pattern",
                    "label": "Phone Number & Callback Verification",
                    "status": "not_detected",
                    "severity": "info",
                    "description": "Extracted phone numbers verified with standard regional patterns; no callback traps or toll fraud detected.",
                    "contribution": 0
                })

        if email_analyses:
            email_sigs = []
            for e in email_analyses:
                email_sigs.extend(e.get("signals", []))
            if email_sigs:
                signals.append({
                    "signal_id": "email_sender_spoofing",
                    "category": "sender_identity",
                    "label": "Email Address Domain & Provider Check",
                    "status": "detected",
                    "severity": "high",
                    "description": "; ".join(email_sigs),
                    "contribution": max([e.get("risk_score", 0) for e in email_analyses])
                })
            else:
                signals.append({
                    "signal_id": "email_sender_spoofing",
                    "category": "sender_identity",
                    "label": "Email Address Domain & Provider Check",
                    "status": "not_detected",
                    "severity": "info",
                    "description": "Extracted email addresses verified; no brand spoofing or disposable burner domains detected.",
                    "contribution": 0
                })

        # -------------------------------------------------------------
        # Category Summaries
        # -------------------------------------------------------------
        categories = {}
        cat_meta = {
            "message_content": "Message Content & Urgency Heuristics",
            "url_structure": "URL & Destination Structure",
            "ml_evidence": "Machine Learning Model Evidence",
            "sender_identity": "Sender Origin & Contact Vectors"
        }
        for cat_key, cat_title in cat_meta.items():
            if cat_key == "sender_identity":
                cat_signals = [s for s in signals if s["category"] in ("sender_identity", "contact_pattern")]
            else:
                cat_signals = [s for s in signals if s["category"] == cat_key]

            detected = [s for s in cat_signals if s["status"] == "detected"]
            evaluated = [s for s in cat_signals if s["status"] in ("detected", "not_detected")]

            if any(s["status"] == "detected" for s in cat_signals):
                c_status = "detected"
            elif any(s["status"] == "not_detected" for s in cat_signals):
                c_status = "clean"
            else:
                c_status = "unavailable"

            categories[cat_key] = {
                "category": cat_key,
                "title": cat_title,
                "detected_count": len(detected),
                "evaluated_count": len(evaluated),
                "status": c_status
            }

        # -------------------------------------------------------------
        # Human-Readable Summary
        # -------------------------------------------------------------
        detected_labels = [s["label"] for s in signals if s["status"] == "detected"]
        label_summary = f": {', '.join(detected_labels[:3])}" if detected_labels else ""
        if verdict == "CRITICAL":
            summary = f"Flagged as CRITICAL risk ({final_score}/100). High-confidence attack indicators detected{label_summary}."
        elif verdict == "HIGH RISK":
            summary = f"Flagged as HIGH RISK ({final_score}/100). Significant threat signals observed{label_summary}."
        elif verdict == "SUSPICIOUS":
            summary = f"Flagged as SUSPICIOUS ({final_score}/100). Anomalous characteristics identified{label_summary}."
        else:
            summary = f"Classified as SAFE ({final_score}/100). No phishing indicators, malicious link patterns, or coercive tactics were identified."

        rec_actions = {
            "SAFE": "Safe to view. Always verify sender identity before opening external attachments.",
            "SUSPICIOUS": "Proceed with caution. Verify the sender's identity through an independent, trusted channel.",
            "HIGH RISK": "Do not click links or call numbers provided in this message. Report and delete.",
            "CRITICAL": "DO NOT INTERACT. This is a high-confidence attack designed to steal credentials or funds."
        }

        return {
            "summary": summary,
            "signals": signals,
            "categories": categories,
            "recommended_action": rec_actions.get(verdict, "Exercise caution.")
        }
