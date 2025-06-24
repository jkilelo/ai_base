@echo off
REM AI Base Project - React Environment Activation Script
REM Version-agnostic script for React development environment activation

echo.
echo ========================================
echo   AI Base - React Development
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
echo Node.js: 
node --version 2>nul || echo Not found
echo npm: 
npm --version 2>nul || echo Not found
echo.
echo Available Commands:
echo   npm start       - Start development server
echo   npm test        - Run tests  
echo   npm run build   - Build for production
echo   npm install     - Install dependencies
echo.
echo Environment Variables: Loaded from shared .env
echo Server URL: http://localhost:3000
echo.

REM Navigate to the appropriate frontend directory
if "%VERSION%"=="unknown" (
    echo [INFO] Run this script from project root or version directory
    echo Usage: scripts\activate-react-env.bat
    echo   or:  cd v1 ^&^& ..\scripts\activate-react-env.bat
) else (
    if not "%CURRENT_DIR%"=="frontend" (
        if exist "%VERSION%\frontend" (
            echo Changing to %VERSION%\frontend directory...
            cd %VERSION%\frontend
        )
    )
    
    echo Ready for React development!
    echo Type 'npm start' to begin development
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
