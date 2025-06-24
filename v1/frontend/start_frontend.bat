@echo off
REM Frontend Start Script for ReactJS Dashboard
REM This script starts the React development server

echo ========================================
echo  FastAPI Dashboard - Frontend Server
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please run 'setup.bat' first to set up the environment
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] node_modules directory not found
    echo [INFO] Running npm install to install dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [INFO] Starting React development server...
echo [INFO] The application will be available at: http://localhost:3000
echo [INFO] Make sure the FastAPI backend is running at: http://localhost:8000
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the React development server
npm start

echo.
echo [INFO] React development server stopped
pause
