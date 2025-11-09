from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


# User-Role çoktan çoğa ilişki tablosu
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    """Rol tablosu - kullanıcı rolleri ve yetkileri"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Yetkiler
    can_create_drops = Column(Boolean, default=False)
    can_edit_drops = Column(Boolean, default=False)
    can_delete_drops = Column(Boolean, default=False)
    can_approve_claims = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=False)
    
    # Timestamp'ler
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class User(Base):
    """Kullanıcı tablosu"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamp alanları
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # İlişkiler
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    def has_permission(self, permission: str) -> bool:
        """Kullanıcının belirli bir yetkisi var mı kontrol et"""
        if self.is_superuser:
            return True
        
        for role in self.roles:
            if hasattr(role, permission) and getattr(role, permission):
                return True
        
        return False
    
    def get_permissions(self) -> dict:
        """Kullanıcının tüm yetkilerini döndür"""
        if self.is_superuser:
            return {
                "can_create_drops": True,
                "can_edit_drops": True,
                "can_delete_drops": True,
                "can_approve_claims": True,
                "can_manage_users": True,
                "can_view_analytics": True
            }
        
        permissions = {
            "can_create_drops": False,
            "can_edit_drops": False,
            "can_delete_drops": False,
            "can_approve_claims": False,
            "can_manage_users": False,
            "can_view_analytics": False
        }
        
        for role in self.roles:
            if role.can_create_drops:
                permissions["can_create_drops"] = True
            if role.can_edit_drops:
                permissions["can_edit_drops"] = True
            if role.can_delete_drops:
                permissions["can_delete_drops"] = True
            if role.can_approve_claims:
                permissions["can_approve_claims"] = True
            if role.can_manage_users:
                permissions["can_manage_users"] = True
            if role.can_view_analytics:
                permissions["can_view_analytics"] = True
        
        return permissions


class RefreshToken(Base):
    """Refresh token tablosu - token yenileme için"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(Text, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
