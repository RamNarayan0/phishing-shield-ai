# Phishing Shield AI - Production Cloud Deployment Guide

This document outlines the step-by-step production deployment for all layers of **Phishing Shield AI**:

1. **GitHub Repository** (Source Code & Model Artifacts)
2. **Render Cloud** (FastAPI ML Backend Engine)
3. **Vercel Cloud** (React + Tailwind Dashboard)
4. **Google Chrome Extension** (Cloud-Connected Manifest V3 Client)

---

## 1. GitHub Repository

The entire codebase, verified datasets, and trained ML weights are published on GitHub:

* **Repository URL**: [https://github.com/RamNarayan0/phishing-shield-ai](https://github.com/RamNarayan0/phishing-shield-ai)
* **Default Branch**: `main`
* **Contents**:
  - `backend/`: FastAPI API, risk engine, detectors, and trained `.pkl` models
  - `frontend/`: React + Vite monitoring dashboard
  - `chrome-extension/`: Manifest V3 browser protection extension
  - `datasets/`: Master verified dataset (`dataset.csv`, 29,113 clean records)
  - `render.yaml`: Infrastructure as Code specification for Render

---

## 2. Render Deployment (Backend API)

The backend is configured via [`render.yaml`](./render.yaml) for automated deployment on Render.

### Steps to Deploy:
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Blueprint** (or **Web Service**).
3. Connect your GitHub account and select **`RamNarayan0/phishing-shield-ai`**.
4. Render will automatically detect `render.yaml` with the following configuration:
   * **Runtime**: Python 3.11.9
   * **Root Directory**: `backend`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Apply / Create Web Service**.
6. Your backend will be live at:
   ```
   https://phishing-shield-ai-backend.onrender.com
   ```
7. Verify health endpoint:
   ```
   GET https://phishing-shield-ai-backend.onrender.com/health
   Response: {"status": "ok"}
   ```

---

## 3. Frontend Dashboard Deployment (GitHub Pages & Vercel)

### Live GitHub Pages Dashboard (Active Now):
The frontend has been built and deployed live directly via GitHub Pages:
* **Live Dashboard URL**: [https://ramnarayan0.github.io/phishing-shield-ai/](https://ramnarayan0.github.io/phishing-shield-ai/)

### Vercel Deployment Option:
The frontend is also configured for zero-config static hosting with SPA rewrites via [`frontend/vercel.json`](./frontend/vercel.json).

#### Option A: Via Vercel Web Dashboard (1-Click Import)
1. Go to [https://vercel.com/new](https://vercel.com/new).
2. Click **Import** next to `RamNarayan0/phishing-shield-ai`.
3. In **Project Configuration**:
   * **Root Directory**: Click *Edit* and select **`frontend`**.
   * **Framework Preset**: Vite (detected automatically).
   * **Build Command**: `vite build`
   * **Output Directory**: `dist`
4. Under **Environment Variables**, add:
   * `VITE_API_URL` = `https://phishing-shield-ai-backend.onrender.com`
5. Click **Deploy**.

#### Option B: Via Vercel CLI
```bash
cd frontend
npx vercel --prod
```

---

## 4. Chrome Extension Cloud Deployment

The extension has been upgraded to Manifest V3 with dual-mode support (Cloud Production vs Local Development).

### Cloud Package & Release:
* **GitHub Release Page**: [https://github.com/RamNarayan0/phishing-shield-ai/releases/tag/v1.0.0](https://github.com/RamNarayan0/phishing-shield-ai/releases/tag/v1.0.0)
* **Direct Cloud ZIP Download**: [https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip](https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip)
* **Manifest Version**: 3
* **Host Permissions**: `<all_urls>`, `https://*.onrender.com/*`, `https://*.vercel.app/*`

### To Deploy to Chrome Web Store:
1. Go to the [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole).
2. Click **Add New Item**.
3. Upload the packaged archive: `dist/phishing-shield-ai-chrome-extension.zip` or download directly from GitHub Release.
4. Fill in description, screenshots, and privacy policy.
5. Click **Submit for Review**.

### To Install Locally for Testing:
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (top right toggle).
3. Click **Load unpacked** and select the `chrome-extension` folder.
4. Click the extension icon and select **Cloud Render Production** or **Local Dev Server**.
