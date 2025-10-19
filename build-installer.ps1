# Abeka Junction Traffic Dashboard Windows Installer Builder
# PowerShell script to create professional Windows installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Abeka Junction Traffic Dashboard" -ForegroundColor Cyan
Write-Host "  Windows Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = [bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544")
if (-not $isAdmin) {
    Write-Host "ERROR: Please run this script as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    exit 1
}

# Check prerequisites
Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Yellow

$pythonCheck = python --version 2>&1
if (-not $pythonCheck) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Python found: $pythonCheck" -ForegroundColor Green

$npmCheck = npm --version 2>&1
if (-not $npmCheck) {
    Write-Host "ERROR: Node.js/npm is not installed" -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ npm found: $npmCheck" -ForegroundColor Green

# Install PyInstaller if needed
Write-Host "[2/5] Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller -q
Write-Host "✓ PyInstaller ready" -ForegroundColor Green

# Build React Frontend
Write-Host "[3/5] Building React frontend..." -ForegroundColor Yellow
cd frontend
npm install --legacy-peer-deps -q
npm run build -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed" -ForegroundColor Red
    exit 1
}
cd ..
Write-Host "✓ Frontend built" -ForegroundColor Green

# Build Python Backend
Write-Host "[4/5] Building Python backend..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt -q
cd ..
pyinstaller build_windows.spec -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend compiled to exe" -ForegroundColor Green

# Build NSIS Installer
Write-Host "[5/5] Building Windows installer..." -ForegroundColor Yellow

# Check if NSIS is installed
$nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
if (-not (Test-Path $nsisPath)) {
    Write-Host "WARNING: NSIS not found at $nsisPath" -ForegroundColor Yellow
    Write-Host "Download and install from: https://nsis.sourceforge.io" -ForegroundColor Yellow
    Write-Host "After installing, run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or manually create installer with:" -ForegroundColor Cyan
    Write-Host "  makensis.exe installer.nsi" -ForegroundColor Cyan
    exit 0
}

& $nsisPath installer.nsi
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Windows installer created!" -ForegroundColor Green
} else {
    Write-Host "ERROR: NSIS installer creation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installer created:" -ForegroundColor Yellow
Write-Host "  Abeka-Junction-Traffic-Dashboard-Setup.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation location:" -ForegroundColor Yellow
Write-Host "  $env:ProgramFiles\Abeka Junction Traffic Dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  ✓ Start Menu shortcuts" -ForegroundColor Green
Write-Host "  ✓ Desktop shortcut" -ForegroundColor Green
Write-Host "  ✓ Windows uninstaller" -ForegroundColor Green
Write-Host "  ✓ Automatic launch on run" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to distribute!" -ForegroundColor Green
Write-Host ""
