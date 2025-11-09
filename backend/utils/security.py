from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
import httpx
from typing import Optional

# Auth servisi URL'i
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")

# JWT ayarları (auth servisi ile aynı olmalı)
SECRET_KEY = os.getenv("SECRET_KEY", "dropspot-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"

# OAuth2 şeması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVICE_URL}/api/auth/login")


def decode_token(token: str) -> dict:
    """Token'ı decode eder ve içeriğini döner"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz veya süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Mevcut kullanıcıyı token'dan alır
    
    Returns:
        dict: {"user_id": int, "username": str, "is_superuser": bool}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama bilgileri doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        is_superuser: bool = payload.get("is_superuser", False)
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # Token'dan gelen bilgileri kullan
        return {
            "user_id": user_id,
            "username": username,
            "is_superuser": is_superuser
        }
        
    except JWTError:
        raise credentials_exception


async def get_current_user_with_details(token: str = Depends(oauth2_scheme)) -> dict:
    """Auth servisinden tam kullanıcı bilgilerini getirir"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "user_id": user_data.get("id"),
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "is_superuser": user_data.get("is_superuser", False),
                    "is_active": user_data.get("is_active", True)
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Kullanıcı bilgileri alınamadı"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth servisi ile bağlantı kurulamadı"
        )


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Admin yetkisi kontrolü yapar"""
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için admin yetkisi gereklidir"
        )
    return current_user


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """İki nokta arasındaki mesafeyi hesaplar (Haversine formülü)
    
    Returns:
        float: Mesafe (metre cinsinden)
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Dünya yarıçapı (metre)
    R = 6371000
    
    # Dereceleri radyana çevir
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    # Haversine formülü
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

