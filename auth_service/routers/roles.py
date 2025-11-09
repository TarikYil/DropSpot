from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models import Role, User
from utils.auth_utils import get_current_user, oauth2_scheme

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: str = None
    can_create_drops: bool = False
    can_edit_drops: bool = False
    can_delete_drops: bool = False
    can_approve_claims: bool = False
    can_manage_users: bool = False
    can_view_analytics: bool = False


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str = None
    can_create_drops: bool
    can_edit_drops: bool
    can_delete_drops: bool
    can_approve_claims: bool
    can_manage_users: bool
    can_view_analytics: bool
    created_at: str = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Tüm rolleri listele (Admin gerekli)"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    roles = db.query(Role).all()
    # RoleResponse şeması için serialize et
    result = []
    for role in roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "can_create_drops": role.can_create_drops,
            "can_edit_drops": role.can_edit_drops,
            "can_delete_drops": role.can_delete_drops,
            "can_approve_claims": role.can_approve_claims,
            "can_manage_users": role.can_manage_users,
            "can_view_analytics": role.can_view_analytics,
            "created_at": role.created_at.isoformat() if role.created_at else None
        }
        result.append(role_dict)
    return result


@router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Yeni rol oluştur (Superuser gerekli)"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    # Rol adı benzersiz mi kontrol et
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{role_data.name}' adında bir rol zaten mevcut"
        )
    
    new_role = Role(**role_data.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # RoleResponse şeması için serialize et
    return {
        "id": new_role.id,
        "name": new_role.name,
        "display_name": new_role.display_name,
        "description": new_role.description,
        "can_create_drops": new_role.can_create_drops,
        "can_edit_drops": new_role.can_edit_drops,
        "can_delete_drops": new_role.can_delete_drops,
        "can_approve_claims": new_role.can_approve_claims,
        "can_manage_users": new_role.can_manage_users,
        "can_view_analytics": new_role.can_view_analytics,
        "created_at": new_role.created_at.isoformat() if new_role.created_at else None
    }


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Rol detayı"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # RoleResponse şeması için serialize et
    return {
        "id": role.id,
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description,
        "can_create_drops": role.can_create_drops,
        "can_edit_drops": role.can_edit_drops,
        "can_delete_drops": role.can_delete_drops,
        "can_approve_claims": role.can_approve_claims,
        "can_manage_users": role.can_manage_users,
        "can_view_analytics": role.can_view_analytics,
        "created_at": role.created_at.isoformat() if role.created_at else None
    }


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Rol sil (Superuser gerekli)"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    db.delete(role)
    db.commit()
    
    return {"message": "Rol başarıyla silindi"}


class RoleAssignRequest(BaseModel):
    user_id: int
    role_id: int


@router.post("/assign")
async def assign_role(
    request: RoleAssignRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcıya rol ata (Superuser gerekli)"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # Rol zaten atanmış mı kontrol et
    if role in user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu rol zaten kullanıcıya atanmış"
        )
    
    user.roles.append(role)
    db.commit()
    
    return {"message": f"'{role.display_name}' rolü kullanıcıya başarıyla atandı"}


@router.post("/remove")
async def remove_role(
    request: RoleAssignRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcıdan rol kaldır (Superuser gerekli)"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol bulunamadı"
        )
    
    # Rol atanmış mı kontrol et
    if role not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu rol kullanıcıya atanmamış"
        )
    
    user.roles.remove(role)
    db.commit()
    
    return {"message": f"'{role.display_name}' rolü kullanıcıdan başarıyla kaldırıldı"}


@router.get("/user/{user_id}", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcının rollerini getir"""
    current_user = get_current_user(db, token)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Rolleri serialize et
    result = []
    for role in user.roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "can_create_drops": role.can_create_drops,
            "can_edit_drops": role.can_edit_drops,
            "can_delete_drops": role.can_delete_drops,
            "can_approve_claims": role.can_approve_claims,
            "can_manage_users": role.can_manage_users,
            "can_view_analytics": role.can_view_analytics,
            "created_at": role.created_at.isoformat() if role.created_at else None
        }
        result.append(role_dict)
    return result

