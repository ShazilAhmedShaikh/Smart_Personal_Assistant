@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
TITLE J.A.R.V.I.S. Operating System - Online
COLOR 0B

echo ==============================================================
echo    STARK INDUSTRIES // J.A.R.V.I.S. LOCAL OPERATING SYSTEM
echo    Commander: Shazil Ahmed Shaikh ("Shaziii")
echo    Host: Dell Latitude 7420 (Windows 11 Pro)
echo ==============================================================
echo.
echo [1/3] Verifying Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH! Please ensure Python 3.10+ is installed.
    pause
    exit /b
)

echo [2/3] Initializing J.A.R.V.I.S. Core Kernel...
cd /d "%~dp0backend"

echo [3/3] Launching Local HUD on http://127.0.0.1:8000...
start "" "http://127.0.0.1:8000"

python main.py

pause
