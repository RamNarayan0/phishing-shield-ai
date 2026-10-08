@echo off
echo ===================================================
echo     PACKAGING PROJECT FOR USB / DRIVE TRANSFER
echo ===================================================
echo.
echo Cleaning up heavy folders (node_modules, pycache)...
echo This makes the zip file small enough to easily share.
echo.

tar.exe -a -c -f Phishing_Shield_AI_Project.zip --exclude=node_modules --exclude=.venv --exclude=__pycache__ --exclude=.git *

echo.
echo [SUCCESS] Created Phishing_Shield_AI_Project.zip!
echo.
echo You can now copy this zip file to your USB drive or upload it to Google Drive.
pause
