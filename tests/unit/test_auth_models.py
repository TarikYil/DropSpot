"""
Auth Service Models Unit Tests
"""
import pytest
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "auth_service"))

from models import User, Role, Permission


@pytest.mark.unit
@pytest.mark.auth
class TestUserModel:
    """User model testleri"""
    
    def test_user_creation(self, db_session_auth):
        """Kullanıcı oluşturma"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            full_name="Test User"
        )
        
        db_session_auth.add(user)
        db_session_auth.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
    
    def test_user_has_permission_superuser(self, db_session_auth):
        """Superuser tüm yetkilere sahip"""
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hash",
            is_superuser=True
        )
        
        db_session_auth.add(user)
        db_session_auth.commit()
        
        # Superuser her yetkiye sahip olmalı
        assert user.has_permission("any.permission") is True
        assert user.has_permission("drop.create") is True
    
    def test_user_has_permission_via_role(self, db_session_auth):
        """Kullanıcı rol üzerinden yetkiye sahip"""
        # Permission oluştur
        perm = Permission(name="drop.create", description="Create drops")
        db_session_auth.add(perm)
        
        # Role oluştur
        role = Role(name="creator", display_name="Creator")
        role.permissions.append(perm)
        db_session_auth.add(role)
        
        # User oluştur
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hash"
        )
        user.roles.append(role)
        db_session_auth.add(user)
        db_session_auth.commit()
        
        assert user.has_permission("drop.create") is True
        assert user.has_permission("drop.delete") is False


@pytest.mark.unit
@pytest.mark.auth
class TestRoleModel:
    """Role model testleri"""
    
    def test_role_creation(self, db_session_auth):
        """Rol oluşturma"""
        role = Role(
            name="moderator",
            display_name="Moderator",
            description="Moderator role"
        )
        
        db_session_auth.add(role)
        db_session_auth.commit()
        
        assert role.id is not None
        assert role.name == "moderator"
        assert role.created_at is not None
    
    def test_role_with_permissions(self, db_session_auth):
        """Yetkilerle birlikte rol"""
        perm1 = Permission(name="drop.read_test", description="Read drops")
        perm2 = Permission(name="drop.update_test", description="Update drops")
        
        role = Role(name="creator_test", display_name="Creator Test")
        role.permissions.extend([perm1, perm2])
        
        db_session_auth.add(role)
        db_session_auth.commit()
        
        assert len(role.permissions) == 2
        assert perm1 in role.permissions
        assert perm2 in role.permissions


@pytest.mark.unit
@pytest.mark.auth
class TestPermissionModel:
    """Permission model testleri"""
    
    def test_permission_creation(self, db_session_auth):
        """Yetki oluşturma"""
        perm = Permission(
            name="drop.delete_test",
            description="Can delete drops"
        )
        
        db_session_auth.add(perm)
        db_session_auth.commit()
        
        assert perm.id is not None
        assert perm.name == "drop.delete_test"
        assert perm.description == "Can delete drops"

