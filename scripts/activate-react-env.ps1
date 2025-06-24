# AI Base Project - React Environment Activation Script (PowerShell)
# Version-agnostic script for React development environment activation

Write-Host ""
Write-Host "========================================"
Write-Host "   AI Base - React Development"
Write-Host "========================================"
Write-Host ""

# Detect current version
$Version = "unknown"
if (Test-Path "v1\frontend\package.json") { $Version = "v1" }
if (Test-Path "v2\frontend\package.json") { $Version = "v2" }  
if (Test-Path "v3\frontend\package.json") { $Version = "v3" }

# If in a version directory, detect which one
$CurrentDir = Split-Path -Leaf (Get-Location)
if ($CurrentDir -eq "v1") { $Version = "v1" }
if ($CurrentDir -eq "v2") { $Version = "v2" }
if ($CurrentDir -eq "v3") { $Version = "v3" }

Write-Host "Project Version: $Version"
Write-Host "Node.js: $((node --version 2>$null) -replace '^v', '')"
Write-Host "npm: $(npm --version 2>$null)"
Write-Host ""
Write-Host "Available Commands:"
Write-Host "  npm start       - Start development server"
Write-Host "  npm test        - Run tests"
Write-Host "  npm run build   - Build for production"
Write-Host "  npm install     - Install dependencies"
Write-Host ""
Write-Host "Environment Variables: Loaded from shared .env"
Write-Host "Server URL: http://localhost:3000"
Write-Host ""

# Navigate to the appropriate frontend directory
if ($Version -eq "unknown") {
    Write-Host "[INFO] Run this script from project root or version directory" -ForegroundColor Yellow
    Write-Host "Usage: scripts\activate-react-env.ps1"
    Write-Host "  or:  cd v1; ..\scripts\activate-react-env.ps1"
}
else {
    if ($CurrentDir -ne "frontend") {
        if (Test-Path "$Version\frontend") {
            Write-Host "Changing to $Version\frontend directory..."
            Set-Location "$Version\frontend"
        }
    }
    
    Write-Host "Ready for React development!" -ForegroundColor Green
    Write-Host "Type 'npm start' to begin development"
}

# Set environment variable to indicate we're in React environment
$env:REACT_ENV_ACTIVE = "true"
$env:AI_BASE_VERSION = $Version

# Function to deactivate environment
function Deactivate-ReactEnv {
    Remove-Item Env:REACT_ENV_ACTIVE -ErrorAction SilentlyContinue
    Remove-Item Env:PS1 -ErrorAction SilentlyContinue
    Write-Host "React environment deactivated." -ForegroundColor Green
}
