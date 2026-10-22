# PHISHING SHIELD AI

**Real-Time AI-Powered Threat Detection**

A cross-platform phishing detection ecosystem prototype.

## Overview
Phishing Shield AI analyzes suspicious messages and URLs, calculates a threat score, explains WHY something is suspicious, and provides an immediate visual warning.

## Cloud Deployment Links

* **Live Frontend Dashboard**: [https://ramnarayan0.github.io/phishing-shield-ai/](https://ramnarayan0.github.io/phishing-shield-ai/)
* **GitHub Repository**: [https://github.com/RamNarayan0/phishing-shield-ai](https://github.com/RamNarayan0/phishing-shield-ai)
* **Chrome Extension Release (v1.0.0 ZIP)**: [https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip](https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip)
* **Full Deployment Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md) (Render Backend + Vercel / GitHub Pages + Chrome Web Store)

## Architecture
- **Backend**: FastAPI (Python) - Analyzes text, URLs, phone numbers, sender domains, and calculates risk scores using trained ML models (`model.pkl`, `phone_pattern_model.pkl`, `email_pattern_model.pkl`).
- **Frontend**: React + Vite + Tailwind CSS - A professional live security dashboard.
- **Chrome Extension**: Manifest V3 - Scans web pages for suspicious content with dual Cloud/Local backend support.
- **Master Dataset**: 29,113 cleaned Kaggle phishing records across SMS, Email, and URLs.

## Installation & Running

### 1. Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*The API will run at http://localhost:8000*
*Swagger UI is available at http://localhost:8000/docs*

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
*The dashboard will run at http://localhost:3000*

### 3. Chrome Extension
1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable "Developer mode" in the top right.
4. Click "Load unpacked" in the top left.
5. Select the `chrome-extension` folder in this repository.

## Features
- **Deterministic Security Heuristics**: Analyzes urgency, financial manipulation, and credential harvesting attempts.
- **URL Analysis**: Checks for suspicious structures, IP addresses, typosquatting patterns, and excessive subdomains.
- **Explainable Verdicts**: Provides a concrete list of reasons for why a message was flagged.
- **Real-Time Browser Protection**: Chrome extension dynamically analyzes page content.

## Demo Scenarios
The frontend includes built-in demo scenarios:
1. **Safe Message**: Everyday conversation.
2. **Suspicious Message**: Vague verification request.
3. **Phishing Link**: Urgent bank suspension with a typosquatted link.

## Privacy Notice
Prototype Privacy Notice: Message content is processed for threat analysis. Do not submit real passwords, OTPs, banking credentials, or other sensitive personal information during testing.

## Future Scope
- Integration with external threat intelligence APIs.
- Fine-tuned NLP models for better text classification.
- Android application for SMS and Notification scanning.
