# Frontend test runner script (PowerShell)

Write-Host "Frontend Test Runner" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
npm test -- --run

