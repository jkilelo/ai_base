@echo off
REM Frontend Setup Script for ReactJS Dashboard
REM This script sets up the Node.js environment and installs dependencies

echo ========================================
echo  FastAPI Dashboard - Frontend Setup
echo ========================================
echo.

REM Check if Node.js is installed
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please install Node.js from https://nodejs.org/
    echo [INFO] Recommended version: Node.js 18.x or 20.x LTS
    pause
    exit /b 1
)

REM Check if npm is installed
echo [INFO] Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed or not in PATH
    echo [INFO] npm should be installed with Node.js
    pause
    exit /b 1
)

echo [INFO] Node.js and npm are available
node --version
npm --version
echo.

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Frontend setup completed successfully!
echo [INFO] You can now run 'start_frontend.bat' to start the development server
echo.
pause
