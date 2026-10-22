# Phishing Shield AI - Safe One-Command Installer & Tailscale Guide

## 1. Overview
The `install.ps1` script is a safe, zero-privilege PowerShell installer for the **Phishing Shield AI** Manifest V3 Chrome Extension. It is designed for multi-laptop deployment (connecting a second laptop to your running backend engine).

### Security Invariants Followed
- **No Administrator Rights**: Runs entirely within user space (`$env:LOCALAPPDATA\PhishingShieldAI`).
- **No Security Downgrades**: Antivirus, Windows Defender, and Chrome security settings are **never** modified or disabled.
- **No Silent Bypasses**: Adheres to Google Chrome's native security model. Chrome is opened to `chrome://extensions/` with the target directory copied to the clipboard for a 3-click manual load (`Developer mode` -> `Load unpacked` -> `Ctrl + V`).
- **File Validation**: Validates `manifest.json`, `manifest_version: 3`, `background.js`, `popup.html`, `popup.js`, and `config.json` before proceeding.

---

## 2. Connecting to Backend via Tailscale (Multi-Laptop Setup)

Tailscale provides a secure, encrypted mesh network allowing any secondary laptop to reach your backend machine directly without port forwarding or exposing ports to the public internet.

### Step-by-Step Tailscale Connection:
1. **Install Tailscale** on both laptops:
   - Download: [https://tailscale.com/download](https://tailscale.com/download)
   - Sign in to the same Tailscale account on both machines.

2. **Obtain Host Tailscale IP**:
   - On the laptop running the FastAPI backend (`uvicorn app.main:app`), open a terminal and run:
     ```bash
     tailscale ip -4
     ```
   - Note the assigned IP (e.g., `100.85.120.45`).

3. **Verify Host Backend Binding**:
   - Ensure your backend on the host machine is listening on all interfaces (`0.0.0.0` or your Tailscale IP):
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```

4. **Run the Installer on the Second Laptop**:
   - In PowerShell, run:
     ```powershell
     powershell -ExecutionPolicy Bypass -File .\install.ps1 -BackendUrl "http://<tailscale-ip>:8000"
     ```
     *(Example: `powershell -ExecutionPolicy Bypass -File .\install.ps1 -BackendUrl "http://100.85.120.45:8000"`)*
   - The installer validates the URL, writes `config.json`, copies the extension to `%LOCALAPPDATA%\PhishingShieldAI`, and opens Chrome.
   - When loaded, the extension displays a green **Tailscale** badge in the popup header.

---

## 3. Installer Commands & Parameters

### Local Interactive Run:
Prompts for Tailscale IP or Cloud backend URL:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Direct Tailscale / Remote Backend:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -BackendUrl "http://100.85.120.45:8000"
```

### Non-Interactive (Automated Testing / Defaults):
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NonInteractive
```

### Clean Uninstallation:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
```

---

## 4. How to Host & Publish

### Publishing Configuration:
- **Repository**: `https://github.com/RamNarayan0/phishing-shield-ai`
- **Release ZIP**: `https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip`
- **Installer Script Web URL**: `https://raw.githubusercontent.com/RamNarayan0/phishing-shield-ai/main/install.ps1` or GitHub Pages.

### One-Line Remote Execution (After Publishing):
```powershell
irm https://raw.githubusercontent.com/RamNarayan0/phishing-shield-ai/main/install.ps1 | iex
```
