$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (!(Test-Path $python)) {
  Write-Host "Backend virtual environment not found. Create it with:" -ForegroundColor Yellow
  Write-Host "  cd backend"
  Write-Host "  python -m venv .venv"
  Write-Host "  .venv\Scripts\python.exe -m pip install -r requirements.txt"
  exit 1
}

Write-Host "Starting ClueHunt backend on http://127.0.0.1:8001" -ForegroundColor Cyan
Start-Process -FilePath $python `
  -ArgumentList "-m uvicorn app.main:app --reload --port 8001" `
  -WorkingDirectory $backend `
  -WindowStyle Normal

Write-Host "Starting ClueHunt frontend on http://127.0.0.1:5175" -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" `
  -ArgumentList "run dev -- --port 5175" `
  -WorkingDirectory $frontend `
  -WindowStyle Normal

Write-Host ""
Write-Host "Both dev servers are starting in separate windows." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:5175"
