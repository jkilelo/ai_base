@echo off
REM React Environment Activation Script
REM Similar to Python's venv activation

echo.
echo ========================================
echo   React Development Environment
echo ========================================
echo.
echo Environment: frontend
echo Node.js: %node --version 2>nul || echo Not found%
echo npm: %npm --version 2>nul || echo Not found%
echo.
echo Available Commands:
echo   npm start       - Start development server
echo   npm test        - Run tests
echo   npm run build   - Build for production
echo   npm install     - Install dependencies
echo.
echo Current directory: %cd%
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
