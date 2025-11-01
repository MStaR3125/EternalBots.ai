@echo off
echo Starting EternalBots Pope Francis AI Server...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo.
echo Environment activated. Starting server...
echo.
python app\server.py
pause
