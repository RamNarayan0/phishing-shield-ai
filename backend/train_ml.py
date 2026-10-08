import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def generate_and_train():
    # 1. Generate a small synthetic dataset for the prototype
    data = [
        # Safe
        {"text": "Hey Rahul, are you coming to college tomorrow?", "label": 0},
        {"text": "Let's meet near the library at 10 AM.", "label": 0},
        {"text": "Can you send me the notes from yesterday's lecture?", "label": 0},
        {"text": "I will be there in 5 minutes.", "label": 0},
        {"text": "Happy birthday! Have a great day.", "label": 0},
        {"text": "Check out this cool new song I found.", "label": 0},
        {"text": "Did you watch the match last night?", "label": 0},
        {"text": "I'm going to the grocery store, need anything?", "label": 0},
        {"text": "Please review the attached project proposal.", "label": 0},
        {"text": "Are we still on for lunch?", "label": 0},
        # -- New UI / Random Web Text (SAFE) --
        {"text": "1 Updates in Status M All Unread 1 Favourites Groups Message and call notifications are off.", "label": 0},
        {"text": "Turn on Archived CSM A 2026 ( PS1,2) 26/09/2026 PS 1 & 2 CSM ( A) unofficial", "label": 0},
        {"text": "Skip to content Using Gmail with screen readers Search Upgrade Upgrade for premium features Try Gemini Compose Labels Inbox 1,418 Starred Snoozed Sent Drafts Purchases 472", "label": 0},
        {"text": "# -------- COMMON DATASET -------- Marks (out of 100) for 30 students in a Python Programming test marks = [45, 67, 89, 34, 78, 92, 56, 73, 81, 39]", "label": 0},
        {"text": "students = ['Ravi', 'Priya', 'Arjun', 'Meena', 'Kiran'] top5_marks = [89, 92, 95, 88, 90] # subset for bar chart", "label": 0},
        {"text": "plt.figure(figsize=(6, 4)) plt.plot(unit_tests, ravi_scores, marker='o', color='blue', linewidth=2) plt.title", "label": 0},
        {"text": "Settings Profile Privacy Notifications Security Log out Home Explore Messages Notifications", "label": 0},
        {"text": "Terms of Service Privacy Policy Cookie Policy About Us Careers Press Contact", "label": 0},
        {"text": "New Message To: Subject: Send Discard Saved drafts", "label": 0},
        {"text": "Dashboard Analytics Reports Campaigns Users Settings Help & Support", "label": 0},
        {"text": "Your cart is empty. Continue shopping to add items.", "label": 0},
        {"text": "Update profile picture. Change password. Two-factor authentication.", "label": 0},
        
        # Suspicious / Phishing
        {"text": "Your account requires verification. Please verify your information immediately.", "label": 1},
        {"text": "URGENT: Your bank account has been suspended. Verify immediately at: https://secure-bank-login-example.com", "label": 1},
        {"text": "KYC VERIFICATION PENDING: Your crypto wallet will be frozen. Verify KYC now: https://binance-kyc-verify.io", "label": 1},
        {"text": "FedEx: Your package delivery failed. Pay the $2.99 fee to reschedule.", "label": 1},
        {"text": "Congratulations! You've won $1,000,000! Claim your prize here.", "label": 1},
        {"text": "Unusual login detected. Click here to secure your account.", "label": 1},
        {"text": "Your password will expire in 24 hours. Update your details now.", "label": 1},
        {"text": "Avoid account closure by clicking this link to confirm your identity.", "label": 1},
        {"text": "Final notice: Unpaid invoice attached. Open PDF to view.", "label": 1},
        {"text": "You are the lucky winner of a brand new iPhone. Claim it now!", "label": 1},
        {"text": "Warning: Unauthorized access to your email. Please login to secure it.", "label": 1},
        {"text": "We noticed suspicious activity on your Apple ID. Verify your credentials.", "label": 1},
        {"text": "Action Required: Your Amazon account is on hold. Update billing info.", "label": 1},
        {"text": "Dear customer, your PayPal transaction was declined. Confirm identity.", "label": 1},
        {"text": "Netflix: Your payment failed. Please update your payment method to continue watching.", "label": 1},
        {"text": "Important Message from IT Helpdesk: Migrate to the new Outlook portal.", "label": 1},
        {"text": "Your WhatsApp account will be deleted. Click here to cancel.", "label": 1},
        {"text": "Security Alert: Someone requested a password reset for your account.", "label": 1},
        {"text": "Claim your $500 Amazon Gift Card by completing this survey.", "label": 1},
        {"text": "You have 1 pending voice message. Click to listen.", "label": 1},
    ]
    
    df = pd.DataFrame(data)
    
    # Save dataset
    os.makedirs('../../datasets', exist_ok=True)
    df.to_csv('../../datasets/phishing_data.csv', index=False)
    
    # 2. Train ML Model (TF-IDF + Logistic Regression)
    X = df['text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', max_features=1000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    model = LogisticRegression(C=1.0)
    model.fit(X_train_tfidf, y_train)
    
    # 3. Evaluate
    y_pred = model.predict(X_test_tfidf)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    # 4. Save models
    os.makedirs('app/ml', exist_ok=True)
    joblib.dump(vectorizer, 'app/ml/vectorizer.pkl')
    joblib.dump(model, 'app/ml/model.pkl')
    
    print("Model Training Complete!")
    print(f"Accuracy: {report['accuracy']:.2f}")
    if '1' in report:
        print(f"Phishing Precision: {report['1']['precision']:.2f}")
        print(f"Phishing Recall: {report['1']['recall']:.2f}")

if __name__ == "__main__":
    generate_and_train()
