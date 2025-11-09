# DropSpot Test Suite

Kapsamlı Unit Test ve Integration Test yapısı.

## Klasör Yapısı

```
tests/
├── conftest.py              # Pytest fixtures
├── pytest.ini               # Pytest konfigürasyonu
├── requirements.txt         # Test dependencies
│
├── unit/                    # Unit Tests (hızlı, izole)
│   ├── test_auth_utils.py       # Auth utility fonksiyonları
│   ├── test_auth_models.py      # Auth database modelleri
│   ├── test_backend_security.py # Backend security utils
│   └── test_backend_models.py   # Backend database modelleri
│
├── integration/             # Integration Tests (servislere bağımlı)
│   ├── test_auth_endpoints.py       # Auth API endpoints
│   ├── test_role_management.py     # Rol yönetimi API
│   └── test_superadmin_panel.py    # Süper admin paneli
│
└── utils/                   # Test yardımcı fonksiyonları
    └── test_helpers.py
```

## Kurulum

### 1. Test Dependencies Yükle

```bash
pip install -r tests/requirements.txt
```

Veya Makefile ile:

```bash
cd tests
make install-test-deps
```

### 2. Test Veritabanlarını Hazırla

Test veritabanları otomatik olarak oluşturulur, ancak manuel olarak da oluşturabilirsiniz:

```bash
# PostgreSQL'de test veritabanları oluştur
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE test_auth_db;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE test_dropspot_db;"
```

## Testleri Çalıştırma

### Tüm Testleri Çalıştır

```bash
pytest tests/
```

Veya Python script ile (tests klasöründen):

```bash
cd tests
python run_tests.py
```

Veya Makefile ile (tests klasöründen):

```bash
cd tests
make test
```

### Unit Testler (Hızlı)

```bash
# Pytest ile (tests klasöründen)
cd tests
pytest . -m unit

# Python script ile
cd tests
python run_tests.py --unit

# Makefile ile
cd tests
make test-unit
```

### Integration Testler

```bash
# Pytest ile (tests klasöründen)
cd tests
pytest . -m integration

# Python script ile
cd tests
python run_tests.py --integration

# Makefile ile
cd tests
make test-integration
```

### Servise Göre Testler

```bash
# Auth service testleri (tests klasöründen)
cd tests
pytest . -m auth
# veya
python run_tests.py --auth
# veya
make test-auth

# Backend testleri
cd tests
pytest . -m backend
# veya
python run_tests.py --backend
# veya
make test-backend
```

### Coverage Raporu

```bash
# Pytest ile
pytest tests/ --cov=auth_service --cov=backend --cov-report=html

# Python script ile
python run_tests.py --coverage

# Makefile ile
make test-coverage
```

Coverage raporu `htmlcov/index.html` dosyasında oluşturulur.

## Test Markers

Tests/pytest.ini dosyasında tanımlı marker'lar:

- `@pytest.mark.unit` - Unit testler (hızlı, izole)
- `@pytest.mark.integration` - Integration testler (daha yavaş)
- `@pytest.mark.auth` - Auth service testleri
- `@pytest.mark.backend` - Backend testleri
- `@pytest.mark.slow` - Yavaş çalışan testler

### Marker Kombinasyonları

```bash
# Auth service unit testleri
pytest tests/ -m "unit and auth"

# Backend integration testleri
pytest tests/ -m "integration and backend"

# Yavaş testleri atla
pytest tests/ -m "not slow"
```

## Test Yazma Örnekleri

### Unit Test Örneği

```python
import pytest

@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    """Şifre hash ve verify işlemi"""
    from auth_service.utils.auth_utils import get_password_hash, verify_password
    
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
```

### Integration Test Örneği

```python
import pytest

@pytest.mark.integration
@pytest.mark.auth
def test_user_registration(auth_client):
    """Kullanıcı kayıt endpoint testi"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123"
    }
    
    response = auth_client.post("/api/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
```

## Fixtures

### Ortak Fixtures (conftest.py)

- `db_session_auth` - Auth service database session
- `db_session_backend` - Backend database session
- `auth_client` - Auth service test client
- `backend_client` - Backend test client
- `sample_user_data` - Örnek kullanıcı verisi
- `sample_drop_data` - Örnek drop verisi

### Kullanım

```python
def test_with_fixtures(auth_client, db_session_auth, sample_user_data):
    """Fixture kullanımı"""
    # auth_client ile API testleri
    response = auth_client.post("/api/auth/register", json=sample_user_data)
    
    # db_session_auth ile database işlemleri
    from models import User
    user = db_session_auth.query(User).first()
    assert user is not None
```

## Test Çıktısı

### Başarılı Test Çıktısı

```
============================= test session starts ==============================
platform linux -- Python 3.11.0
collected 45 items

tests/unit/test_auth_utils.py ..................                        [ 40%]
tests/unit/test_auth_models.py .......                                  [ 55%]
tests/integration/test_auth_endpoints.py ...............                [ 89%]
tests/integration/test_role_management.py .....                         [100%]

============================== 45 passed in 2.34s ===============================
```

### Coverage Raporu

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
auth_service/utils/auth_utils.py    87     12    86%   45-52, 89
auth_service/models.py              124      8    94%   67-74
backend/utils/security.py            56      5    91%   78-82
---------------------------------------------------------------
TOTAL                               267     25    91%
```

## Hata Ayıklama

### Verbose Mode

```bash
pytest tests/ -vv --tb=long
```

### İlk Hatada Dur

```bash
pytest tests/ -x
```

### Belirli Bir Test Çalıştır

```bash
pytest tests/unit/test_auth_utils.py::TestPasswordHashing::test_password_hashing
```

### Print Statements Göster

```bash
pytest tests/ -s
```

## CI/CD Entegrasyonu

GitHub Actions örneği:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=auth_service --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test İsimlendirme**: `test_` prefix kullan
2. **Descriptive Names**: Test adı ne test edildiğini açıklasın
3. **Arrange-Act-Assert**: Test yapısını düzenli tut
4. **Fixtures Kullan**: Tekrarı azalt
5. **Mock Kullanımı**: External servisleri mock'la
6. **Fast Tests**: Unit testleri hızlı tut
7. **Independent Tests**: Testler birbirinden bağımsız olmalı

## Sorun Giderme

### Database Connection Hatası

```bash
# Test veritabanlarının var olduğundan emin ol
docker-compose exec postgres psql -U postgres -l
```

### Import Hatası

```bash
# PYTHONPATH'i ayarla
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Fixture Not Found

conftest.py dosyasının doğru konumda olduğundan emin ol.

## Kaynaklar

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

