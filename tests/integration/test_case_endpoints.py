"""
Case formatına uygun endpoint'ler için integration testleri
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Backend path'i ekle
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models import Drop, Waitlist, Claim, DropStatus, ClaimStatus
from tests.conftest import backend_client, db_session_backend, db_session_auth

# Auth service path'i
auth_service_path = Path(__file__).parent.parent.parent / "auth_service"


@pytest.fixture
def auth_token():
    """Test için JWT token oluştur (backend'in SECRET_KEY'ini kullanarak)"""
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    
    # Backend'in SECRET_KEY'i ile token oluştur
    SECRET_KEY = "dropspot-super-secret-key-change-in-production-2024"
    ALGORITHM = "HS256"
    
    # Token payload
    user_id = 1
    username = "testuser"
    is_superuser = False
    
    # Token expire time (30 dakika)
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    # JWT payload
    payload = {
        "sub": str(user_id),  # Backend string bekliyor
        "username": username,
        "is_superuser": is_superuser,
        "type": "access",
        "exp": expire
    }
    
    # Token oluştur
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


@pytest.fixture
def test_drop(db_session_backend: Session):
    """Test drop oluştur"""
    now = datetime.now(timezone.utc)
    drop = Drop(
        title="Test Drop",
        description="Test açıklama",
        total_quantity=100,
        claimed_quantity=0,
        remaining_quantity=100,
        latitude=41.0082,
        longitude=28.9784,
        address="Test Adres",
        radius_meters=1000,
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=1),
        status=DropStatus.ACTIVE,
        is_active=True,
        created_by=1
    )
    db_session_backend.add(drop)
    db_session_backend.commit()
    db_session_backend.refresh(drop)
    return drop


@pytest.mark.integration
@pytest.mark.backend
class TestCaseFormatEndpoints:
    """Case formatına uygun endpoint testleri"""
    
    def test_post_drops_id_join(self, backend_client: TestClient, auth_token: str, test_drop: Drop):
        """Test POST /api/drops/{drop_id}/join"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Join
        response = backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}, {response.text}"
        data = response.json()
        assert data["drop_id"] == test_drop.id
        assert "user_id" in data
        assert "created_at" in data
    
    def test_post_drops_id_join_idempotent(self, backend_client: TestClient, auth_token: str, test_drop: Drop):
        """Test POST /api/drops/{drop_id}/join idempotent"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # İlk join
        response1 = backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        assert response1.status_code in [200, 201]
        
        # İkinci join (idempotent olmalı)
        response2 = backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        assert response2.status_code in [200, 201]
        
        # Aynı kayıt dönmeli
        assert response1.json()["id"] == response2.json()["id"]
    
    def test_post_drops_id_leave(self, backend_client: TestClient, auth_token: str, test_drop: Drop):
        """Test POST /api/drops/{drop_id}/leave"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Önce join
        backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        
        # Leave
        response = backend_client.post(
            f"/api/drops/{test_drop.id}/leave",
            headers=headers
        )
        
        assert response.status_code == 200, f"Unexpected status: {response.status_code}, {response.text}"
        data = response.json()
        assert "message" in data
    
    def test_post_drops_id_claim(self, backend_client: TestClient, auth_token: str, test_drop: Drop):
        """Test POST /api/drops/{drop_id}/claim"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Önce join
        backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        
        # Claim
        claim_data = {
            "quantity": 1,
            "claim_latitude": 41.0082,
            "claim_longitude": 28.9784
        }
        
        response = backend_client.post(
            f"/api/drops/{test_drop.id}/claim",
            headers=headers,
            json=claim_data
        )
        
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}, {response.text}"
        data = response.json()
        assert data["drop_id"] == test_drop.id
        assert data["status"] == ClaimStatus.PENDING
        assert "verification_code" in data
    
    def test_post_drops_id_claim_idempotent(self, backend_client: TestClient, auth_token: str, test_drop: Drop):
        """Test POST /api/drops/{drop_id}/claim idempotent"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Önce join
        backend_client.post(
            f"/api/drops/{test_drop.id}/join",
            headers=headers
        )
        
        claim_data = {
            "quantity": 1,
            "claim_latitude": 41.0082,
            "claim_longitude": 28.9784
        }
        
        # İlk claim
        response1 = backend_client.post(
            f"/api/drops/{test_drop.id}/claim",
            headers=headers,
            json=claim_data
        )
        assert response1.status_code in [200, 201]
        
        # İkinci claim (idempotent olmalı)
        response2 = backend_client.post(
            f"/api/drops/{test_drop.id}/claim",
            headers=headers,
            json=claim_data
        )
        assert response2.status_code in [200, 201]
        
        # Aynı claim dönmeli
        assert response1.json()["id"] == response2.json()["id"]
    
    def test_post_drops_id_claim_stock_check(self, backend_client: TestClient, auth_token: str, db_session_backend: Session):
        """Test POST /api/drops/{drop_id}/claim stok kontrolü"""
        if not auth_token:
            pytest.skip("Auth token alınamadı")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Stok bitmiş drop oluştur
        now = datetime.now(timezone.utc)
        drop = Drop(
            title="Stok Bitmiş Drop",
            description="Test",
            total_quantity=1,
            claimed_quantity=1,
            remaining_quantity=0,
            latitude=41.0082,
            longitude=28.9784,
            address="Test",
            radius_meters=1000,
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            status=DropStatus.ACTIVE,
            is_active=True,
            created_by=1
        )
        db_session_backend.add(drop)
        db_session_backend.commit()
        db_session_backend.refresh(drop)
        
        # Join
        backend_client.post(
            f"/api/drops/{drop.id}/join",
            headers=headers
        )
        
        # Claim (stok bitmiş, 403 dönmeli)
        claim_data = {
            "quantity": 1,
            "claim_latitude": 41.0082,
            "claim_longitude": 28.9784
        }
        
        response = backend_client.post(
            f"/api/drops/{drop.id}/claim",
            headers=headers,
            json=claim_data
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

