@echo off
REM AI Base Project - Webpack Deprecation Warning Fix Test
REM Version-agnostic script to test webpack configuration across all versions

echo.
echo ========================================
echo   Webpack Fix Verification Tool
echo ========================================
echo.

REM Detect available versions
echo Scanning for project versions...
echo.

set "FOUND_VERSIONS="

if exist "v1\frontend\package.json" (
    echo [✓] Found v1/frontend
    set "FOUND_VERSIONS=%FOUND_VERSIONS% v1"
)

if exist "v2\frontend\package.json" (
    echo [✓] Found v2/frontend  
    set "FOUND_VERSIONS=%FOUND_VERSIONS% v2"
)

if exist "v3\frontend\package.json" (
    echo [✓] Found v3/frontend
    set "FOUND_VERSIONS=%FOUND_VERSIONS% v3"
)

if "%FOUND_VERSIONS%"=="" (
    echo [ERROR] No frontend versions found!
    echo Please run this script from the ai_base project root
    pause
    exit /b 1
)

echo.
echo Available versions:%FOUND_VERSIONS%
echo.

set /p VERSION="Enter version to test (v1, v2, v3): "

if not exist "%VERSION%\frontend\package.json" (
    echo [ERROR] Version %VERSION% not found!
    pause
    exit /b 1
)

echo.
echo Testing %VERSION%/frontend...
echo Looking for webpack-dev-server deprecation warnings...
echo.
echo [INFO] Starting development server...
echo [INFO] Press Ctrl+C after server starts to verify no warnings appear
echo [INFO] Look for these warnings (should NOT appear):
echo   - onAfterSetupMiddleware deprecation warning
echo   - onBeforeSetupMiddleware deprecation warning
echo.

cd %VERSION%\frontend
npm start

set PORT=3000
npm start
