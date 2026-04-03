# Run EternalBots Pope Francis (Upgraded) using eternal311 conda env
# This script uses Python 3.11 which is required for XTTS-v2 voice cloning

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EternalBots - Pope Francis AI (v2)" -ForegroundColor Cyan
Write-Host "  Powered by XTTS-v2 + SadTalker + Groq" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate conda eternal311 env (Python 3.11)
$condaPath = "C:\Users\micro\miniconda3"
$envPath = "$condaPath\envs\eternal311"

if (-not (Test-Path $envPath)) {
    Write-Host "ERROR: eternal311 conda env not found at $envPath" -ForegroundColor Red
    exit 1
}

Write-Host "Activating eternal311 conda env (Python 3.11)..." -ForegroundColor Yellow
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
& "$envPath\python.exe" app/server.py

