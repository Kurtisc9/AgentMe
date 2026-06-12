$ErrorActionPreference = "Stop"

Write-Host "=== AgentMe / Sage PC1 Installer ===" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git is required. Install Git first."
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw "Docker Desktop is required. Install Docker Desktop first."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python 3.12+ is required. Install Python first."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js LTS is required. Install Node.js first."
}

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example. Edit secrets before production use." -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force -Path "Inbox", "logs", "data", "voices", "backups" | Out-Null

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Push-Location frontend
npm install
npm run build
Pop-Location

docker compose -f docker-compose.prod.yml up -d --build
docker exec agentme-backend python scripts/migrate.py

Write-Host "AgentMe install complete." -ForegroundColor Green
Write-Host "HUD: http://127.0.0.1:8080" -ForegroundColor Cyan
Write-Host "API: http://127.0.0.1:8000" -ForegroundColor Cyan
