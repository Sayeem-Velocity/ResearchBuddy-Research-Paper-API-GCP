# Start script for ResearchBuddy API and Frontend

Write-Host "🚀 Starting ResearchBuddy Application..." -ForegroundColor Green

# Kill any existing processes on ports
Write-Host "Cleaning up ports..." -ForegroundColor Yellow
$process8004 = Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process8004) { Stop-Process -Id $process8004 -Force -ErrorAction SilentlyContinue }

$process3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process3000) { Stop-Process -Id $process3000 -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 1

# Start Backend in new terminal
Write-Host "Starting Backend API on port 8004..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; venv\Scripts\activate; uvicorn app.main:app --reload --port 8004"

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend in new terminal
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "✅ Application Started!" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:8004" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup on exit
Write-Host "Stopping servers..." -ForegroundColor Red
$process8004 = Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process8004) { Stop-Process -Id $process8004 -Force -ErrorAction SilentlyContinue }

$process3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process3000) { Stop-Process -Id $process3000 -Force -ErrorAction SilentlyContinue }

Write-Host "Servers stopped." -ForegroundColor Green
