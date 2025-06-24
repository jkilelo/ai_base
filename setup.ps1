#!/usr/bin/env pwsh
# AI Base Platform - Environment Setup with UV (PowerShell)
# This script sets up Python 3.12+ environment using UV

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "AI Base Platform - Environment Setup" -ForegroundColor Cyan
Write-Host "Python 3.12+ Required" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Cyan

# Function to check Python version
function Test-PythonVersion {
    param($pythonCmd, $pythonArgs = $null)
    try {
        if ($pythonArgs) {
            $versionOutput = & $pythonCmd $pythonArgs --version 2>&1
        } else {
            $versionOutput = & $pythonCmd --version 2>&1
        }
        
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

# Function to remove old Python environments
function Remove-OldPythonEnvironments {
    Write-Host "Checking for old Python environments to remove..." -ForegroundColor Yellow
    
    # Remove existing venv if it uses old Python
    if (Test-Path ".venv") {
        Write-Host "Found existing .venv directory. Checking Python version..." -ForegroundColor Yellow
        $oldPython = ".venv\Scripts\python.exe"
        if (Test-Path $oldPython) {
            if (-not (Test-PythonVersion $oldPython)) {
                Write-Host "Removing old Python environment (< 3.12)..." -ForegroundColor Red
                Remove-Item -Recurse -Force ".venv"
                Write-Host "Old environment removed" -ForegroundColor Green
            } else {
                Write-Host "Existing environment uses Python 3.12+, keeping it" -ForegroundColor Green
                return $true
            }
        } else {
            Write-Host "Removing broken environment..." -ForegroundColor Red
            Remove-Item -Recurse -Force ".venv"
        }
    }
    
    # Also remove any conda environments that might be named ai-base or similar
    Write-Host "Checking for conda environments with old Python..." -ForegroundColor Yellow
    try {
        $condaEnvs = conda env list 2>$null | Select-String "ai-base"
        if ($condaEnvs) {
            Write-Host "Found conda ai-base environment. Checking if it needs removal..." -ForegroundColor Yellow
            $condaPython = conda run -n ai-base python --version 2>$null
            if ($condaPython -and $condaPython -notmatch "Python 3\.1[2-9]|Python 3\.[2-9][0-9]") {
                Write-Host "Removing old conda ai-base environment..." -ForegroundColor Red
                conda env remove -n ai-base -y 2>$null
                Write-Host "Old conda environment removed" -ForegroundColor Green
            }
        }
    } catch {
        # Conda not available, continue
    }
    
    return $false
}

# Check for Python 3.12+
Write-Host "Checking for Python 3.12+..." -ForegroundColor Yellow
$pythonCommands = @("python3.12", "python3.13", "python3.14", "python", "py")
$validPython = $null

foreach ($cmd in $pythonCommands) {
    try {
        if (Test-PythonVersion $cmd) {
            $validPython = $cmd
            $versionOutput = & $cmd --version
            Write-Host "Found valid Python: $versionOutput" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $validPython) {
    Write-Host "ERROR: Python 3.12+ not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure it's added to your PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Currently available Python versions:" -ForegroundColor Yellow
    foreach ($cmd in @("python", "py", "python3")) {
        try {
            $version = & $cmd --version 2>&1
            Write-Host "  $cmd : $version" -ForegroundColor Gray
        } catch {
            Write-Host "  $cmd : Not found" -ForegroundColor Gray
        }
    }
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if UV is installed
try {
    $uvVersion = uv --version
    Write-Host "UV version: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "UV not found. Installing UV..." -ForegroundColor Yellow
    try {
        irm https://astral.sh/uv/install.ps1 | iex
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $uvVersion = uv --version
        Write-Host "UV installed successfully: $uvVersion" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install UV. Please install manually: https://github.com/astral-sh/uv" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Remove old environments and check if we can reuse existing one
$reuseEnv = Remove-OldPythonEnvironments

if (-not $reuseEnv) {
    # Create virtual environment with UV using Python 3.12+
    Write-Host "Creating virtual environment with Python 3.12+..." -ForegroundColor Yellow
    try {
        uv venv .venv --python $validPython
        Write-Host "Virtual environment created successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    uv pip install -e .
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install development dependencies
Write-Host "Installing development dependencies..." -ForegroundColor Yellow
try {
    uv pip install -e ".[dev,test]"
    Write-Host "Development dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to install development dependencies" -ForegroundColor Yellow
}

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
try {
    playwright install
    Write-Host "Playwright browsers installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to install Playwright browsers" -ForegroundColor Yellow
}

# Copy environment template if .env doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.template .env
    Write-Host ".env file created from template" -ForegroundColor Green
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment, run:" -ForegroundColor Yellow
Write-Host ".venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To start the backend server, run:" -ForegroundColor Yellow
Write-Host "uv run python main.py" -ForegroundColor White
Write-Host ""
Write-Host "To start the development mode, run:" -ForegroundColor Yellow
Write-Host "uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
