@echo off
setlocal enabledelayedexpansion

echo =========================================
echo        PHISHING SHIELD AI
echo =========================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)
echo [OK] Python is installed.

:: 2. Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b
)
echo [OK] Node.js is installed.

:: 3. Check npm
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed or not in PATH.
    pause
    exit /b
)
echo [OK] npm is installed.
echo.

echo Starting services...
echo.

echo Backend:
echo http://127.0.0.1:8000
echo.
echo API Docs:
echo http://127.0.0.1:8000/docs
echo.
echo Frontend:
echo http://127.0.0.1:5176
echo.
echo =========================================

:: Start backend
echo Starting FastAPI Backend...
start "Phishing Shield Backend" cmd /k "cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Start frontend
echo Starting React Frontend...
start "Phishing Shield Frontend" cmd /k "cd frontend && npm run dev -- --port 5176"

echo.
echo [INFO] Close the launched windows to stop the servers.
pause
