import os
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove excessive newlines/tabs
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Normalize spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def build_dataset():
    records = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(base_dir, '..', 'datasets')

    # 1. Nazario Phishing Corpus (Kaggle standard for phishing emails)
    nazario_path = os.path.join(datasets_dir, 'nazario_phishing.csv')
    if os.path.exists(nazario_path):
        print(f"Loading Nazario phishing dataset: {nazario_path}")
        df = pd.read_csv(nazario_path, on_bad_lines='skip')
        for _, row in df.iterrows():
            subj = str(row.get('subject', '')) if pd.notna(row.get('subject')) else ''
            body = str(row.get('body', '')) if pd.notna(row.get('body')) else ''
            full_txt = clean_text(f"{subj} {body}")
            if len(full_txt) > 20:
                records.append({'text': full_txt, 'label': 1, 'source': 'Nazario'})

    # 2. SpamAssassin Corpus (Ham + Phishing/Spam)
    sa_path = os.path.join(datasets_dir, 'spamassassin.csv')
    if os.path.exists(sa_path):
        print(f"Loading SpamAssassin dataset: {sa_path}")
        df = pd.read_csv(sa_path, on_bad_lines='skip')
        for _, row in df.iterrows():
            subj = str(row.get('subject', '')) if pd.notna(row.get('subject')) else ''
            body = str(row.get('body', '')) if pd.notna(row.get('body')) else ''
            lbl = int(row.get('label', 0))
            full_txt = clean_text(f"{subj} {body}")
            if len(full_txt) > 20:
                records.append({'text': full_txt, 'label': lbl, 'source': 'SpamAssassin'})

    # 3. Nigerian / Advance-Fee Fraud Emails (Financial Scams)
    fraud_path = os.path.join(datasets_dir, 'nigerian_fraud.csv')
    if os.path.exists(fraud_path):
        print(f"Loading Nigerian fraud dataset: {fraud_path}")
        df = pd.read_csv(fraud_path, on_bad_lines='skip')
        for _, row in df.iterrows():
            subj = str(row.get('subject', '')) if pd.notna(row.get('subject')) else ''
            body = str(row.get('body', '')) if pd.notna(row.get('body')) else ''
            full_txt = clean_text(f"{subj} {body}")
            if len(full_txt) > 20:
                records.append({'text': full_txt, 'label': 1, 'source': 'Nigerian_Fraud'})

    # 4. SMS Spam / Smishing Collection (UCI / Kaggle)
    sms_path = os.path.join(datasets_dir, 'sms_spam_collection.tsv')
    if os.path.exists(sms_path):
        print(f"Loading SMS Spam/Smishing dataset: {sms_path}")
        df = pd.read_csv(sms_path, sep='\t', names=['label_str', 'text'], on_bad_lines='skip')
        for _, row in df.iterrows():
            lbl = 1 if str(row['label_str']).lower() == 'spam' else 0
            txt = clean_text(str(row['text']))
            if len(txt) > 10:
                records.append({'text': txt, 'label': lbl, 'source': 'SMS_Spam'})

    # 5. Targeted modern chat & web UI samples (WhatsApp, KYC, Bank, normal chat)
    modern_samples = [
        # Normal chat / web UI
        ("Hey, are you free this evening for the study session?", 0, "Modern_Curated"),
        ("Let's meet at college canteen around 12:30 PM.", 0, "Modern_Curated"),
        ("Can you please share the PPT slides from the lab presentation?", 0, "Modern_Curated"),
        ("The class has been rescheduled to Thursday 2 PM by HOD.", 0, "Modern_Curated"),
        ("Hi dad, reaching home by 8 PM, traffic near Uppal.", 0, "Modern_Curated"),
        ("Please find attached the signed project abstract document for review.", 0, "Modern_Curated"),
        ("Google Meet link for tomorrow morning seminar discussion.", 0, "Modern_Curated"),
        ("Thanks for the update, see you tomorrow.", 0, "Modern_Curated"),
        ("Did you complete the assignment for Cyber Security module 4?", 0, "Modern_Curated"),
        ("Your OTP for Swiggy order delivery is 4821. Do not share with anyone.", 0, "Modern_Curated"),
        ("Your Uber ride OTP is 3912. Share with driver to start trip.", 0, "Modern_Curated"),
        # Modern Phishing / Smishing / WhatsApp Scams
        ("URGENT: Your SBI net banking account is blocked due to missing PAN update. Verify immediately at http://sbi-kyc-update.com", 1, "Modern_Curated"),
        ("Dear customer, electricity bill unpaid. Power supply will be disconnected tonight 9:30 PM. Call electricity officer immediately: +919876543210", 1, "Modern_Curated"),
        ("HDFC Alert: Your credit card reward points worth Rs.9,850 expiring today. Redeem cash directly to account: http://hdfc-rewards-cash.xyz", 1, "Modern_Curated"),
        ("Amazon Delivery: Your parcel is on hold due to wrong address. Update shipping info and pay Rs.25 re-delivery fee: http://amazon-parcel-delivery.top", 1, "Modern_Curated"),
        ("Paytm KYC Suspended: Complete biometric video verification within 24 hours to prevent wallet freeze: http://paytm-kyc-auth.net", 1, "Modern_Curated"),
        ("WhatsApp Web security notice: Suspicious login from Moscow, Russia. If not you, cancel device access now: http://whatsapp-web-verify.info", 1, "Modern_Curated"),
        ("Binance Alert: Unauthorized withdrawal request of 0.85 BTC detected. Cancel withdrawal immediately: http://binance-security-cancel.online", 1, "Modern_Curated"),
        ("Part time work from home: Earn Rs.3000 to Rs.8000 daily by liking YouTube videos and Telegram channels. Contact HR manager now: +2348021234567", 1, "Modern_Curated"),
        ("Income Tax Refund: You have an approved refund of Rs.24,500. Enter bank account and IFSC to credit: http://incometax-efiling-refund.co", 1, "Modern_Curated"),
        ("Congratulations! Your mobile number won 25 Lakhs in Kaun Banega Crorepati WhatsApp Lottery. Contact lottery manager: +923001234567", 1, "Modern_Curated")
    ]
    for txt, lbl, src in modern_samples:
        records.append({'text': clean_text(txt), 'label': lbl, 'source': src})

    full_df = pd.DataFrame(records)
    # Deduplicate
    full_df = full_df.drop_duplicates(subset=['text']).reset_index(drop=True)
    
    # Save combined master dataset
    output_csv = os.path.join(datasets_dir, 'kaggle_combined_phishing_dataset.csv')
    full_df.to_csv(output_csv, index=False)
    print(f"\nSaved combined master dataset to {output_csv}")
    print(f"Total samples: {len(full_df)}")
    print(f"Legitimate (Safe): {sum(full_df['label'] == 0)}")
    print(f"Phishing/Scams: {sum(full_df['label'] == 1)}")
    
    return full_df

