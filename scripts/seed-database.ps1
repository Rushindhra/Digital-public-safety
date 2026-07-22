@echo off
setlocal
cd /d "%~dp0..\backend"

call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
    echo Run scripts\start-backend.ps1 first to create the virtual environment.
    exit /b 1
)

python -m app.db.seed
echo Seed complete.
