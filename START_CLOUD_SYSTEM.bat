@echo off
title Phishing Shield AI - Cloud & Local Launcher
echo ======================================================================
echo             PHISHING SHIELD AI - SYSTEM LAUNCHER
echo ======================================================================
echo.
echo [1/2] Starting Python FastAPI Backend Engine on http://127.0.0.1:8000...
start "Phishing Shield Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Cloudflare HTTPS Public Cloud Tunnel...
start "Phishing Shield Cloud Tunnel" cmd /k "cd /d "%~dp0" && .\cloudflared.exe tunnel --url http://127.0.0.1:8000"

echo.
echo ======================================================================
echo  Both Backend and Cloud Tunnel are now ACTIVE!
echo  The Cloud Tunnel allows the Chrome Extension to work on ANY LAPTOP.
echo  Keep the two opened console windows open while running tests.
echo ======================================================================
echo.
pause
