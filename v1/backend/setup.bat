@echo off
setlocal enabledelayedexpansion
REM AI Base Project v1 - Python Environment Setup
REM This script sets up the Python environment using UV package manager

echo.
echo ========================================
echo   AI Base v1 - Python Setup
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0"

REM Set minimum required Python version
set MIN_PYTHON_MAJOR=3
set MIN_PYTHON_MINOR=12

echo [INFO] Setting up Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ environment with UV...

REM Check if UV is already installed
uv --version >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] UV is already installed
    for /f "tokens=*" %%i in ('uv --version') do echo   %%i
    goto :check_python_with_uv
)

echo [INFO] UV not found, installing UV...

REM Step 1: Check for Python 3.12+ first (preferred)
echo [INFO] Checking for Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+...

REM Method 1: Try Python Launcher with 3.12+
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('py -3.12 --version') do echo [SUCCESS] Found %%i via Python Launcher
    set PYTHON_CMD=py -3.12
    set HAS_MIN_PYTHON=1
    goto :install_uv
)

py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('py -3.13 --version') do echo [SUCCESS] Found %%i via Python Launcher
    set PYTHON_CMD=py -3.13
    set HAS_MIN_PYTHON=1
    goto :install_uv
)

REM Method 2: Check if default python is 3.12+
python --version 2>&1 | findstr /R /C:"Python 3\.1[2-9]" >nul
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('python --version') do echo [SUCCESS] Found %%i as default python
    set PYTHON_CMD=python
    set HAS_MIN_PYTHON=1
    goto :install_uv
)

REM Step 2: Look for any Python 3.x (fallback)
echo [WARNING] Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ not found, checking for any Python 3.x...

python --version 2>&1 | findstr /R /C:"Python 3\." >nul
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('python --version') do echo [SUCCESS] Found %%i (will install Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ via UV)
    set PYTHON_CMD=python
    set HAS_MIN_PYTHON=0
    goto :install_uv
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('py -3 --version') do echo [SUCCESS] Found %%i via launcher (will install Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ via UV)
    set PYTHON_CMD=py -3
    set HAS_MIN_PYTHON=0
    goto :install_uv
)

REM Step 3: No Python found at all
echo [ERROR] No Python 3.x installation found!
echo.
echo Python Installation Required:
echo   Option 1 - Official Installer:
echo     1. Download Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ from: https://www.python.org/downloads/
echo     2. Run installer and check "Add Python to PATH"
echo     3. Restart this terminal and run this script again
echo.
echo   Option 2 - Package Managers:
echo     • Microsoft Store: Search for "Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%"
echo     • Chocolatey: choco install python%MIN_PYTHON_MINOR%%MIN_PYTHON_MAJOR%
echo     • Winget: winget install Python.Python.%MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
echo.
echo   Option 3 - Install any Python 3.x, then run this script
echo     This script can use UV to install Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ automatically
echo.
pause
exit /b 1

:install_uv
echo [INFO] Installing UV using %PYTHON_CMD%...
%PYTHON_CMD% -m pip install uv
if errorlevel 1 (
    echo [ERROR] Failed to install UV
    echo.
    echo Troubleshooting:
    echo   1. Check internet connection
    echo   2. Try: %PYTHON_CMD% -m pip install --upgrade pip
    echo   3. Try: %PYTHON_CMD% -m pip install --user uv
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] UV installed successfully

REM Verify UV installation
uv --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] UV installed but not found in PATH
    echo [INFO] You may need to restart your terminal or add UV to PATH
    echo [INFO] Continuing with setup...
) else (
    for /f "tokens=*" %%i in ('uv --version') do echo [SUCCESS] UV verified: %%i
)

:check_python_with_uv
REM Step 4: Install Python 3.12+ with UV if needed
if "%HAS_MIN_PYTHON%"=="0" (
    echo [INFO] Installing Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% using UV...
    uv python install %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
    if errorlevel 1 (
        echo [ERROR] Failed to install Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% with UV
        echo.
        echo Troubleshooting:
        echo   1. Check internet connection
        echo   2. Try manually: uv python install %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
        echo   3. Check UV documentation: https://docs.astral.sh/uv/
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% installed via UV
) else (
    echo [INFO] Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%+ already available
)

REM Step 5: Set up virtual environment
echo [INFO] Setting up virtual environment...

REM Check if .venv directory exists (UV uses .venv by default)
if exist ".venv\" (
    echo [INFO] Found existing UV virtual environment, checking Python version...
    
    REM Check Python version in existing .venv
    .venv\Scripts\python.exe -c "import sys; exit(0 if sys.version_info >= (%MIN_PYTHON_MAJOR%, %MIN_PYTHON_MINOR%) else 1)" >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=*" %%i in ('.venv\Scripts\python.exe --version') do echo [SUCCESS] Existing .venv has %%i
        goto :install_dependencies
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
    echo.
    echo Troubleshooting:
    echo   1. Check if Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% is available: uv python list
    echo   2. Try: uv python install %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%
    echo   3. Try: uv venv --python python (use system Python)
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created with UV

REM Verify virtual environment
if exist ".venv\Scripts\python.exe" (
    for /f "tokens=*" %%i in ('.venv\Scripts\python.exe --version') do echo [SUCCESS] Virtual environment Python: %%i
) else (
    echo [WARNING] Virtual environment created but Python not found at expected location
)

:install_dependencies
REM Step 6: Install dependencies
echo [INFO] Installing dependencies with UV...

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [WARNING] requirements.txt not found
    echo [INFO] Skipping dependency installation
    goto :setup_complete
)

uv pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies with UV
    echo.
    echo Troubleshooting:
    echo   1. Check requirements.txt format
    echo   2. Try manually: uv pip install -r requirements.txt
    echo   3. Check individual packages in requirements.txt
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed with UV

:setup_complete
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Environment Summary:
if exist ".venv\Scripts\python.exe" (
    for /f "tokens=*" %%i in ('.venv\Scripts\python.exe --version') do echo   Python: %%i
) else (
    echo   Python: Not detected in .venv
)

uv --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('uv --version') do echo   UV: %%i
) else (
    echo   UV: Not in PATH (may need terminal restart)
)

echo   Virtual Environment: .venv
echo.
echo Next Steps:
echo   1. To activate the environment manually:
echo      .venv\Scripts\activate
echo.
echo   2. To start the development server:
echo      start_backend.bat
echo      or
echo      python start_dev_server.py
echo.
echo   3. To install additional packages:
echo      uv pip install package-name
echo.

pause
