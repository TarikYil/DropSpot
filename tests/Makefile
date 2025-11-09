# Test Makefile - DropSpot Test Suite

.PHONY: help test test-unit test-integration test-auth test-backend test-coverage test-watch clean-test

help:
	@echo "DropSpot Test Commands:"
	@echo ""
	@echo "  make test              - Tüm testleri çalıştır"
	@echo "  make test-unit         - Sadece unit testleri çalıştır"
	@echo "  make test-integration  - Sadece integration testleri çalıştır"
	@echo "  make test-auth         - Auth service testleri"
	@echo "  make test-backend      - Backend testleri"
	@echo "  make test-coverage     - Coverage raporu ile testleri çalıştır"
	@echo "  make test-watch        - Testleri watch modda çalıştır"
	@echo "  make install-test-deps - Test dependencies yükle"
	@echo "  make clean-test        - Test dosyalarını temizle"
	@echo ""

# Test dependencies yükle
install-test-deps:
	@echo "Test dependencies yükleniyor..."
	pip install -r requirements.txt

# Tüm testleri çalıştır
test:
	@echo "Tüm testler çalıştırılıyor..."
	pytest . -v

# Sadece unit testler
test-unit:
	@echo "Unit testler çalıştırılıyor..."
	pytest . -m unit -v

# Sadece integration testler
test-integration:
	@echo "Integration testler çalıştırılıyor..."
	pytest . -m integration -v

# Auth service testleri
test-auth:
	@echo "Auth service testleri çalıştırılıyor..."
	pytest . -m auth -v

# Backend testleri
test-backend:
	@echo "Backend testleri çalıştırılıyor..."
	pytest . -m backend -v

# Coverage raporu ile
test-coverage:
	@echo "Coverage raporu oluşturuluyor..."
	pytest . --cov=../auth_service --cov=../backend --cov-report=html --cov-report=term-missing -v
	@echo ""
	@echo "Coverage raporu: htmlcov/index.html"

# Watch mode (değişiklikleri izle)
test-watch:
	@echo "Watch mode başlatılıyor..."
	pytest-watch . -- -v

# Hızlı testler (fast tests)
test-fast:
	@echo "Hızlı testler çalıştırılıyor..."
	pytest . -v --tb=short --maxfail=1

# Verbose mode
test-verbose:
	@echo "Verbose mode ile testler..."
	pytest . -vv --tb=long

# Test dosyalarını temizle
clean-test:
	@echo "Test dosyaları temizleniyor..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf __pycache__
	rm -rf unit/__pycache__
	rm -rf integration/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Temizlik tamamlandı!"

# Parallel testler
test-parallel:
	@echo "Testler paralel çalıştırılıyor..."
	pytest . -n auto -v

