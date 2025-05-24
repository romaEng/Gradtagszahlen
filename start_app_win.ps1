# Get absolute path to the script directory
$SCRIPT_DIR = $PSScriptRoot

# Change to the project directory
Set-Location -Path $SCRIPT_DIR

# Refresh Git-Repository
Write-Host "Git Pull..." -ForegroundColor Cyan
git pull

# Activate virtual environment
Write-Host "Aktiviere virtuelle Umgebung..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Host "Virtuelle Umgebung erfolgreich aktiviert." -ForegroundColor Green
} else {
    Write-Host "Virtuelle Umgebung nicht gefunden. Erstelle neue Umgebung..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    Write-Host "Virtuelle Umgebung erfolgreich erstellt und aktiviert." -ForegroundColor Green
}

# Start Python script
Write-Host "Starte Anwendung..." -ForegroundColor Cyan
python main.py

# Keep terminal open after completion
Write-Host "Vorgang abgeschlossen. Zum Beenden: [ENTER]" -ForegroundColor Green
Read-Host
