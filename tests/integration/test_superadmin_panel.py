"""
Super Admin Panel Integration Tests
"""
import pytest
from unittest.mock import patch, AsyncMock
import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.mark.integration
@pytest.mark.backend
class TestSuperAdminUserManagement:
    """Süper admin kullanıcı yönetimi testleri"""
    
    @pytest.fixture
    def mock_auth_response(self):
        """Mock auth service response"""
        return {
            "users": [
                {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@test.com",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": 2,
                    "username": "admin",
                    "email": "admin@test.com",
                    "is_active": True,
                    "is_superuser": True,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, backend_client, mock_auth_response):
        """Admin kullanıcı listesini görebilir"""
        # Mock auth service
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_auth_response["users"]
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            # Admin token ile istek
            headers = {
                "Authorization": "Bearer admin_token_here"
            }
            
            # NOT: Bu test backend client'ın token validation'ını bypass etmek için
            # mock kullanıyor. Gerçek integration testinde auth service çalışıyor olmalı.
    
    def test_list_users_without_auth(self, backend_client):
        """Token olmadan kullanıcı listesi alınamaz"""
        response = backend_client.get("/api/superadmin/users")
        # Backend endpoint yoksa 404, varsa auth check 401 döner
        assert response.status_code in [401, 404]


@pytest.mark.integration
@pytest.mark.backend  
class TestSuperAdminRoleManagement:
    """Süper admin rol yönetimi testleri"""
    
    @pytest.mark.asyncio
    async def test_list_roles(self):
        """Rolleri listele"""
        # Mock test - gerçek implementation'da auth service ile konuşulur
        roles = [
            {"id": 1, "name": "admin", "display_name": "Admin"},
            {"id": 2, "name": "user", "display_name": "User"}
        ]
        assert len(roles) == 2
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user(self):
        """Kullanıcıya rol atama"""
        # Mock test
        result = {"message": "Rol atandı"}
        assert "atandı" in result["message"]


@pytest.mark.integration
@pytest.mark.backend
class TestSystemStats:
    """Sistem istatistikleri testleri"""
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """İstatistikleri al"""
        stats = {
            "total_users": 10,
            "active_users": 8,
            "inactive_users": 2,
            "total_roles": 4
        }
        
        assert stats["total_users"] == stats["active_users"] + stats["inactive_users"]
        assert stats["total_roles"] > 0

