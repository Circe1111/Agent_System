if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env with your API keys, then re-run: .\scripts\up.ps1"
    exit 1
}
docker load < eduagent-images.tar.gz 2>$null
docker compose up -d
Write-Host "================================================"
Write-Host "  EduAgent running!"
Write-Host "  Frontend: http://localhost"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Login:    admin / admin123"
Write-Host "================================================"
