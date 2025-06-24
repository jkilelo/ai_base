@echo off
REM AI Base Project - Environment Management Script
REM This script helps manage environment variables across all versions

echo ========================================
echo AI Base Project - Environment Manager
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] No .env file found!
    echo.
    echo Creating .env from template...
    if exist ".env.template" (
        copy ".env.template" ".env"
        echo [SUCCESS] Created .env from template
        echo Please edit .env with your specific configuration
    ) else (
        echo [ERROR] No .env.template found!
        echo Please create .env manually
    )
    echo.
    pause
    exit /b 1
)

echo [INFO] Found .env file
echo.

REM Sync .env to all versions
echo Syncing .env to all versions...
echo.

REM Sync to v1
if exist "v1\frontend\" (
    copy ".env" "v1\frontend\.env" >nul
    echo [✓] Synced to v1/frontend/
)

REM Sync to v2 (if it exists)
if exist "v2\frontend\" (
    copy ".env" "v2\frontend\.env" >nul
    echo [✓] Synced to v2/frontend/
)

REM Sync to v3 (if it exists)
if exist "v3\frontend\" (
    copy ".env" "v3\frontend\.env" >nul
    echo [✓] Synced to v3/frontend/
)

echo.
echo [SUCCESS] Environment variables synchronized!
echo.
echo Available commands:
echo   1. Edit shared .env file
echo   2. View current .env contents
echo   3. Create version-specific override
echo   4. Exit
echo.

:MENU
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    notepad .env
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo ========== Current .env Contents ==========
    type .env
    echo.
    echo ==========================================
    echo.
    goto MENU
)

if "%choice%"=="3" (
    echo.
    set /p version="Enter version (v1, v2, v3, etc.): "
    set /p component="Enter component (frontend, backend, etc.): "
    
    set override_path=%version%\%component%\.env.local
    
    echo Creating override file: %override_path%
    echo # Version-specific environment variable overrides > "%override_path%"
    echo # These variables will override the shared .env file >> "%override_path%"
    echo # >> "%override_path%"
    echo # Example: >> "%override_path%"
    echo # REACT_APP_PROJECT_VERSION=%version% >> "%override_path%"
    echo # PORT=3001 >> "%override_path%"
    
    echo [SUCCESS] Created %override_path%
    echo You can now edit this file to add version-specific overrides
    echo.
    goto MENU
)

if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
)

echo Invalid choice. Please try again.
goto MENU
