@echo off
REM AI Base Project - Version Management Script
REM Centralized script for managing multiple versions

echo.
echo ========================================
echo     AI Base Project Manager
echo ========================================
echo.

REM Scan for existing versions
echo Scanning project versions...
echo.

set "VERSIONS="
if exist "v1\" (
    echo [✓] v1 - React.js Environment with Webpack Fix
    set "VERSIONS=%VERSIONS% v1"
)

if exist "v2\" (
    echo [✓] v2 - Available
    set "VERSIONS=%VERSIONS% v2"
)

if exist "v3\" (
    echo [✓] v3 - Available  
    set "VERSIONS=%VERSIONS% v3"
)

if "%VERSIONS%"=="" (
    echo [!] No versions found. Run this from the ai_base project root.
    pause
    exit /b 1
)

echo.
echo Available Actions:
echo   1. Activate React Environment (version-specific)
echo   2. Test Webpack Fix (version-specific)
echo   3. Manage Environment Variables
echo   4. Create New Version
echo   5. View Project Status
echo   6. Exit
echo.

:MENU
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Available versions:%VERSIONS%
    set /p version="Enter version to activate (v1, v2, v3): "
    
    if not exist "%version%\" (
        echo [ERROR] Version %version% not found!
        echo.
        goto MENU
    )
    
    echo Activating React environment for %version%...
    cd %version%
    call ..\scripts\activate-react-env.bat
    goto END
)

if "%choice%"=="2" (
    echo.
    call scripts\test-webpack-fix.bat
    goto MENU
)

if "%choice%"=="3" (
    echo.
    call manage-env.bat
    goto MENU
)

if "%choice%"=="4" (
    echo.
    set /p newversion="Enter new version name (e.g., v2, v3): "
    
    if exist "%newversion%\" (
        echo [ERROR] Version %newversion% already exists!
        echo.
        goto MENU
    )
    
    echo Creating %newversion%...
    mkdir "%newversion%"
    mkdir "%newversion%\frontend"
    mkdir "%newversion%\backend"
    mkdir "%newversion%\database"
    
    echo # %newversion% README > "%newversion%\README.md"
    echo. >> "%newversion%\README.md"
    echo This is version %newversion% of the AI Base project. >> "%newversion%\README.md"
    echo. >> "%newversion%\README.md"
    echo ## Quick Start >> "%newversion%\README.md"
    echo. >> "%newversion%\README.md"
    echo ```bash >> "%newversion%\README.md"
    echo cd %newversion%/frontend >> "%newversion%\README.md"
    echo npm install >> "%newversion%\README.md"
    echo npm start >> "%newversion%\README.md"
    echo ``` >> "%newversion%\README.md"
    
    REM Copy shared .env
    copy ".env" "%newversion%\frontend\.env" >nul
    
    echo [SUCCESS] Created %newversion%!
    echo Next steps:
    echo   1. Set up your frontend/backend in %newversion%/
    echo   2. Use 'scripts\activate-react-env.bat' to start development
    echo.
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo ========== Project Status ==========
    echo.
    echo Versions:%VERSIONS%
    echo.
    echo Shared Configuration:
    if exist ".env" (
        echo [✓] .env - Shared environment variables
    ) else (
        echo [!] .env - Missing
    )
    
    if exist ".env.template" (
        echo [✓] .env.template - Developer template
    )
    
    if exist "scripts\" (
        echo [✓] scripts/ - Shared automation scripts
    )
    
    if exist "manage-env.bat" (
        echo [✓] manage-env.bat - Environment management
    )
    
    echo.
    echo Git Status:
    git status --short 2>nul || echo [!] Not a git repository
    echo.
    echo ===================================
    echo.
    goto MENU
)

if "%choice%"=="6" (
    echo.
    echo Thanks for using AI Base Project Manager!
    goto END
)

echo Invalid choice. Please try again.
echo.
goto MENU

:END
echo.
pause
