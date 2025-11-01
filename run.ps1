# Activate venv (if not already active) and launch server
if (-not (Test-Path .venv)) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements-py313.txt
python app/server.py
