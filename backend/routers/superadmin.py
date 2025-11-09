"""
Süper Admin Paneli
Kullanıcı yönetimi, rol atama ve sistem kontrolleri için endpoint'ler
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import httpx
import os

from database import get_db
from utils.security import require_admin
from schemas import (
    MessageResponse,
    UserListResponse,
    UserRoleAssignRequest,
    RoleListResponse,
    UserDetailResponse
)

router = APIRouter()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")


@router.get("/users", response_model=List[UserListResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Tüm kullanıcıları listele (Sadece süper admin)
    
    - **skip**: Kaç kullanıcı atlanacak (pagination)
    - **limit**: Max kaç kullanıcı dönecek
    - **is_active**: Sadece aktif veya pasif kullanıcıları filtrele
    """
    try:
        # Auth servisinden kullanıcıları al
        params = {"skip": skip, "limit": limit}
        if is_active is not None:
            params["is_active"] = is_active
            
        async with httpx.AsyncClient() as client:
            # Admin token'ını kullan (burada current_user'dan alıyoruz)
            headers = {"Authorization": f"Bearer {current_user.get('token')}"}
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/users",
                params=params,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            users = response.json()
            
        return users
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    current_user: dict = Depends(require_admin)
):
    """
    Belirli bir kullanıcının detaylı bilgilerini getir (Sadece süper admin)
    Kullanıcının rollerini ve yetkilerini de içerir
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {current_user.get('token')}"}
            
            # Kullanıcı bilgileri
            user_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/users/{user_id}",
                headers=headers,
                timeout=10.0
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Kullanıcının rolleri ve yetkileri
            roles_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/roles/user/{user_id}",
                headers=headers,
                timeout=10.0
            )
            roles_response.raise_for_status()
            roles_data = roles_response.json()
            
            # Birleştir
            user_data.update({
                "roles": roles_data.get("roles", []),
                "permissions": roles_data.get("permissions", [])
            })
            
        return user_data
        
    except httpx.HTTPError as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    permanent: bool = Query(False, description="Kalıcı olarak sil (True) veya sadece deaktif et (False)"),
    current_user: dict = Depends(require_admin)
):
    """
    Kullanıcıyı sil veya deaktif et (Sadece süper admin)
    
    - **permanent=False**: Kullanıcıyı sadece deaktif eder (soft delete)
    - **permanent=True**: Kullanıcıyı kalıcı olarak siler (dikkatli kullanın!)
    """
    try:
        # Kendi hesabını silemez
        if current_user.get("user_id") == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kendi hesabınızı silemezsiniz"
            )
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {current_user.get('token')}"}
            
            if permanent:
                # Kalıcı silme - auth servisinde endpoint varsa
                response = await client.delete(
                    f"{AUTH_SERVICE_URL}/api/auth/users/{user_id}?permanent=true",
                    headers=headers,
                    timeout=10.0
                )
            else:
                # Soft delete - kullanıcıyı deaktif et
                response = await client.delete(
                    f"{AUTH_SERVICE_URL}/api/auth/users/{user_id}",
                    headers=headers,
                    timeout=10.0
                )
            
            response.raise_for_status()
            result = response.json()
            
        action = "kalıcı olarak silindi" if permanent else "deaktif edildi"
        return {
            "message": f"Kullanıcı #{user_id} {action}",
            "details": result
        }
        
    except httpx.HTTPError as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.get("/roles", response_model=List[RoleListResponse])
async def list_all_roles(
    current_user: dict = Depends(require_admin)
):
    """
    Tüm rolleri listele (Sadece süper admin)
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {current_user.get('token')}"}
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/roles/",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            roles = response.json()
            
        return roles
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.post("/roles", response_model=dict)
async def create_role(
    role_data: dict,
    current_user: dict = Depends(require_admin)
):
    """
    Yeni rol oluştur (Sadece süper admin)
    
    Request body:
    ```json
    {
        "name": "moderator",
        "display_name": "Moderatör",
        "description": "İçerik moderatörü"
    }
    ```
    """
    # Token kontrolü
    token = current_user.get('token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bulunamadı"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/roles/",
                headers=headers,
                json=role_data,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
        return result
        
    except httpx.HTTPStatusError as e:
        error_detail = "Bilinmeyen hata"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("detail", str(e))
        except:
            error_detail = str(e)
        
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        elif e.response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail or "Bu işlem için yetkiniz yok"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth servisi hatası: {error_detail}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.delete("/roles/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(require_admin)
):
    """
    Rolü sil (Sadece süper admin)
    """
    # Token kontrolü
    token = current_user.get('token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bulunamadı"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.delete(
                f"{AUTH_SERVICE_URL}/api/roles/{role_id}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
        return {"message": result.get("message", "Rol başarıyla silindi")}
        
    except httpx.HTTPStatusError as e:
        error_detail = "Bilinmeyen hata"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("detail", str(e))
        except:
            error_detail = str(e)
        
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail or "Rol bulunamadı"
            )
        elif e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        elif e.response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail or "Bu işlem için yetkiniz yok"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth servisi hatası: {error_detail}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.post("/users/{user_id}/roles", response_model=MessageResponse)
async def assign_role_to_user(
    user_id: int,
    role_data: UserRoleAssignRequest,
    current_user: dict = Depends(require_admin)
):
    """
    Kullanıcıya rol ata (Sadece süper admin)
    
    Request body:
    ```json
    {
        "role_id": 1
    }
    ```
    """
    # Token kontrolü
    token = current_user.get('token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bulunamadı"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/roles/assign",
                headers=headers,
                json={"user_id": user_id, "role_id": role_data.role_id},
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
        return {"message": result.get("message", "Rol başarıyla atandı")}
        
    except httpx.HTTPStatusError as e:
        # HTTP hata kodları için detaylı mesaj
        error_detail = "Bilinmeyen hata"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("detail", str(e))
        except:
            error_detail = str(e)
        
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail or "Kullanıcı veya rol bulunamadı"
            )
        elif e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        elif e.response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail or "Bu işlem için yetkiniz yok"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth servisi hatası: {error_detail}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.delete("/users/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: dict = Depends(require_admin)
):
    """
    Kullanıcıdan rol kaldır (Sadece süper admin)
    """
    # Token kontrolü
    token = current_user.get('token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bulunamadı"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/roles/remove",
                headers=headers,
                json={"user_id": user_id, "role_id": role_id},
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
        return {"message": result.get("message", "Rol başarıyla kaldırıldı")}
        
    except httpx.HTTPStatusError as e:
        # HTTP hata kodları için detaylı mesaj
        error_detail = "Bilinmeyen hata"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("detail", str(e))
        except:
            error_detail = str(e)
        
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail or "Kullanıcı veya rol bulunamadı"
            )
        elif e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        elif e.response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail or "Bu işlem için yetkiniz yok"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth servisi hatası: {error_detail}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth servisi ile iletişim kurulamadı: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_system_stats(
    current_user: dict = Depends(require_admin)
):
    """
    Sistem istatistiklerini getir (Sadece süper admin)
    
    - Toplam kullanıcı sayısı
    - Aktif kullanıcı sayısı
    - Toplam rol sayısı
    - Son kayıt olan kullanıcılar
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {current_user.get('token')}"}
            
            # Kullanıcıları al
            users_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/users?limit=1000",
                headers=headers,
                timeout=10.0
            )
            users_response.raise_for_status()
            users = users_response.json()
            
            # Rolleri al
            roles_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/roles/",
                headers=headers,
                timeout=10.0
            )
            roles_response.raise_for_status()
            roles = roles_response.json()
            
        # İstatistikleri hesapla
        total_users = len(users)
        active_users = sum(1 for u in users if u.get("is_active", False))
        total_roles = len(roles)
        
        # Son kayıt olan 5 kullanıcı
        recent_users = sorted(
            users,
            key=lambda u: u.get("created_at", ""),
            reverse=True
        )[:5]
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "total_roles": total_roles,
            "recent_users": recent_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"İstatistikler alınamadı: {str(e)}"
        )

