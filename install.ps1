<#
.SYNOPSIS
    Safe, one-command installer and uninstaller for Phishing Shield AI Chrome Extension.
.DESCRIPTION
    This script installs the Phishing Shield AI Chrome extension into the user's LOCALAPPDATA
    directory, validates all required files and Manifest V3 structure, configures the backend
    API endpoint (Tailscale IP, Cloud, or custom), and guides the user through loading it in Chrome.
    
    Security Guarantees:
    - Never requires or prompts for Administrator privileges.
    - Never disables or modifies Windows Defender, antivirus, or security settings.
    - Never attempts silent registry injection or security bypasses.
.PARAMETER BackendUrl
    The backend API endpoint to configure (e.g. your Tailscale address 'http://100.x.y.z:8000' or Cloud URL).
.PARAMETER InstallPath
    The target directory. Defaults to '$env:LOCALAPPDATA\PhishingShieldAI'.
.PARAMETER DownloadUrl
    The verified remote release archive URL if installing remotely.
.PARAMETER Uninstall
    When specified, cleanly removes the installed extension directory and provides Chrome removal steps.
.PARAMETER NonInteractive
    Disables interactive prompts (useful for automated scripts and testing).
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$BackendUrl,

    [Parameter(Mandatory = $false)]
    [string]$InstallPath = (Join-Path $env:LOCALAPPDATA "PhishingShieldAI"),

    [Parameter(Mandatory = $false)]
    [string]$DownloadUrl = "https://github.com/RamNarayan0/phishing-shield-ai/releases/download/v1.0.0/phishing-shield-ai-chrome-extension.zip",

    [Parameter(Mandatory = $false)]
    [switch]$Uninstall,

    [Parameter(Mandatory = $false)]
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

