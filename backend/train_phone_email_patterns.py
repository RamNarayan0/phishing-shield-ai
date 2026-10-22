import os
import re
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

from app.detectors.phone_detector import PhoneDetector
from app.detectors.email_detector import EmailDetector
from app.extraction.phone_extractor import PhoneExtractor
from app.extraction.email_extractor import EmailExtractor

def extract_phone_features(phone: str, context: str = "") -> list:
    clean = re.sub(r'\D', '', phone)
    length = len(clean)
    
    # 1. Country code risk
    code_risk = 0
    for code, (_, _, weight) in PhoneDetector.HIGH_RISK_COUNTRY_CODES.items():
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
    
    # 5. Institutional context threat
    lower_ctx = (context or "").lower()
    has_inst_threat = 1 if any(kw in lower_ctx for kw in PhoneDetector.INSTITUTIONAL_KEYWORDS) else 0
    has_call_cta = 1 if any(cta in lower_ctx for cta in PhoneDetector.SUSPICIOUS_CTA_PHRASES) else 0
    
    # 6. Indian mobile flag
    is_indian = 1 if ((clean.startswith("91") and length == 12) or (length == 10 and clean and clean[0] in '6789')) else 0
    
    return [code_risk, is_premium, length, entropy, repeat_ratio, has_inst_threat, has_call_cta, is_indian]

def extract_email_features(email: str, display_name: str = "") -> list:
    lower_e = email.lower().strip()
    lower_d = display_name.lower().strip()
    
    if "@" not in lower_e:
        return [0]*10
        
    local, domain = lower_e.split("@", 1)
    parts = domain.split(".")
    tld = parts[-1] if len(parts) > 1 else ""
    domain_root = parts[0] if parts else ""
    
    # 1. Brand in local part
    brand_in_local = 1 if any(b in local for b in EmailDetector.BRAND_KEYWORDS) else 0
    
    # 2. Free webmail
    is_free = 1 if domain in EmailDetector.FREE_WEBMAIL_PROVIDERS else 0
    
    # 3. Disposable
    is_disposable = 1 if (domain in EmailDetector.DISPOSABLE_EMAIL_PROVIDERS or any(domain.endswith("." + d) for d in EmailDetector.DISPOSABLE_EMAIL_PROVIDERS)) else 0
    
    # 4. Brand in non-official domain (Lookalike)
    is_lookalike = 0
    for brand, auth_domain in EmailDetector.TRUSTED_BRAND_DOMAINS.items():
        if domain != auth_domain and (brand in domain or brand in domain.replace('0','o').replace('1','l')):
            is_lookalike = 1
            break
            
    # 5. Display name spoofing
    display_spoof = 0
    if lower_d:
        for brand, auth_domain in EmailDetector.TRUSTED_BRAND_DOMAINS.items():
            if brand in lower_d and not (domain == auth_domain or domain.endswith("." + auth_domain)):
                display_spoof = 1
                break
                
    # 6. High risk TLD
    is_bad_tld = 1 if tld in EmailDetector.HIGH_RISK_TLDS else 0
    
    # 7. Entropy of domain
    entropy = EmailDetector._calculate_entropy(domain_root)
    
    # 8. Digits in domain ratio
    digit_ratio = sum(c.isdigit() for c in domain_root) / max(1, len(domain_root))
    
    # 9. Subdomain nesting count
    subdomains = len(parts)
    
    # 10. Local-to-free mismatch
    free_brand_clash = 1 if (is_free and brand_in_local) else 0
    
    return [brand_in_local, is_free, is_disposable, is_lookalike, display_spoof, is_bad_tld, entropy, digit_ratio, subdomains, free_brand_clash]