def train_and_evaluate(df):
    X = df['text']
    y = df['label']

    print("\nSplitting into Train (80%) and Test (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("Extracting TF-IDF features (unigrams + bigrams, sublinear TF)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=12000,
        sublinear_tf=True,
        stop_words='english',
        min_df=2
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression Classifier...")
    model = LogisticRegression(C=2.5, max_iter=1000, solver='lbfgs', random_state=42)
    model.fit(X_train_vec, y_train)

    # Predictions
    y_pred = model.predict(X_test_vec)
    y_proba = model.predict_proba(X_test_vec)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n" + "="*50)
    print("MODEL TRAINING & EVALUATION REPORT")
    print("="*50)
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"ROC-AUC:   {auc * 100:.2f}%")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Phishing (1)'], digits=4))

    # Save to production location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(base_dir, 'app', 'ml')
    os.makedirs(ml_dir, exist_ok=True)

    vec_path = os.path.join(ml_dir, 'vectorizer.pkl')
    model_path = os.path.join(ml_dir, 'model.pkl')
    joblib.dump(vectorizer, vec_path)
    joblib.dump(model, model_path)

    print(f"\n[OK] Production Model saved to: {model_path}")
    print(f"[OK] Production Vectorizer saved to: {vec_path}")

    # Run quick sanity check
    test_phish = "URGENT: Your bank account is locked. Verify at http://fake-login.com"
    test_safe = "Hey, are we still meeting for lunch near the campus library?"
    p_phish = model.predict_proba(vectorizer.transform([test_phish]))[0][1]
    p_safe = model.predict_proba(vectorizer.transform([test_safe]))[0][1]
    print("\nSanity Check:")
    print(f"  Phishing sample probability: {p_phish*100:.2f}% (Expected >90%)")
    print(f"  Safe sample probability:     {p_safe*100:.2f}% (Expected <10%)")

if __name__ == "__main__":
    df = build_dataset()
    train_and_evaluate(df)
