@echo off
cd /d %~dp0
if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)
echo Installing dependencies...
.venv\Scripts\python -m pip install -q fastapi uvicorn numpy opencv-python Pillow python-multipart
echo Starting server at http://localhost:8000
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
