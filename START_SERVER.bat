@echo off
title EternalBots Pope Francis Server
color 0A
echo.
echo ========================================
echo   EternalBots - Pope Francis AI
echo ========================================
echo.
echo Starting server...
echo.
echo Server will be available at:
echo http://127.0.0.1:7861
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app\server.py
pause
