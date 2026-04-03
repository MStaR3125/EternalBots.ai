# Quick start script for EternalBots Pope Francis AI
Write-Host "🕊️ Starting EternalBots Pope Francis AI Server..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Start the server
Write-Host "Starting Gradio server..." -ForegroundColor Yellow
Write-Host "The server will be available at: http://127.0.0.1:7861" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python app\server.py