def train_phone_pattern_model():
    print("=" * 60)
    print("TRAINING PHONE NUMBER SPAM & SMISHING PATTERN MODEL")
    print("=" * 60)
    
    # Build phone benchmark dataset
    samples = [
        # Legitimate contacts (Label 0)
        ("+919848012345", "Hey can you call me when you reach home?", 0),
        ("+918765432109", "Let's catch up tomorrow at college campus.", 0),
        ("+12125550198", "Here is our office support line for conference registration.", 0),
        ("+442079460912", "London corporate office main desk.", 0),
        ("+919820011223", "Swiggy driver delivery coordination contact.", 0),
        ("+919440123456", "Uncle visiting Hyderabad this weekend.", 0),
        ("+14155552671", "Engineering team daily standup dial-in.", 0),
        ("+919100234567", "Study group discussion on Tuesday.", 0),
        
        # Spam / High-Risk / Smishing (Label 1)
        ("+2348021234567", "Contact HR manager on WhatsApp to earn daily commission.", 1),
        ("+2349012345678", "Foreign investment fund manager payout.", 1),
        ("+923001234567", "Congratulations! Won 25 Lakhs in KBC WhatsApp Lottery. Contact manager.", 1),
        ("+923129876543", "WhatsApp lucky winner reward verification.", 1),
        ("+855977123456", "High paying online typing task from Cambodia compound.", 1),
        ("+95912345678", "Crypto investment double return guarantee Myanmar.", 1),
        ("+919876543210", "Dear customer, electricity bill unpaid. Power supply will be disconnected tonight. Call officer immediately: +919876543210", 1),
        ("+918877665544", "URGENT: Your SBI bank account will be blocked. Call bank officer on mobile to verify KYC.", 1),
        ("09061701461", "WINNER!! Claim £900 cash reward. Call 09061701461 now.", 1),
        ("09012345678", "Live adult chat line call 09012345678 only £2/min.", 1),
        ("+19005551234", "Call now to speak to your personal psychic advisor.", 1),
        ("Shortcode:87121", "Text FA to 87121 to win FA Cup tickets standard network rates apply.", 1),
        ("Shortcode:87575", "Send CASH to 87575 for £1000 prize entry.", 1),
        ("+919999999999", "Dummy testing line spam.", 1),
        ("+447012345678", "UK personal redirect routing advance fee fee trap.", 1)
    ]
    
    # Synthesize variations with noise
    X_rows, y_rows = [], []
    for ph, ctx, lbl in samples:
        feats = extract_phone_features(ph, ctx)
        X_rows.append(feats)
        y_rows.append(lbl)
        # Data augmentation
        for _ in range(20):
            noisy = [f + np.random.normal(0, 0.05) if isinstance(f, float) else f for f in feats]
            X_rows.append(noisy)
            y_rows.append(lbl)
            
    X = np.array(X_rows)
    y = np.array(y_rows)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"Phone Pattern Model Accuracy: {acc * 100:.2f}% | F1: {f1 * 100:.2f}%")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(base_dir, 'app', 'ml')
    os.makedirs(ml_dir, exist_ok=True)
    out_path = os.path.join(ml_dir, 'phone_pattern_model.pkl')
    joblib.dump(clf, out_path)
    print(f"[OK] Saved phone pattern model to: {out_path}")

def train_email_pattern_model():
    print("\n" + "=" * 60)
    print("TRAINING EMAIL SPOOFING & FAKE SENDER PATTERN MODEL")
    print("=" * 60)
    
    samples = [
        # Legitimate Corporate & Personal (Label 0)
        ("service@paypal.com", "PayPal Inc", 0),
        ("no-reply@apple.com", "Apple", 0),
        ("orders@amazon.com", "Amazon.com", 0),
        ("support@google.com", "Google Support", 0),
        ("alerts@hdfcbank.com", "HDFC Bank Alert", 0),
        ("contact@onlinesbi.sbi", "State Bank of India", 0),
        ("info@microsoft.com", "Microsoft Corporation", 0),
        ("rahul.sharma@gmail.com", "Rahul Sharma", 0),
        ("priya98@yahoo.com", "Priya", 0),
        ("vincent.kaminski@enron.com", "Vince Kaminski", 0),
        
        # Spoofed / Fake / Free Webmail Impersonation / Lookalike (Label 1)
        ("paypal.support@gmail.com", "PayPal Customer Support", 1),
        ("sbi.kyc.verification@yahoo.com", "State Bank of India", 1),
        ("appleid.helpdesk@outlook.com", "Apple ID Security", 1),
        ("netflix.billing@hotmail.com", "Netflix Alerts", 1),
        ("security@paypa1.com", "PayPal Official", 1),
        ("support@app1e-verify.com", "Apple Support", 1),
        ("billing@netf1ix-billing.xyz", "Netflix Streaming", 1),
        ("kyc-team@sbi-kyc-update.top", "SBI Bank Official", 1),
        ("refund@incometax-refund.site", "Income Tax Department", 1),
        ("admin@x98fa12c.top", "IT Desk Admin", 1),
        ("user1029@tempmail.com", "Confidential Partner", 1),
        ("alert@mailinator.com", "Account Alert", 1),
        ("security-alert@random-server.ru", "State Bank of India", 1),
        ("officer@freehost.net", "HDFC Bank Security", 1)
    ]
    
    X_rows, y_rows = [], []
    for em, dn, lbl in samples:
        feats = extract_email_features(em, dn)
        X_rows.append(feats)
        y_rows.append(lbl)
        for _ in range(25):
            noisy = [f + np.random.normal(0, 0.04) if isinstance(f, float) else f for f in feats]
            X_rows.append(noisy)
            y_rows.append(lbl)
            
    X = np.array(X_rows)
    y = np.array(y_rows)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"Email Pattern Model Accuracy: {acc * 100:.2f}% | F1: {f1 * 100:.2f}%")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(base_dir, 'app', 'ml')
    os.makedirs(ml_dir, exist_ok=True)
    out_path = os.path.join(ml_dir, 'email_pattern_model.pkl')
    joblib.dump(clf, out_path)
    print(f"[OK] Saved email pattern model to: {out_path}")

if __name__ == "__main__":
    train_phone_pattern_model()
    train_email_pattern_model()
