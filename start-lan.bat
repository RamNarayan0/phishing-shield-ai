@echo off
setlocal enabledelayedexpansion

echo =========================================
echo    PHISHING SHIELD AI - LAN MODE
echo =========================================
echo.

:: Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP: =!
)

if "%IP%"=="" (
    echo [ERROR] Could not detect LAN IP Address. Defaulting to 127.0.0.1
    set IP=127.0.0.1
)

echo Your LAN IP:
echo %IP%
echo.
echo Backend:
echo http://%IP%:8000
echo.
echo Frontend:
echo http://%IP%:5173
echo.
echo API Docs:
echo http://%IP%:8000/docs
echo.
echo Instruct your friend to connect to the Same Wi-Fi and open the Frontend URL above.
echo =========================================

:: Start backend
echo Starting FastAPI Backend...
start "Phishing Shield Backend (LAN)" cmd /k "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Start frontend
echo Starting React Frontend...
start "Phishing Shield Frontend (LAN)" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo [INFO] Close the launched windows to stop the servers.
pause
