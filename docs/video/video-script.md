# Phishing Shield AI - Demonstration Video Script

## 0:00–0:20 | Project introduction
*Visual: Title Slide of PPT.*
"Welcome. Today we present Phishing Shield AI, a multi-channel phishing detection prototype. Our goal is to secure communications across the web and mobile."

## 0:20–0:50 | Problem statement
*Visual: Problem statement slide.*
"Phishing attacks don't just happen via email anymore. They happen on WhatsApp, SMS, and malicious web links. Users often lack the technical expertise to spot these threats."

## 0:50–1:20 | Architecture
*Visual: Architecture Slide.*
"Our solution is an intelligent backend built with FastAPI, connected to a React frontend, a Chrome Extension, and an Android scaffold. It uses a hybrid detection engine combining Machine Learning and deterministic security heuristics."

## 1:20–2:00 | Safe message test
*Visual: React Dashboard.*
"Let's see it in action. Here we paste a safe, everyday message into the analyzer... The AI correctly identifies the conversational context and returns a 0 risk score. It is classified as SAFE."

## 2:00–2:50 | Phishing message test
*Visual: React Dashboard - Bank Phishing Scenario.*
"Now let's test a malicious payload simulating a bank suspension alert. As you can see, the Risk Engine immediately flags it as CRITICAL with a score above 90."

## 2:50–3:40 | Explain risk calculation
*Visual: Verdict detail view in Dashboard.*
"Notice the explainability. The system doesn't just say 'bad'. It explicitly lists the detected signals: urgency, financial context, credential requests, and suspicious URL paths. It combined a TF-IDF Machine Learning prediction with deterministic URL parsing."

## 3:40–4:20 | Chrome extension demonstration
*Visual: Chrome Browser with extension popup.*
"This same intelligence extends to the browser. Using Manifest V3, our Chrome extension scans the active tab's DOM and communicates with the same backend API to warn users before they click malicious links."

## 4:20–5:00 | Android notification concept/demo
*Visual: Android Readme / Architecture.*
"For mobile, we engineered an Android architecture leveraging the NotificationListenerService. This intercepts WhatsApp or SMS notifications, extracts the text, and queries our API without requiring intrusive database decryption."

## 5:00–5:40 | Technology stack + ML
*Visual: ML / Tech Stack Slides.*
"Under the hood, we use Python, React, and scikit-learn. The ML pipeline utilizes TF-IDF vectorization and Logistic Regression for highly efficient, lightweight inference, achieving a perfect baseline on our synthetic dataset."

## 5:40–6:00 | Conclusion
*Visual: Final slide.*
"Phishing Shield AI demonstrates how multi-channel AI threat detection can be achieved efficiently. Thank you."
