"""
Auth utilities for AI Service
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/api/auth/login", auto_error=False)


def decode_token(token: str) -> dict:
    """JWT token'ı decode et"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz veya süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """Mevcut kullanıcıyı al (opsiyonel)"""
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        username: str = payload.get("username")
        is_superuser: bool = payload.get("is_superuser", False)
        
        if user_id_str is None:
            return None
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None
        
        return {
            "user_id": user_id,
            "username": username,
            "is_superuser": is_superuser,
            "token": token
        }
    except HTTPException:
        return None

