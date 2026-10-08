@echo off
setlocal enabledelayedexpansion

echo =========================================
echo    PHISHING SHIELD AI - ENV CHECKER
echo =========================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [V] Python
) else (
    echo [X] Python - REQUIRED
)

:: 2. Check Node
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [V] Node
) else (
    echo [X] Node - REQUIRED
)

:: 3. Check npm
call npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [V] npm
) else (
    echo [X] npm - REQUIRED
)

:: 4. Check Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [V] Git
) else (
    echo [X] Git - REQUIRED
)

:: 5. Check Java (Optional for Android)
java -version >nul 2>&1
if %errorlevel% equ 0 (
    echo [V] Java (Android)
) else (
    echo [!] Java - OPTIONAL (Android)
)

echo.
echo Environment check complete!
pause
