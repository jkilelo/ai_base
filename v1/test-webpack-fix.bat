@echo off
echo.
echo ========================================
echo   Webpack Deprecation Warning Fix Test
echo ========================================
echo.
echo Testing React development server...
echo Looking for deprecation warnings...
echo.

cd frontend
echo Starting server on port 3000 for testing...
echo Press Ctrl+C after server starts to verify no warnings appear
echo.

set PORT=3000
npm start
