# Development Environment Start Script (PowerShell)
# This script starts both backend and frontend or provides guidance

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Check
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FastAPI Dashboard - Development Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Test-BackendHealth {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get -TimeoutSec 5
        return $true
    } catch {
        return $false
    }
}

function Test-FrontendServer {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Head -TimeoutSec 5
        return $true
    } catch {
        return $false
    }
}

if ($Check) {
    Write-Host "[INFO] Checking development environment status..." -ForegroundColor Blue
    Write-Host ""
    
    # Check backend
    Write-Host "Backend (FastAPI) - http://localhost:8000" -NoNewline
    if (Test-BackendHealth) {
        Write-Host " [RUNNING]" -ForegroundColor Green
    } else {
        Write-Host " [NOT RUNNING]" -ForegroundColor Red
    }
    
    # Check frontend
    Write-Host "Frontend (React) - http://localhost:3000" -NoNewline
    if (Test-FrontendServer) {
        Write-Host " [RUNNING]" -ForegroundColor Green
    } else {
        Write-Host " [NOT RUNNING]" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "[INFO] To start services:" -ForegroundColor Yellow
    Write-Host "  Backend:  cd ..\backend && .\start_backend.bat" -ForegroundColor Gray
    Write-Host "  Frontend: .\start_frontend.bat" -ForegroundColor Gray
    Write-Host ""
    return
}

if ($BackendOnly) {
    Write-Host "[INFO] Starting backend only..." -ForegroundColor Blue
    Write-Host "[INFO] Please run this from the backend directory:" -ForegroundColor Yellow
    Write-Host "  cd ..\backend" -ForegroundColor Gray
    Write-Host "  .\start_backend.bat" -ForegroundColor Gray
    Write-Host ""
    return
}

if ($FrontendOnly) {
    Write-Host "[INFO] Starting frontend only..." -ForegroundColor Blue
    
    # Check if backend is running
    if (-not (Test-BackendHealth)) {
        Write-Host "[WARNING] Backend is not running at http://localhost:8000" -ForegroundColor Yellow
        Write-Host "[INFO] The dashboard may not show live data without the backend" -ForegroundColor Yellow
        Write-Host ""
    }
    
    & ".\start_frontend.ps1"
    return
}

# Default: Show full development setup instructions
Write-Host "[INFO] Full Development Environment Setup" -ForegroundColor Blue
Write-Host ""
Write-Host "To start the complete development environment:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Start Backend (FastAPI):" -ForegroundColor Yellow
Write-Host "   cd ..\backend" -ForegroundColor Gray
Write-Host "   .\start_backend.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend (React) - In a new terminal:" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   .\start_frontend.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "Or use these PowerShell commands:" -ForegroundColor Green
Write-Host "   .\start_dev.ps1 -BackendOnly    # Start backend only" -ForegroundColor Gray
Write-Host "   .\start_dev.ps1 -FrontendOnly   # Start frontend only" -ForegroundColor Gray
Write-Host "   .\start_dev.ps1 -Check          # Check service status" -ForegroundColor Gray
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Green
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to continue"
