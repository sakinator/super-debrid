@echo off
title Super Debrid - 100%% Free Debrid Gateway
cd /d "%~dp0"

echo ========================================================
echo    SUPER DEBRID - 100%% FREE DEBRID & LEECH GATEWAY
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Creating .venv...
    python -m venv .venv
    echo [*] Installing dependencies...
    .venv\Scripts\pip.exe install -r requirements.txt
)

echo [*] Launching Super Debrid on http://127.0.0.1:7070 ...
.venv\Scripts\python.exe main.py
pause
