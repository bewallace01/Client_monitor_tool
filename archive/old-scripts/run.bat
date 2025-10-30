@echo off
REM Quick launch script for Client Intelligence Monitor

echo Client Intelligence Monitor
echo ============================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>NUL
if errorlevel 1 (
    echo [ERROR] Dependencies not installed!
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "data\client_intelligence.db" (
    echo [INFO] No database found. Running seed script...
    python scripts\seed_data.py
    echo.
)

echo [INFO] Starting dashboard...
echo [INFO] Dashboard will open at http://localhost:8501
echo.
python -m streamlit run app.py
