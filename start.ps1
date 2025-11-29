# Start script for Federated NL2SQL (PowerShell)
# Run both backend and frontend servers

Write-Host "Starting Federated NL2SQL..." -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "backend/app.py")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Start backend in new window
Write-Host "Starting Flask backend on port 5000..." -ForegroundColor Yellow
$backendScript = @"
Write-Host 'Flask Backend Starting...' -ForegroundColor Green
if (Test-Path 'shrm/Scripts/Activate.ps1') {
    & '.\shrm\Scripts\Activate.ps1'
}
python backend/app.py
"@
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendScript)

# Wait for backend to initialize
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting React frontend on port 3000..." -ForegroundColor Yellow
$currentPath = Get-Location
$frontendPath = Join-Path $currentPath "frontend"
$frontendScript = @"
Write-Host 'React Frontend Starting...' -ForegroundColor Green
Set-Location -LiteralPath '$frontendPath'
npm run dev
"@
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendScript)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Federated NL2SQL is running!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "" 
Write-Host "Close the terminal windows to stop servers" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