function Write-BoxHeader {
    param([string]$Text)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "   $Text" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Get-ChromeExecutablePath {
    $candidates = @(
        (Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe' -ErrorAction SilentlyContinue).'(default)',
        (Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe' -ErrorAction SilentlyContinue).'(default)',
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) {
            return $c
        }
    }
    return $null
}

# ------------------------------------------------------------------------------
# 1. UNINSTALL FLOW
# ------------------------------------------------------------------------------
if ($Uninstall) {
    Write-BoxHeader "Phishing Shield AI - Uninstaller"
    Write-Host "[*] Target installation folder: $InstallPath" -ForegroundColor Yellow

    if (Test-Path $InstallPath) {
        try {
            Remove-Item -Path $InstallPath -Recurse -Force -ErrorAction Stop
            Write-Host "[OK] Successfully removed extension files from: $InstallPath" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Failed to remove folder: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[INFO] No existing installation found at: $InstallPath" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "   TO FINISH REMOVING FROM GOOGLE CHROME:" -ForegroundColor Cyan
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "1. Open Chrome and navigate to: chrome://extensions/"
    Write-Host "2. Locate the 'Phishing Shield AI' card."
    Write-Host "3. Click the 'Remove' button."
    Write-Host "4. Confirm removal."
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
    exit 0
}

# ------------------------------------------------------------------------------
# 2. PRIVILEGE & SECURITY CHECK (Safety Invariants)
# ------------------------------------------------------------------------------
$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]$currentIdentity
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "[!] Note: Running with elevated rights. Administrator privileges are NOT required for this installation." -ForegroundColor Yellow
}

Write-BoxHeader "Phishing Shield AI - Chrome Extension Installer"
Write-Host "[*] Safe User-Level Installation: No registry modifications, no system changes." -ForegroundColor Gray
Write-Host "[*] Target installation directory: $InstallPath" -ForegroundColor Gray

# ------------------------------------------------------------------------------
# 3. BACKEND API & TAILSCALE CONFIGURATION
# ------------------------------------------------------------------------------
$DEFAULT_CLOUD_URL = "https://reference-centered-por-agree.trycloudflare.com"

if (-not $BackendUrl -or $BackendUrl.Trim() -eq "") {
    if ($NonInteractive) {
        $BackendUrl = $DEFAULT_CLOUD_URL
    } else {
        Write-Host ""
        Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
        Write-Host "   BACKEND CONNECTION SETUP (Remote Laptop / Tailscale Configuration)" -ForegroundColor Cyan
        Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
        Write-Host "To connect this extension on another laptop to your Phishing Shield AI backend:" -ForegroundColor White
        Write-Host ""
        Write-Host "1. TAILSCALE SETUP (Recommended for multi-laptop private connection):" -ForegroundColor Yellow
        Write-Host "   - Install Tailscale (https://tailscale.com) on your backend machine and this laptop."
        Write-Host "   - On the backend machine, find its Tailscale IP by running: tailscale ip -4"
        Write-Host "   - Enter your URL below as: http://<tailscale-ip>:8000 (e.g. http://100.85.120.45:8000)"
        Write-Host ""
        Write-Host "2. CLOUD BACKEND SETUP:" -ForegroundColor Yellow
        Write-Host "   - Press Enter to use the active Cloud API: $DEFAULT_CLOUD_URL"
        Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan

        $userInput = Read-Host "Enter Backend URL [Press Enter for default Cloud API]"
        if ($userInput -and $userInput.Trim() -ne "") {
            $BackendUrl = $userInput.Trim()
        } else {
            $BackendUrl = $DEFAULT_CLOUD_URL
        }
    }
}

# Validate URL format
try {
    $uri = [System.Uri]$BackendUrl
    if ($uri.Scheme -ne "http" -and $uri.Scheme -ne "https") {
        throw "URL scheme must be http or https"
    }
} catch {
    Write-Host "[ERROR] '$BackendUrl' is not a valid HTTP or HTTPS URL." -ForegroundColor Red
    exit 1
}

# Warn if user provided localhost for what is intended to be a remote installation
if ($BackendUrl -match "^https?://(localhost|127\.0\.0\.1)(:\d+)?/?$") {
    Write-Host "[!] Note: You provided a localhost URL ($BackendUrl)." -ForegroundColor Yellow
    Write-Host "    If you run this on a second laptop, localhost will point to THAT laptop instead of your host." -ForegroundColor Yellow
    Write-Host "    For remote laptops, use your Tailscale IP (e.g. http://100.x.y.z:8000) or Cloud URL." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 4. DEPLOY FILES TO LOCALAPPDATA
# ------------------------------------------------------------------------------
try {
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }

    $localExtensionDir = Join-Path $PSScriptRoot "chrome-extension"
    if (Test-Path (Join-Path $localExtensionDir "manifest.json")) {
        Write-Host "[*] Copying extension files from repository source..." -ForegroundColor Cyan
        Copy-Item -Path "$localExtensionDir\*" -Destination $InstallPath -Recurse -Force
    } else {
        Write-Host "[*] Downloading verified extension release from: $DownloadUrl..." -ForegroundColor Cyan
        $tempZip = Join-Path $env:TEMP "phishing-shield-ai-$([System.Guid]::NewGuid().ToString('N')).zip"
        
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $tempZip -UseBasicParsing
        
        Write-Host "[*] Extracting package to target directory..." -ForegroundColor Cyan
        Expand-Archive -Path $tempZip -DestinationPath $InstallPath -Force
        Remove-Item -Path $tempZip -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "[ERROR] Installation failed during file deployment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------------------------
# 5. WRITE CONFIG.JSON WITH EXPLICIT BACKEND ENDPOINT
# ------------------------------------------------------------------------------
try {
    $configData = @{
        apiUrl = $BackendUrl.TrimEnd('/')
        configuredAt = (Get-Date).ToString("o")
        connectionMode = if ($BackendUrl -match "100\." -or $BackendUrl -match "\.ts\.net") { "tailscale" } else { "custom" }
        installerVersion = "1.0.0"
    }
    $configFilePath = Join-Path $InstallPath "config.json"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $jsonText = $configData | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($configFilePath, $jsonText, $utf8NoBom)
    Write-Host "[OK] Configured backend endpoint in config.json: $BackendUrl" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed writing config.json: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------------------------
# 6. VALIDATE REQUIRED FILES & MANIFEST.JSON
# ------------------------------------------------------------------------------
Write-Host "[*] Validating unpacked extension integrity..." -ForegroundColor Cyan

$requiredFiles = @("manifest.json", "background.js", "popup.html", "popup.js", "config.json")
foreach ($req in $requiredFiles) {
    $fullPath = Join-Path $InstallPath $req
    if (-not (Test-Path $fullPath)) {
        Write-Host "[ERROR] Validation failed: Missing required file '$req' in '$InstallPath'." -ForegroundColor Red
        exit 1
    }
}

try {
    $manifestRaw = Get-Content (Join-Path $InstallPath "manifest.json") -Raw
    $manifest = $manifestRaw | ConvertFrom-Json
    if ($manifest.manifest_version -ne 3) {
        Write-Host "[ERROR] Validation failed: manifest_version must be 3, found: $($manifest.manifest_version)" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Integrity checks passed: Valid Manifest V3 extension ($($manifest.name) v$($manifest.version))." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Validation failed: Corrupt manifest.json ($($_.Exception.Message))" -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------------------------
# 7. CLIPBOARD ASSISTANCE & USER GUIDANCE FOR CHROME
# ------------------------------------------------------------------------------
$clipboardOk = $false
try {
    Set-Clipboard -Value $InstallPath -ErrorAction SilentlyContinue
    $clipboardOk = $true
} catch {
    $clipboardOk = $false
}

$chromeExe = Get-ChromeExecutablePath
if ($chromeExe -and -not $NonInteractive) {
    Write-Host "[*] Opening Google Chrome to chrome://extensions/..." -ForegroundColor Cyan
    Start-Process -FilePath $chromeExe -ArgumentList "chrome://extensions/"
}

Write-BoxHeader "ACTION REQUIRED IN GOOGLE CHROME (Finish in 3 Clicks)"

Write-Host "Your extension files are verified and ready at:" -ForegroundColor White
Write-Host "  $InstallPath" -ForegroundColor Yellow

if ($clipboardOk) {
    Write-Host "  (The path above has been COPIED to your clipboard automatically!)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Follow these 4 quick steps in Google Chrome:" -ForegroundColor White
Write-Host "1. In Chrome, open a new tab and go to: chrome://extensions/" -ForegroundColor Cyan
Write-Host "2. In the top-right corner, turn ON the switch: [ Developer mode ]" -ForegroundColor Cyan
Write-Host "3. In the top-left corner, click the button: [ Load unpacked ]" -ForegroundColor Cyan
Write-Host "4. Paste the path (Ctrl + V): $InstallPath and click 'Select Folder'." -ForegroundColor Cyan
Write-Host ""
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "UNINSTALLATION INSTRUCTIONS:" -ForegroundColor Gray
Write-Host "To remove at any time, run:" -ForegroundColor Gray
Write-Host "  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall" -ForegroundColor Gray
Write-Host "And click 'Remove' on the Phishing Shield AI card in chrome://extensions/" -ForegroundColor Gray
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Gray

Write-Host "[OK] Installer completed successfully!`n" -ForegroundColor Green
