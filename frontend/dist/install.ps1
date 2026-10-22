# Phishing Shield AI - 1-Click Free Chrome Extension Installer
Write-Host "Installing Phishing Shield AI Chrome Extension (100% Free)..." -ForegroundColor Cyan

$installDir = "$env:LOCALAPPDATA\PhishingShieldAI"
$zipPath = "$env:TEMP\phishing-shield-ai.zip"
$downloadUrl = "https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip"

if (Test-Path $installDir) {
    Remove-Item $installDir -Recurse -Force
}
New-Item -ItemType Directory -Path $installDir -Force | Out-Null

Write-Host "Downloading latest extension package..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

Write-Host "Extracting extension..." -ForegroundColor Yellow
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath -Force

Write-Host "`nInstallation Complete! Phishing Shield AI is installed at: $installDir" -ForegroundColor Green
Write-Host "`nLaunching Chrome with Phishing Shield AI..." -ForegroundColor Cyan

$chromePath = (Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe' -ErrorAction SilentlyContinue).'(default)'
if (-not $chromePath) {
    $chromePath = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
}
if (-not (Test-Path $chromePath)) {
    $chromePath = "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe"
}

if (Test-Path $chromePath) {
    Start-Process $chromePath -ArgumentList "--load-extension=`"$installDir`"", "https://ramnarayan0.github.io/phishing-shield-ai/"
    Write-Host "Chrome launched with Phishing Shield AI active! Look for the shield icon in your Chrome toolbar." -ForegroundColor Green
} else {
    Write-Host "Chrome not found at standard path. You can load unpacked from: $installDir" -ForegroundColor Yellow
}
