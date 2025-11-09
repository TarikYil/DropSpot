# 🧪 DropSpot Test Guide

Docker içinde tam entegre test ortamı.

## 📋 İçindekiler

- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Test Çalıştırma](#test-çalıştırma)
- [Test Tipleri](#test-tipleri)
- [Docker Komutları](#docker-komutları)

## 🚀 Hızlı Başlangıç

### 1. Servisleri Başlat

```bash
# Ana servisleri başlat (auth, backend, postgres)
docker-compose up -d

# Test veritabanlarının oluşturulduğunu kontrol et
docker-compose exec postgres psql -U postgres -l
```

### 2. Testleri Çalıştır

```bash
# Tüm testleri çalıştır
docker-compose --profile test run --rm test_service

# Veya kısa yol:
docker-compose run --rm test_service
```

## 🧪 Test Çalıştırma

### Tüm Testler

```bash
# Docker içinde
docker-compose run --rm test_service

# PowerShell script ile
.\scripts\run_tests_docker.ps1

# Bash script ile
./scripts/run_tests_docker.sh
```

### Unit Testler (Hızlı)

```bash
# Docker içinde
docker-compose run --rm test_service pytest tests/ -m unit -v

# Script ile
.\scripts\run_tests_docker.ps1 -TestType unit
```

### Integration Testler

```bash
# Docker içinde
docker-compose run --rm test_service pytest tests/ -m integration -v

# Script ile
.\scripts\run_tests_docker.ps1 -TestType integration
```

### Servise Göre Testler

```bash
# Auth service testleri
docker-compose run --rm test_service pytest tests/ -m auth -v

# Backend testleri
docker-compose run --rm test_service pytest tests/ -m backend -v
```

### Coverage Raporu

```bash
# Docker içinde
docker-compose run --rm test_service pytest tests/ \
  --cov=auth_service \
  --cov=backend \
  --cov-report=html \
  --cov-report=term-missing -v

# Script ile
.\scripts\run_tests_docker.ps1 -TestType coverage

# Coverage raporunu görüntüle
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

## 📊 Test Tipleri

### Unit Tests
- **Hızlı** (saniyeler içinde)
- **İzole** (external dependency yok)
- Test edilen: Utils, models, fonksiyonlar

```bash
docker-compose run --rm test_service pytest tests/unit/ -v
```

### Integration Tests
- **Yavaş** (dakikalar)
- **Servislere bağımlı** (database, API)
- Test edilen: API endpoints, servisler arası iletişim

```bash
docker-compose run --rm test_service pytest tests/integration/ -v
```

## 🐳 Docker Komutları

### Test Container Build

```bash
# Test container'ı build et
docker-compose build test_service

# Cache olmadan rebuild
docker-compose build --no-cache test_service
```

### İnteraktif Test

```bash
# Test container'a shell ile gir
docker-compose run --rm test_service /bin/bash

# Container içinde:
pytest tests/unit/test_auth_utils.py -v
pytest tests/integration/test_auth_endpoints.py::TestAuthLogin -v
```

### Belirli Bir Test Dosyası

```bash
docker-compose run --rm test_service \
  pytest tests/unit/test_auth_utils.py -v
```

### Belirli Bir Test Fonksiyonu

```bash
docker-compose run --rm test_service \
  pytest tests/unit/test_auth_utils.py::TestPasswordHashing::test_password_hashing -v
```

### Test Logları

```bash
# Test container loglarını izle
docker-compose logs -f test_service

# Son 50 satır
docker-compose logs --tail 50 test_service
```

## 🔧 Gelişmiş Kullanım

### Paralel Test

```bash
docker-compose run --rm test_service pytest tests/ -n auto -v
```

### Fail Fast (İlk hatada dur)

```bash
docker-compose run --rm test_service pytest tests/ -x -v
```

### Verbose Output

```bash
docker-compose run --rm test_service pytest tests/ -vv --tb=long
```

### Print Statements Göster

```bash
docker-compose run --rm test_service pytest tests/ -s
```

### Sadece Başarısız Testleri Tekrar Çalıştır

```bash
docker-compose run --rm test_service pytest tests/ --lf -v
```

### Test Süresini Göster

```bash
docker-compose run --rm test_service pytest tests/ --durations=10
```

## 🎯 Marker Kombinasyonları

```bash
# Auth service unit testleri
docker-compose run --rm test_service pytest tests/ -m "unit and auth" -v

# Backend integration testleri
docker-compose run --rm test_service pytest tests/ -m "integration and backend" -v

# Yavaş testleri atla
docker-compose run --rm test_service pytest tests/ -m "not slow" -v
```

## 🛠️ Sorun Giderme

### Test Veritabanı Sıfırlama

```bash
# Test veritabanlarını sil ve yeniden oluştur
docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS test_auth_db;"
docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS test_dropspot_db;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE test_auth_db;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE test_dropspot_db;"
```

### Cache Temizleme

```bash
# Pytest cache'i temizle
docker-compose run --rm test_service pytest --cache-clear

# __pycache__ dizinlerini temizle
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Test Container Yeniden Build

```bash
docker-compose build --no-cache test_service
```

## 📈 CI/CD Entegrasyonu

### GitHub Actions Örneği

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build containers
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose run --rm test_service
      
      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: htmlcov/
```

## 📝 Test Yazma

### Yeni Test Ekleme

1. **Unit test için:**
   ```bash
   # tests/unit/test_yeni_modul.py oluştur
   docker-compose run --rm test_service pytest tests/unit/test_yeni_modul.py -v
   ```

2. **Integration test için:**
   ```bash
   # tests/integration/test_yeni_endpoint.py oluştur
   docker-compose run --rm test_service pytest tests/integration/test_yeni_endpoint.py -v
   ```

### Test Template

```python
import pytest

@pytest.mark.unit  # veya @pytest.mark.integration
@pytest.mark.auth  # veya @pytest.mark.backend
def test_example():
    """Test açıklaması"""
    # Arrange
    expected = "result"
    
    # Act
    actual = function_to_test()
    
    # Assert
    assert actual == expected
```

## 🎓 Best Practices

1. ✅ **Hızlı testler yaz** - Unit testler saniyeler içinde bitmeli
2. ✅ **İzole testler** - Testler birbirinden bağımsız olmalı
3. ✅ **Anlamlı isimler** - `test_user_login_with_valid_credentials`
4. ✅ **Fixtures kullan** - Tekrarlayan setup kodunu azalt
5. ✅ **Mock kullan** - External servisleri mock'la
6. ✅ **Coverage takip et** - %80+ hedefle
7. ✅ **CI/CD entegrasyonu** - Her commit'te testler çalışsın

## 📞 Yardım

```bash
# Pytest yardım
docker-compose run --rm test_service pytest --help

# Marker listesi
docker-compose run --rm test_service pytest --markers

# Fixture listesi
docker-compose run --rm test_service pytest --fixtures
```

## 🎯 Örnek Kullanım Senaryoları

### Senaryo 1: Yeni özellik geliştirme
```bash
# 1. Unit testleri yaz ve çalıştır
docker-compose run --rm test_service pytest tests/unit/test_yeni_ozellik.py -v

# 2. Integration testleri ekle
docker-compose run --rm test_service pytest tests/integration/test_yeni_ozellik.py -v

# 3. Tüm testleri çalıştır
docker-compose run --rm test_service
```

### Senaryo 2: Bug fix
```bash
# 1. Bug'ı reproduce eden test yaz (red)
docker-compose run --rm test_service pytest tests/unit/test_bug.py -v

# 2. Bug'ı düzelt

# 3. Testi tekrar çalıştır (green)
docker-compose run --rm test_service pytest tests/unit/test_bug.py -v
```

### Senaryo 3: Refactoring
```bash
# 1. Tüm testleri çalıştır (green olmalı)
docker-compose run --rm test_service

# 2. Refactor yap

# 3. Testleri tekrar çalıştır (hala green)
docker-compose run --rm test_service
```

---

**Not:** Test servisi `--profile test` ile işaretlendiği için normal `docker-compose up` komutu ile başlamaz. Sadece test çalıştırırken aktif olur.

