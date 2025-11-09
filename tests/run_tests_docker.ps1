# Docker içinde testleri çalıştırma scripti (PowerShell)

param(
    [string]$TestType = "all"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  DropSpot Test Suite - Docker Mode" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

switch ($TestType) {
    "unit" {
        Write-Host "Unit testleri calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ -m unit -v
    }
    "integration" {
        Write-Host "Integration testleri calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ -m integration -v
    }
    "auth" {
        Write-Host "Auth service testleri calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ -m auth -v
    }
    "backend" {
        Write-Host "Backend testleri calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ -m backend -v
    }
    "coverage" {
        Write-Host "Coverage raporu ile testler calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ --cov=auth_service --cov=backend --cov-report=html --cov-report=term-missing -v
        Write-Host ""
        Write-Host "Coverage raporu olusturuldu: htmlcov/index.html" -ForegroundColor Green
    }
    default {
        Write-Host "Tum testler calistiriliyor..." -ForegroundColor Yellow
        docker-compose --profile test run --rm test_service pytest tests/ -v --tb=short
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Testler basarili!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "  Testler basarisiz!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit 1
}

