from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Role, User, user_roles
from schemas import (
    RoleCreate, RoleUpdate, RoleResponse, MessageResponse,
    UserRoleAssign, UserRoleRemove, UserWithPermissions
)
from utils.auth_utils import get_current_user, oauth2_scheme

router = APIRouter()


def require_permission(permission: str):
    """Belirli bir yetkinin olup olmadığını kontrol eden decorator fonksiyon"""
    async def permission_checker(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ):
        current_user = get_current_user(db, token)
        
        if not current_user.is_superuser and not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için '{permission}' yetkisi gereklidir"
            )
        
        return current_user
    
    return permission_checker


# Role CRUD - Sadece superuser
@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Yeni rol oluştur (Sadece superuser)"""
    current_user = get_current_user(db, token)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece superuser rol oluşturabilir"
        )
    
    # Rol adı benzersiz mi kontrol et
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu isimde bir rol zaten mevcut"
        )
    
    # Yeni rol oluştur
    new_role = Role(**role_data.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return new_role


@router.get("/", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Tüm rolleri listele"""
    current_user = get_current_user(db, token)  # Auth kontrolü
    
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Belirli bir rolün detaylarını getir"""
    current_user = get_current_user(db, token)  # Auth kontrolü
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Rolü güncelle (Sadece superuser)"""
    current_user = get_current_user(db, token)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece superuser rol güncelleyebilir"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # Güncelle
    for field, value in role_data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    
    role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(role)
    
    return role


@router.delete("/{role_id}", response_model=MessageResponse)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Rolü sil (Sadece superuser)"""
    current_user = get_current_user(db, token)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece superuser rol silebilir"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    db.delete(role)
    db.commit()
    
    return MessageResponse(
        message="Rol başarıyla silindi",
        detail=f"Role: {role.name}"
    )


# User-Role Assignment
@router.post("/users/{user_id}/assign", response_model=MessageResponse)
def assign_role_to_user(
    user_id: int,
    role_data: UserRoleAssign,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcıya rol ata"""
    current_user = get_current_user(db, token)
    
    if not current_user.is_superuser and not current_user.has_permission("can_manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı yönetimi yetkisi gereklidir"
        )
    
    # Kullanıcı kontrolü
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Rol kontrolü
    role = db.query(Role).filter(Role.id == role_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # Zaten bu role sahip mi?
    if role in user.roles:
        return MessageResponse(
            message="Kullanıcı zaten bu role sahip",
            detail=f"User: {user.username}, Role: {role.name}"
        )
    
    # Rolü ata
    user.roles.append(role)
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(
        message="Rol başarıyla atandı",
        detail=f"User: {user.username}, Role: {role.name}"
    )


@router.post("/users/{user_id}/remove", response_model=MessageResponse)
def remove_role_from_user(
    user_id: int,
    role_data: UserRoleRemove,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcıdan rol kaldır"""
    current_user = get_current_user(db, token)
    
    if not current_user.is_superuser and not current_user.has_permission("can_manage_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı yönetimi yetkisi gereklidir"
        )
    
    # Kullanıcı kontrolü
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Rol kontrolü
    role = db.query(Role).filter(Role.id == role_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # Rolü kaldır
    if role in user.roles:
        user.roles.remove(role)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return MessageResponse(
            message="Rol başarıyla kaldırıldı",
            detail=f"User: {user.username}, Role: {role.name}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanıcı bu role sahip değil"
        )


@router.get("/users/{user_id}/permissions", response_model=UserWithPermissions)
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcının tüm yetkilerini getir"""
    current_user = get_current_user(db, token)
    
    # Sadece kendi yetkilerini veya superuser görebilir
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Başka kullanıcıların yetkilerini görme yetkiniz yok"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    permissions = user.get_permissions()
    
    return UserWithPermissions(
        **user.__dict__,
        permissions=permissions
    )

