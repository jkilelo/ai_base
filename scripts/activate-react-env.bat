@echo off
REM AI Base Project - Full Stack Development Environment Activation
REM Tech Stack: Python 3.12+ | ReactJS 19.1 | FastAPI | Bootstrap 5.3 | SQLite/PostgreSQL/MongoDB

echo.
echo ========================================
echo   AI Base - Full Stack Development
echo ========================================
echo.

REM Detect current version
set "VERSION=unknown"
if exist "v1\frontend\package.json" set "VERSION=v1"
if exist "v2\frontend\package.json" set "VERSION=v2"
if exist "v3\frontend\package.json" set "VERSION=v3"

REM If in a version directory, detect which one
for %%I in ("%cd%") do set "CURRENT_DIR=%%~nxI"
if "%CURRENT_DIR%"=="v1" set "VERSION=v1"
if "%CURRENT_DIR%"=="v2" set "VERSION=v2"
if "%CURRENT_DIR%"=="v3" set "VERSION=v3"

echo Project Version: %VERSION%
echo.
echo Tech Stack Status:
echo   Python: 
python --version 2>nul || echo Not found - Install Python 3.12+
echo   Node.js: 
node --version 2>nul || echo Not found - Install Node.js 22.16+
echo   npm: 
npm --version 2>nul || echo Not found
echo.
echo Available Services:
echo   Frontend (React 19.1 + Bootstrap 5.3):
echo     npm start       - Start React development server (Port 3000)
echo     npm test        - Run React tests
echo     npm run build   - Build React for production
echo.
echo   Backend (FastAPI + SQLAlchemy):
echo     uvicorn app.main:app --reload --port 8000
echo     python -m pytest - Run Python tests
echo.
echo   Database Options:
echo     SQLite    - Default development database
echo     PostgreSQL - Production database (Port 5432)
echo     MongoDB   - NoSQL database (Port 27017)
echo.
echo Environment: Loaded from shared .env
echo Frontend URL: http://localhost:3000
echo Backend API:  http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo.

REM Navigate to the appropriate directory
if "%VERSION%"=="unknown" (
    echo [INFO] Run this script from project root or version directory
    echo Usage: scripts\activate-env.bat
    echo   or:  cd v1 ^&^& ..\scripts\activate-env.bat
) else (
    echo Available Commands for %VERSION%:
    echo.
    echo Frontend Development:
    echo   cd %VERSION%\frontend ^&^& npm start
    echo.
    echo Backend Development:
    echo   cd %VERSION%\backend ^&^& python -m uvicorn app.main:app --reload
    echo.
    echo Full Stack Development:
    echo   1. Start Backend:  cd %VERSION%\backend ^&^& uvicorn app.main:app --reload
    echo   2. Start Frontend: cd %VERSION%\frontend ^&^& npm start
    echo.
    
    if not "%CURRENT_DIR%"=="frontend" (
        if exist "%VERSION%\frontend" (
            echo Changing to %VERSION%\frontend directory...
            cd %VERSION%\frontend
        )
    )
    
    echo Ready for full-stack development!
    echo Choose your development mode:
    echo   Type 'npm start' for frontend development
    echo   Type 'cd ..\backend' for backend development
)
echo.
echo To start development server: npm start
echo Server will be available at: http://localhost:3000
echo.

REM Change to frontend directory if not already there
if not exist "package.json" (
    if exist "frontend\package.json" (
        echo Changing to frontend directory...
        cd frontend
    ) else (
        echo Warning: No package.json found. Are you in the right directory?
    )
)

REM Set command prompt to show we're in React environment
prompt $P$S[React-Env]$G$S
