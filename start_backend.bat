@echo off
REM AI Base Platform - Start Backend Server
REM Uses UV and enforces Python 3.12+

echo ===================================
echo AI Base Platform - Starting Backend
echo ===================================

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check Python version in venv
echo Checking Python version in virtual environment...
.venv\Scripts\python.exe --version 2>nul | findstr /R "Python 3\.1[2-9]\|Python 3\.[2-9][0-9]" >nul
if errorlevel 1 (
    echo [ERROR] Virtual environment does not use Python 3.12+
    echo Please run setup.bat to recreate the environment
    pause
    exit /b 1
)

echo [✓] Python 3.12+ confirmed in virtual environment
.venv\Scripts\python.exe --version

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV not found. Please install UV or run setup.bat
    pause
    exit /b 1
)

REM Start the server
echo.
echo Starting AI Base Platform backend server...
echo Server will be available at: http://localhost:8000
echo API documentation will be available at: http://localhost:8000/docs
echo Interactive API docs: http://localhost:8000/redoc
echo.

uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
