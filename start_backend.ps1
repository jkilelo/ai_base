#!/usr/bin/env pwsh
# AI Base Platform - Start Backend Server (PowerShell)
# Uses UV and enforces Python 3.12+

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "AI Base Platform - Starting Backend" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Function to check Python version
function Test-PythonVersion {
    param($pythonPath)
    try {
        $versionOutput = & $pythonPath --version 2>&1
        if ($versionOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            return ($major -eq 3 -and $minor -ge 12)
        }
        return $false
    } catch {
        return $false
    }
}

# Check if virtual environment exists
if (-not (Test-Path .venv)) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version in venv
Write-Host "Checking Python version in virtual environment..." -ForegroundColor Yellow
$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Python executable not found in virtual environment" -ForegroundColor Red
    Write-Host "Please run setup.ps1 to recreate the environment" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-PythonVersion $venvPython)) {
    Write-Host "Virtual environment does not use Python 3.12+" -ForegroundColor Red
    Write-Host "Please run setup.ps1 to recreate the environment" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonVersion = & $venvPython --version
Write-Host "✓ Python 3.12+ confirmed in virtual environment: $pythonVersion" -ForegroundColor Green

# Check if UV is installed
try {
    $uvVersion = uv --version
    Write-Host "Using UV: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "UV not found. Please install UV or run setup.ps1" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the server
Write-Host "" -ForegroundColor White
Write-Host "Starting AI Base Platform backend server..." -ForegroundColor Yellow
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation will be available at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Interactive API docs: http://localhost:8000/redoc" -ForegroundColor Green
Write-Host "" -ForegroundColor White

try {
    uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "Failed to start the server" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
