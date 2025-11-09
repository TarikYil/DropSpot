#!/bin/bash
# Docker içinde testleri çalıştırma scripti

set -e

echo "=========================================="
echo "  DropSpot Test Suite - Docker Mode"
echo "=========================================="
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test tipini al (varsayılan: tümü)
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    unit)
        echo -e "${YELLOW}Unit testleri çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ -m unit -v
        ;;
    integration)
        echo -e "${YELLOW}Integration testleri çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ -m integration -v
        ;;
    auth)
        echo -e "${YELLOW}Auth service testleri çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ -m auth -v
        ;;
    backend)
        echo -e "${YELLOW}Backend testleri çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ -m backend -v
        ;;
    coverage)
        echo -e "${YELLOW}Coverage raporu ile testler çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ \
            --cov=auth_service --cov=backend \
            --cov-report=html --cov-report=term-missing -v
        echo ""
        echo -e "${GREEN}Coverage raporu oluşturuldu: htmlcov/index.html${NC}"
        ;;
    watch)
        echo -e "${YELLOW}Watch mode - testler izleniyor...${NC}"
        docker-compose --profile test run --rm test_service ptw tests/ -- -v
        ;;
    all|*)
        echo -e "${YELLOW}Tüm testler çalıştırılıyor...${NC}"
        docker-compose --profile test run --rm test_service pytest tests/ -v --tb=short
        ;;
esac

# Exit code'u kontrol et
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo -e "  ✓ Testler başarılı!"
    echo -e "==========================================${NC}"
else
    echo ""
    echo -e "${RED}=========================================="
    echo -e "  ✗ Testler başarısız!"
    echo -e "==========================================${NC}"
    exit 1
fi

