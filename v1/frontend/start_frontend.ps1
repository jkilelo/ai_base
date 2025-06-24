# Frontend Start Script for ReactJS Dashboard (PowerShell)
# This script starts the React development server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FastAPI Dashboard - Frontend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[INFO] Node.js version: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "[INFO] Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "[INFO] Recommended version: Node.js 18.x or 20.x LTS" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[INFO] npm version: $npmVersion" -ForegroundColor Green
    } else {
        throw "npm not found"
    }
} catch {
    Write-Host "[ERROR] npm is not installed or not in PATH" -ForegroundColor Red
    Write-Host "[INFO] npm should be installed with Node.js" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[WARNING] node_modules directory not found" -ForegroundColor Yellow
    Write-Host "[INFO] Running npm install to install dependencies..." -ForegroundColor Blue
    
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed"
        }
        Write-Host "[SUCCESS] Dependencies installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[INFO] Starting React development server..." -ForegroundColor Blue
Write-Host "[INFO] The application will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host "[INFO] Make sure the FastAPI backend is running at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the React development server
try {
    npm start
} catch {
    Write-Host "[ERROR] Failed to start React development server" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "[INFO] React development server stopped" -ForegroundColor Blue
    Read-Host "Press Enter to exit"
}
