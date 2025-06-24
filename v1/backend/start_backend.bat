@echo off
setlocal enabledelayedexpansion
REM AI Base Project v1 - FastAPI Backend Development Server
REM Windows batch script using UV for Python and package management

echo.
echo ========================================
echo   AI Base v1 - FastAPI Backend
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0"

REM Set minimum required Python version
set MIN_PYTHON_MAJOR=3
set MIN_PYTHON_MINOR=12

echo [INFO] Setting up Python environment with UV...

REM Check if UV is already installed
uv --version >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] UV is already installed
    goto :check_python_with_uv
)

echo [INFO] UV not found, installing UV...

REM Check for Python 3.12+ first (preferred)
echo [INFO] Checking for Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+...

REM Method 1: Try Python Launcher with 3.12
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Found Python 3.12+ via Python Launcher
    set PYTHON_CMD=py -3.12
    goto :install_uv
)

REM Method 2: Check if default python is 3.12+
python --version 2>&1 | findstr /R /C:"Python 3\.1[2-9]" >nul
if not errorlevel 1 (
    echo [SUCCESS] Found Python 3.12+ as default python
    set PYTHON_CMD=python
    goto :install_uv
)

REM Method 3: Check for any Python 3.x (fallback)
echo [WARNING] Python 3.12+ not found, checking for any Python 3.x...
python --version 2>&1 | findstr /R /C:"Python 3\." >nul
if not errorlevel 1 (
    echo [SUCCESS] Found Python 3.x, will use UV to install Python 3.12+
    set PYTHON_CMD=python
    set NEED_PYTHON_INSTALL=1
    goto :install_uv
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Found Python 3.x via launcher, will use UV to install Python 3.12+
    set PYTHON_CMD=py -3
    set NEED_PYTHON_INSTALL=1
    goto :install_uv
)

REM No Python found at all
echo [ERROR] No Python 3.x installation found!
echo.
echo Python Installation Required:
echo   1. Download Python 3.12+ from: https://www.python.org/downloads/
echo   2. Install with "Add Python to PATH" checked
echo   3. Restart this terminal
echo   4. Try running this script again
echo.
echo Quick Install Options:
echo   - Microsoft Store: Search for "Python 3.12"
echo   - Chocolatey: choco install python312
echo   - Winget: winget install Python.Python.3.12
echo.
pause
exit /b 1

:install_uv
echo [INFO] Installing UV using %PYTHON_CMD%...
%PYTHON_CMD% -m pip install uv
if errorlevel 1 (
    echo [ERROR] Failed to install UV
    pause
    exit /b 1
)
echo [SUCCESS] UV installed successfully

:check_python_with_uv
REM Check if we need to install Python 3.12+ using UV
if defined NEED_PYTHON_INSTALL (
    echo [INFO] Installing Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% using UV...
    uv python install %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
    if errorlevel 1 (
        echo [ERROR] Failed to install Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% with UV
        pause
        exit /b 1
    )
    echo [SUCCESS] Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% installed via UV
)

REM Check if .venv directory exists (UV uses .venv by default)
if exist ".venv\" (
    echo [INFO] Found existing UV virtual environment, checking Python version...
    
    REM Check Python version in existing .venv
    .venv\Scripts\python.exe -c "import sys; exit(0 if sys.version_info >= (%MIN_PYTHON_MAJOR%, %MIN_PYTHON_MINOR%) else 1)" >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] Existing .venv has Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+
        goto :activate_venv
    ) else (
        echo [WARNING] Existing .venv does not have Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+
        echo [INFO] Removing incompatible virtual environment...
        rmdir /s /q .venv
        echo [SUCCESS] Old virtual environment removed
    )
)

REM Create new virtual environment with UV
echo [INFO] Creating virtual environment with UV (Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+)...
uv venv --python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment with UV
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created with UV

:activate_venv
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

:install_dependencies
echo.
echo [INFO] Installing dependencies with UV...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies with UV
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Dependencies installed with UV
echo.

REM Create databases directory if it doesn't exist
if not exist "..\..\databases\" (
    mkdir "..\..\databases"
    echo [INFO] Created databases directory
)

echo ========================================
echo   Starting FastAPI Development Server
echo ========================================
echo.

REM Display connection info
echo Backend API:     http://127.0.0.1:8000
echo API Docs:        http://127.0.0.1:8000/docs
echo Health Check:    http://127.0.0.1:8000/api/v1/health
echo Detailed Health: http://127.0.0.1:8000/api/v1/health/detailed
echo.
echo Press Ctrl+C to stop the server
echo ----------------------------------------

REM Start the FastAPI server - try different ports if 8000 is busy
echo [INFO] Attempting to start server on port 8000...
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if errorlevel 1 (
    echo [WARNING] Port 8000 is busy, trying port 8001...
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
    if errorlevel 1 (
        echo [WARNING] Port 8001 is busy, trying port 8002...
        python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
        if errorlevel 1 (
            echo [ERROR] Could not start server on ports 8000-8002
            echo [INFO] Please check if another service is using these ports
            pause
            exit /b 1
        )
    )
)

echo.
echo [INFO] Server stopped
pause
