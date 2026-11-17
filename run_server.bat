@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Create the environment first: py -3 -m venv .venv
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m uvicorn server.app:app --host 0.0.0.0 --port 8000
pause
