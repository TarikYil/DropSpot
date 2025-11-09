"""
Pytest Fixtures - Tüm testler için ortak fixture'lar
"""
import sys
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Auth service ve backend'i path'e ekle
auth_service_path = Path(__file__).parent.parent / "auth_service"
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(auth_service_path))
sys.path.insert(0, str(backend_path))


# Test database URL'leri
TEST_AUTH_DATABASE_URL = os.getenv(
    "TEST_AUTH_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_auth_db"
)
TEST_BACKEND_DATABASE_URL = os.getenv(
    "TEST_BACKEND_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_dropspot_db"
)


@pytest.fixture(scope="session")
def test_db_engine_auth():
    """Auth service test database engine"""
    # Import auth service modüllerini sys.path'ten
    sys.path.insert(0, str(auth_service_path))
    from database import Base as AuthBase
    sys.path.remove(str(auth_service_path))
    
    engine = create_engine(TEST_AUTH_DATABASE_URL)
    AuthBase.metadata.create_all(bind=engine)
    yield engine
    AuthBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def test_db_engine_backend():
    """Backend test database engine"""
    # Import backend modüllerini sys.path'ten
    sys.path.insert(0, str(backend_path))
    from database import Base as BackendBase
    sys.path.remove(str(backend_path))
    
    engine = create_engine(TEST_BACKEND_DATABASE_URL)
    BackendBase.metadata.create_all(bind=engine)
    yield engine
    BackendBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session_auth(test_db_engine_auth):
    """Her test için temiz auth database session"""
    from sqlalchemy import text
    TestSessionLocal = sessionmaker(bind=test_db_engine_auth)
    session = TestSessionLocal()
    
    yield session
    
    # Test sonrası cleanup
    session.rollback()
    
    # Tüm tabloları temizle (foreign key'ler için sıralı)
    try:
        session.execute(text("TRUNCATE TABLE user_roles CASCADE"))
        session.execute(text("TRUNCATE TABLE role_permissions CASCADE"))
        session.execute(text("TRUNCATE TABLE refresh_tokens CASCADE"))
        session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        session.execute(text("TRUNCATE TABLE roles RESTART IDENTITY CASCADE"))
        session.execute(text("TRUNCATE TABLE permissions RESTART IDENTITY CASCADE"))
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@pytest.fixture(scope="function")
def db_session_backend(test_db_engine_backend):
    """Her test için temiz backend database session"""
    TestSessionLocal = sessionmaker(bind=test_db_engine_backend)
    session = TestSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture
def auth_client(db_session_auth):
    """Auth service test client"""
    sys.path.insert(0, str(auth_service_path))
    from main import app
    from database import get_db
    sys.path.remove(str(auth_service_path))
    
    def override_get_db():
        try:
            yield db_session_auth
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def backend_client(db_session_backend):
    """Backend service test client"""
    sys.path.insert(0, str(backend_path))
    from main import app
    from database import get_db
    sys.path.remove(str(backend_path))
    
    def override_get_db():
        try:
            yield db_session_backend
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Örnek kullanıcı verisi"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_drop_data():
    """Örnek drop verisi"""
    from datetime import datetime, timedelta
    
    return {
        "title": "Test Drop",
        "description": "Test drop description",
        "total_quantity": 100,
        "latitude": 41.0082,
        "longitude": 28.9784,
        "address": "Istanbul, Turkey",
        "radius_meters": 500,
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }


# Pytest configuration
def pytest_configure(config):
    """Pytest konfigürasyonu"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "auth: Auth service tests")
    config.addinivalue_line("markers", "backend: Backend service tests")

