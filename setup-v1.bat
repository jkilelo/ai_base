@echo off
REM AI Base Project v1 - Environment Setup Script (UV-based)
REM Sets up Python 3.12+ with UV, Node.js, and all dependencies for v1

echo.
echo ========================================
echo   AI Base Project v1 - Setup (UV)
echo ========================================
echo.
echo Tech Stack:
echo   - Python 3.12+ ^& FastAPI (UV-managed)
echo   - React.js 19.1 ^& Bootstrap 5.3
echo   - SQLite3 / PostgreSQL 17 / MongoDB
echo.

REM Change to project root
cd /d "%~dp0"

REM Check Python installation
echo [1/6] Checking Python 3.12+ installation...
python --version 2>nul | findstr /C:"3.12" >nul
if errorlevel 1 (
    python --version 2>nul | findstr /C:"3.1" >nul
    if errorlevel 1 (
        echo [ERROR] Python 3.12+ not found!
        echo Please install Python 3.12+ from https://python.org
        pause
        exit /b 1
    ) else (
        echo [WARNING] Python version may be compatible, continuing...
    )
) else (
    echo [✓] Python 3.12+ found
)

REM Check Node.js installation
echo.
echo [2/6] Checking Node.js installation...
node --version 2>nul | findstr /C:"v22" >nul
if errorlevel 1 (
    node --version 2>nul
    echo [WARNING] Node.js 22.16+ recommended but will continue...
) else (
    echo [✓] Node.js 22.16+ found
)

REM Set up shared configuration
echo.
echo [3/6] Setting up shared configuration...
if not exist "config\" mkdir config
if not exist "shared\" mkdir shared
if not exist "databases\" mkdir databases
if not exist "docs\" mkdir docs
echo [✓] Directory structure verified

REM Check for .env file
echo.
echo [4/6] Checking environment configuration...
if not exist ".env" (
    if exist ".env.template" (
        copy ".env.template" ".env" >nul
        echo [✓] Created .env from template
        echo [!] Please review and update .env with your specific settings
    ) else (
        echo [ERROR] No .env or .env.template found!
        exit /b 1
    )
) else (
    echo [✓] Environment file exists
)

REM Copy .env to v1
copy ".env" "v1\.env" >nul 2>nul
if exist "v1\frontend\" copy ".env" "v1\frontend\.env" >nul 2>nul

REM Set up v1 backend with UV
echo.
echo [5/6] Setting up v1 backend with UV...
if exist "v1\backend\" (
    cd v1\backend
    
    REM Run the v1 setup script
    if exist "setup.bat" (
        call setup.bat
        echo [✓] v1 backend setup completed with UV
    ) else (
        echo [ERROR] v1\backend\setup.bat not found!
        echo Please ensure v1 backend is properly configured
    )
    
    cd ..\..
) else (
    echo [ERROR] v1\backend directory not found!
    exit /b 1
)

REM Install Node.js dependencies for v1
echo.
echo [6/6] Installing Node.js dependencies for v1...
if exist "v1\frontend\package.json" (
    echo Installing Node.js packages for v1/frontend...
    cd v1\frontend
    npm install
    echo [✓] Installed frontend dependencies for v1
    cd ..\..
) else (
    echo [WARNING] v1\frontend\package.json not found, skipping frontend setup
)

REM Final setup
echo.
echo ========================================
echo          v1 Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo   1. Review .env file and update as needed
echo   2. Start v1 development environment:
echo      - Backend:  cd v1\backend ^&^& start_backend.bat
echo      - Frontend: cd v1\frontend ^&^& npm start
echo   3. Or use: project-manager.bat for interactive management
echo.
echo Development URLs:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Database Setup:
echo   SQLite:     Automatic (./databases/ai_base.db)
echo   PostgreSQL: Manual setup required
echo   MongoDB:    Manual setup required
echo.
pause
