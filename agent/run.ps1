# --- FastAPI Development Server Startup Script ---
# --- Activates virtual environment and starts uvicorn server ---

Write-Host "Starting Cold Email Agent Backend..." -ForegroundColor Cyan
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Yellow

# --- Check Virtual Environment ---
if (-Not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "Virtual environment not found at .venv\Scripts\activate.ps1" -ForegroundColor Red
    Write-Host "Please create a virtual environment first with: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# --- Activate Virtual Environment ---
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".venv\Scripts\activate.ps1"

# --- Start Uvicorn Server ---
Write-Host "Starting FastAPI server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Auto-reload enabled for development" -ForegroundColor Gray
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Gray
Write-Host ""

uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
