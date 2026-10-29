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

## Database & Persistence (MongoDB)

Phishing Shield AI supports both local MongoDB on Windows and MongoDB Atlas cloud clusters. If MongoDB is unavailable, the application gracefully falls back to an in-memory threat store so analysis and verdicts are never interrupted.

### Local Windows MongoDB (Default)
By default, the backend connects to your locally installed MongoDB server:
```env
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=phishing_shield_ai
MONGODB_COLLECTION=analysis_history
```

To verify local MongoDB on Windows:
```powershell
Get-Service *MongoDB*
```
If the service is stopped, start it in an elevated terminal:
```powershell
Start-Service MongoDB
```

### MongoDB Atlas (Alternative)
Set your Atlas connection string in `backend/.env`:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
```

### Duplicate Prevention & Indexing
- **Deterministic Fingerprinting**: Incoming messages are normalized (whitespace collapsed, lowercased, sender and source included) and hashed using **SHA-256**.
- **Unique Database Index**: A unique index on `fingerprint` guarantees database-level uniqueness and prevents race conditions under concurrent requests.
- **Atomic Upsert**: Repeated submissions are idempotent—they increment `duplicate_count` and update `last_seen_at` without polluting the database with duplicate rows.

### Duplicate Audit & Cleanup Tool
To safely audit existing records without deleting data (Dry Run):
```bash
python cleanup_duplicates.py --dry-run
```
To purge redundant historical duplicates and retain the canonical record:
```bash
python cleanup_duplicates.py --apply
```

## Security Hardening
- **Strict Input Validation**: Pydantic models reject oversized submissions (max 50,000 characters) and disallow MongoDB operator injection patterns (e.g. `$where`).
- **Request Size Limiting**: `ContentLengthLimitMiddleware` enforces a 256 KB payload cap (HTTP 413).
- **Rate Limiting**: Sliding-window rate limiter prevents abuse (default: 60 req/min per IP, HTTP 429).
- **Protective Security Headers**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and strict referrer policy.
- **Administrative Endpoint Protection**: Optional `ADMIN_API_KEY` locks down history and cleanup endpoints (`X-API-Key` required).
- **Safe Error Responses**: Sensitive database credentials, internal paths, and stack traces are suppressed in API error responses.

## Privacy Notice
Prototype Privacy Notice: Message content is processed for threat analysis. Do not submit real passwords, OTPs, banking credentials, or other sensitive personal information during testing.

## Future Scope
- Integration with external threat intelligence APIs (VirusTotal, Google Safe Browsing).
- Fine-tuned transformer models (DistilBERT/RoBERTa) for contextual zero-shot threat classification.
- Automated incident response webhook integrations for enterprise SIEM/SOAR platforms.
