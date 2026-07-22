$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
Set-Location $backendDir

if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -q

# A local MongoDB service may need a few seconds to open port 27017 after
# Windows starts it. Start it when it is installed but stopped, then wait for
# the port before launching Uvicorn.
if (-not (Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    $mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    if ($mongoService -and $mongoService.Status -ne "Running") {
        Write-Host "Starting MongoDB service..."
        Start-Service -Name "MongoDB"
    }

    Write-Host "Waiting for MongoDB on localhost:27017..."
    $deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Seconds 1
        $mongoReady = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
    } until ($mongoReady -or (Get-Date) -ge $deadline)

    if (-not $mongoReady) {
        throw "MongoDB is not accepting connections on localhost:27017. Start MongoDB or set MONGODB_URI in backend/.env."
    }
}

Write-Host "Starting FastAPI backend on http://localhost:8000"
Write-Host "API docs: http://localhost:8000/api/docs"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
