@echo off
REM AI Base Project - Complete Environment Setup Script
REM Sets up Python 3.12+, Node.js, databases, and all dependencies

echo.
echo ========================================
echo   AI Base Project - Environment Setup
echo ========================================
echo.
echo Tech Stack:
echo   - Python 3.12+ ^& FastAPI
echo   - React.js 19.1 ^& Bootstrap 5.3
echo   - SQLite3 / PostgreSQL 17 / MongoDB
echo.

REM Check Python installation
echo [1/8] Checking Python 3.12+ installation...
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
echo [2/8] Checking Node.js installation...
node --version 2>nul | findstr /C:"v22" >nul
if errorlevel 1 (
    node --version 2>nul
    echo [WARNING] Node.js 22.16+ recommended but will continue...
) else (
    echo [✓] Node.js 22.16+ found
)

REM Set up shared configuration
echo.
echo [3/8] Setting up shared configuration...
if not exist "config\" mkdir config
if not exist "shared\" mkdir shared
if not exist "databases\" mkdir databases
if not exist "docs\" mkdir docs
echo [✓] Directory structure created

REM Check for .env file
echo.
echo [4/8] Checking environment configuration...
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

REM Set up version directories
echo.
echo [5/8] Setting up version structure...
for %%v in (v1 v2 v3) do (
    if exist "%%v\" (
        echo [✓] %%v exists
        
        REM Ensure proper structure
        if not exist "%%v\frontend\" mkdir "%%v\frontend"
        if not exist "%%v\backend\" mkdir "%%v\backend"
        if not exist "%%v\backend\app\" mkdir "%%v\backend\app"
        if not exist "%%v\tests\" mkdir "%%v\tests"
        
        REM Copy shared configurations if they don't exist
        if not exist "%%v\frontend\tsconfig.json" (
            if exist "config\tsconfig.json" (
                copy "config\tsconfig.json" "%%v\frontend\tsconfig.json" >nul
            )
        )
        
        if not exist "%%v\frontend\craco.config.js" (
            if exist "config\craco.config.js" (
                copy "config\craco.config.js" "%%v\frontend\craco.config.js" >nul
            )
        )
        
        if not exist "%%v\pyproject.toml" (
            if exist "config\pyproject.toml" (
                copy "config\pyproject.toml" "%%v\pyproject.toml" >nul
            )
        )
        
        REM Copy .env to version
        copy ".env" "%%v\.env" >nul 2>nul
        if exist "%%v\frontend\" copy ".env" "%%v\frontend\.env" >nul 2>nul
    )
)

REM Install Python dependencies for existing versions
echo.
echo [6/8] Installing Python dependencies...
for %%v in (v1 v2 v3) do (
    if exist "%%v\backend\" (
        echo Installing Python packages for %%v...
        cd %%v
        
        REM Create virtual environment if it doesn't exist
        if not exist "venv\" (
            echo Creating virtual environment for %%v...
            python -m venv venv
        )
        
        REM Activate virtual environment and install packages
        if exist "venv\Scripts\activate.bat" (
            call venv\Scripts\activate.bat
            
            REM Install from shared requirements
            if exist "..\shared\requirements\dev.txt" (
                pip install -r ..\shared\requirements\dev.txt
                echo [✓] Installed development dependencies for %%v
            ) else (
                pip install fastapi uvicorn sqlalchemy alembic
                echo [✓] Installed basic dependencies for %%v
            )
            
            deactivate
        )
        
        cd ..
    )
)

REM Install Node.js dependencies for existing versions
echo.
echo [7/8] Installing Node.js dependencies...
for %%v in (v1 v2 v3) do (
    if exist "%%v\frontend\package.json" (
        echo Installing Node.js packages for %%v/frontend...
        cd %%v\frontend
        npm install
        echo [✓] Installed frontend dependencies for %%v
        cd ..\..
    )
)

REM Final setup
echo.
echo [8/8] Finalizing setup...
echo [✓] Environment setup complete!
echo.
echo ========================================
echo          Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo   1. Review .env file and update as needed
echo   2. Choose a version to work with (v1, v2, v3)
echo   3. Run: project-manager.bat for interactive management
echo   4. Or run: scripts\activate-react-env.bat
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
