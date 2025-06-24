# React Environment Activation Script (PowerShell)
# Similar to Python's venv activation

Write-Host ""
Write-Host "========================================"
Write-Host "   React Development Environment"
Write-Host "========================================"
Write-Host ""
Write-Host "Environment: frontend"
Write-Host "Node.js: $((node --version 2>$null) -replace '^v', '')"
Write-Host "npm: $(npm --version 2>$null)"
Write-Host ""
Write-Host "Available Commands:"
Write-Host "  npm start       - Start development server"
Write-Host "  npm test        - Run tests"
Write-Host "  npm run build   - Build for production"
Write-Host "  npm install     - Install dependencies"
Write-Host ""
Write-Host "Current directory: $(Get-Location)"
Write-Host ""
Write-Host "To start development server: npm start"
Write-Host "Server will be available at: http://localhost:3000"
Write-Host ""

# Change to frontend directory if not already there
if (-not (Test-Path "package.json")) {
    if (Test-Path "frontend\package.json") {
        Write-Host "Changing to frontend directory..."
        Set-Location frontend
    }
    else {
        Write-Host "Warning: No package.json found. Are you in the right directory?" -ForegroundColor Yellow
    }
}

# Set environment variable to indicate we're in React environment
$env:REACT_ENV_ACTIVE = "true"
$env:PS1 = "[React-Env] PS $($PWD.Path)> "

# Function to deactivate environment
function Deactivate-ReactEnv {
    Remove-Item Env:REACT_ENV_ACTIVE -ErrorAction SilentlyContinue
    Remove-Item Env:PS1 -ErrorAction SilentlyContinue
    Write-Host "React environment deactivated." -ForegroundColor Green
}
