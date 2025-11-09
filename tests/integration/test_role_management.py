"""
Role Management Integration Tests
"""
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "auth_service"))

from models import User, Role, Permission
from utils.auth_utils import get_password_hash


@pytest.mark.integration
@pytest.mark.auth
class TestRoleEndpoints:
    """Rol yönetimi endpoint testleri"""
    
    @pytest.fixture
    def admin_user(self, auth_client, db_session_auth):
        """Admin kullanıcı ve token"""
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("AdminPass123"),
            is_superuser=True
        )
        db_session_auth.add(user)
        db_session_auth.commit()
        
        login_data = {"username": "admin", "password": "AdminPass123"}
        response = auth_client.post("/api/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        return {
            "user": user,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }
    
    @pytest.fixture
    def regular_user(self, auth_client, db_session_auth):
        """Normal kullanıcı"""
        user = User(
            email="user@example.com",
            username="regularuser",
            hashed_password=get_password_hash("UserPass123"),
            is_superuser=False
        )
        db_session_auth.add(user)
        db_session_auth.commit()
        
        login_data = {"username": "regularuser", "password": "UserPass123"}
        response = auth_client.post("/api/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        return {
            "user": user,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }
    
    @pytest.fixture
    def sample_role(self, db_session_auth):
        """Örnek rol"""
        role = Role(
            name="tester",
            display_name="Tester",
            description="Test role"
        )
        db_session_auth.add(role)
        db_session_auth.commit()
        return role
    
    def test_list_roles(self, auth_client, admin_user, sample_role):
        """Rolleri listele"""
        response = auth_client.get(
            "/api/roles/",
            headers=admin_user["headers"]
        )
        
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        assert len(roles) >= 1
    
    def test_create_role_as_admin(self, auth_client, admin_user):
        """Admin kullanıcı rol oluşturabilir"""
        role_data = {
            "name": "newrole",
            "display_name": "New Role",
            "description": "A new test role"
        }
        
        response = auth_client.post(
            "/api/roles/",
            json=role_data,
            headers=admin_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "newrole"
        assert data["display_name"] == "New Role"
    
    def test_create_role_as_regular_user(self, auth_client, regular_user):
        """Normal kullanıcı rol oluşturamaz"""
        role_data = {
            "name": "unauthorized",
            "display_name": "Unauthorized Role"
        }
        
        response = auth_client.post(
            "/api/roles/",
            json=role_data,
            headers=regular_user["headers"]
        )
        
        assert response.status_code == 403
    
    def test_assign_role_to_user(self, auth_client, admin_user, regular_user, sample_role, db_session_auth):
        """Kullanıcıya rol atama"""
        assign_data = {
            "user_id": regular_user["user"].id,
            "role_id": sample_role.id
        }
        
        response = auth_client.post(
            "/api/roles/assign",
            json=assign_data,
            headers=admin_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "atandı" in data["message"]
        
        # Kullanıcının rolü olduğunu kontrol et
        db_session_auth.refresh(regular_user["user"])
        assert sample_role in regular_user["user"].roles
    
    def test_assign_role_duplicate(self, auth_client, admin_user, regular_user, sample_role, db_session_auth):
        """Aynı rolü tekrar atamaya çalışma"""
        # İlk atama
        assign_data = {
            "user_id": regular_user["user"].id,
            "role_id": sample_role.id
        }
        auth_client.post("/api/roles/assign", json=assign_data, headers=admin_user["headers"])
        
        # İkinci atama (hata bekleniyor)
        response = auth_client.post("/api/roles/assign", json=assign_data, headers=admin_user["headers"])
        assert response.status_code == 400
        assert "zaten" in response.json()["detail"].lower()
    
    def test_remove_role_from_user(self, auth_client, admin_user, regular_user, sample_role, db_session_auth):
        """Kullanıcıdan rol kaldırma"""
        # Önce rol ata
        regular_user["user"].roles.append(sample_role)
        db_session_auth.commit()
        
        # Rolü kaldır
        remove_data = {
            "user_id": regular_user["user"].id,
            "role_id": sample_role.id
        }
        
        response = auth_client.post(
            "/api/roles/remove",
            json=remove_data,
            headers=admin_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "kaldırıldı" in data["message"]
        
        # Kullanıcının rolü olmadığını kontrol et
        db_session_auth.refresh(regular_user["user"])
        assert sample_role not in regular_user["user"].roles
    
    def test_get_user_permissions(self, auth_client, admin_user, regular_user, db_session_auth):
        """Kullanıcı yetkilerini getir"""
        # Permission ve Role oluştur
        perm1 = Permission(name="test.read", description="Read test")
        perm2 = Permission(name="test.write", description="Write test")
        db_session_auth.add_all([perm1, perm2])
        
        role = Role(name="testrole", display_name="Test Role")
        role.permissions.extend([perm1, perm2])
        db_session_auth.add(role)
        
        regular_user["user"].roles.append(role)
        db_session_auth.commit()
        
        # Yetkileri al
        response = auth_client.get(
            f"/api/roles/user/{regular_user['user'].id}",
            headers=admin_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) >= 1
        assert len(data["permissions"]) >= 2

