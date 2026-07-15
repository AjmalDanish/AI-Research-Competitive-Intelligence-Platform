@echo off
REM Installation and Test Script for AI Research Competitive Intelligence Platform
REM Run this in Windows Command Prompt or PowerShell

echo ============================================================
echo AI Research Competitive Intelligence Platform
echo Installation and Testing Script
echo ============================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python found!
echo.

REM Navigate to backend directory
echo [2/6] Navigating to backend directory...
cd /d D:\project\AI-Research-Competitive-Intelligence-Platform\backend
if errorlevel 1 (
    echo ERROR: Could not navigate to backend directory
    pause
    exit /b 1
)
echo Current directory: %CD%
echo.

REM Install minimal dependencies
echo [3/6] Installing minimal dependencies...
pip install fastapi uvicorn
echo.

REM Create minimal environment file
echo [4/6] Creating environment file...
echo DEBUG=True > .env
echo ENVIRONMENT=development >> .env
echo SECRET_KEY=test-secret-key-for-development >> .env
echo DATABASE_URL=sqlite+aiosqlite:///./test.db >> .env
echo Environment file created!
echo.

REM Run basic tests
echo [5/6] Running basic application tests...
python test_app.py
if errorlevel 1 (
    echo WARNING: Some tests failed, but continuing...
)
echo.

REM Start test server
echo [6/6] Starting minimal test server...
echo.
echo ============================================================
echo Server will start at: http://localhost:8000
echo Test endpoints:
echo   - Home: http://localhost:8000/
echo   - Health: http://localhost:8000/health  
echo   - Test: http://localhost:8000/test
echo   - API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python test_server.py

pause