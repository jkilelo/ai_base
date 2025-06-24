@echo off
REM AI Base Platform - Quick Setup with UV (Batch)
REM Enforces Python 3.12+ and uses UV for fast dependency management

echo ========================================
echo AI Base Platform - Quick Setup
echo Python 3.12+ Required
echo ========================================

REM Function to check Python version
set "PYTHON_CMD="
set "PYTHON_FOUND=0"

echo [1/5] Checking for Python 3.12+...
REM Try different Python commands
for %%p in (python3.12 python3.13 python3.14 python py) do (
    %%p --version 2>nul | findstr /R "Python 3\.1[2-9]\|Python 3\.[2-9][0-9]" >nul
    if not errorlevel 1 (
        set "PYTHON_CMD=%%p"
        set "PYTHON_FOUND=1"
        echo [✓] Found valid Python: %%p
        %%p --version
        goto :python_found
    )
)

:python_found
if "%PYTHON_FOUND%"=="0" (
    echo [ERROR] Python 3.12+ not found!
    echo.
    echo Please install Python 3.12+ from https://python.org
    echo Make sure to add Python to your PATH during installation
    echo.
    echo Currently available Python versions:
    for %%p in (python py python3) do (
        echo   Checking %%p:
        %%p --version 2>nul || echo     Not found
    )
    echo.
    pause
    exit /b 1
)

REM Check for UV
echo.
echo [2/5] Checking for UV package manager...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [!] UV not found. Installing UV...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if errorlevel 1 (
        echo [ERROR] Failed to install UV
        echo Please install manually: https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    echo [✓] UV installed successfully
) else (
    echo [✓] UV found
    uv --version
)

REM Remove old environments
echo.
echo [3/5] Checking for old Python environments...
if exist ".venv\" (
    echo Found existing .venv directory. Checking Python version...
    .venv\Scripts\python.exe --version 2>nul | findstr /R "Python 3\.1[2-9]\|Python 3\.[2-9][0-9]" >nul
    if errorlevel 1 (
        echo [!] Removing old Python environment (< 3.12)...
        rmdir /s /q ".venv"
        echo [✓] Old environment removed
        set "NEED_NEW_VENV=1"
    ) else (
        echo [✓] Existing environment uses Python 3.12+, keeping it
        set "NEED_NEW_VENV=0"
    )
) else (
    set "NEED_NEW_VENV=1"
)

REM Check for conda environments
conda env list 2>nul | findstr "ai-base" >nul
if not errorlevel 1 (
    echo Found conda ai-base environment. Checking if it needs removal...
    conda run -n ai-base python --version 2>nul | findstr /R "Python 3\.1[2-9]\|Python 3\.[2-9][0-9]" >nul
    if errorlevel 1 (
        echo [!] Removing old conda ai-base environment...
        conda env remove -n ai-base -y >nul 2>&1
        echo [✓] Old conda environment removed
    )
)

REM Create virtual environment if needed
if "%NEED_NEW_VENV%"=="1" (
    echo.
    echo [4/5] Creating virtual environment with Python 3.12+...
    uv venv .venv --python %PYTHON_CMD%
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [✓] Virtual environment created
) else (
    echo.
    echo [4/5] Using existing virtual environment
)

REM Install dependencies
echo.
echo [5/5] Installing dependencies with UV...
uv pip install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Install development dependencies
echo Installing development dependencies...
uv pip install -e ".[dev,test]"
if errorlevel 1 (
    echo [WARNING] Failed to install development dependencies
)

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
if errorlevel 1 (
    echo [WARNING] Failed to install Playwright browsers
)

REM Copy environment template if .env doesn't exist
if not exist .env (
    if exist .env.template (
        echo Creating .env file from template...
        copy .env.template .env
        echo [✓] .env file created from template
    )
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the backend server:
echo   start_backend.bat
echo.
echo To activate the environment manually:
echo   .venv\Scripts\activate
echo.
echo Python version in environment:
.venv\Scripts\python.exe --version
echo.
echo UV version:
uv --version
echo.
pause
