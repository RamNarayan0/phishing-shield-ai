# Narration Track

**[0:00 - 0:20]**
"Welcome to the demonstration of Phishing Shield AI. Today, we are showcasing a prototype built to detect and explain phishing attempts across multiple platforms, beyond just traditional email."

**[0:20 - 0:50]**
"As you know, modern social engineering targets users on WhatsApp, SMS, and malicious web links. To combat this, we engineered an intelligent backend with a hybrid detection model."

**[0:50 - 1:20]**
"Here is the main dashboard. Let's start with a normal, safe message. When a user receives 'Hey, are you coming to college tomorrow?', the AI parses the intent, recognizes it as a benign conversational text, and returns a 0 risk score. It is completely safe."

**[1:20 - 2:00]**
"However, threats look different. Let's paste a simulated banking phishing attempt. The system immediately flags this as 'CRITICAL' with a 92% risk score."

**[2:00 - 2:50]**
"What makes this prototype unique is its explainability. Instead of a black-box 'Yes' or 'No', the Risk Engine details exactly *why* it's malicious. It detected urgent language, financial context, a credential request, and a suspicious URL pattern. This is powered by combining TF-IDF Machine Learning with deterministic security heuristics."

**[2:50 - 3:40]**
"We also have a Chrome Extension that acts as a browser safety net, scanning the active page's text and URLs, feeding them into the exact same FastAPI backend, providing seamless cross-platform security."

**[3:40 - 4:20]**
"Our Android architecture concept works similarly by using the NotificationListenerService to intercept incoming texts or WhatsApp messages, evaluating them without needing to aggressively scan the device's internal databases."

**[4:20 - 5:00]**
"To summarize, Phishing Shield AI provides a lightweight, real-time, and explainable line of defense against modern digital deception. Thank you for watching."
