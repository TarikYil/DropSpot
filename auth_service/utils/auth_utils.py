from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

# Şifreleme ayarları
# Argon2 kullanıyoruz - modern, güvenli ve bcrypt'ten daha hızlı
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT ayarları
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-use-strong-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# OAuth2 şeması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrular"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Şifreyi hashler"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Access token oluşturur"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Refresh token oluşturur"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Token'ı decode eder ve içeriğini döner"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token claims hatası: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token decode hatası: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(db: Session, token: str):
    """Mevcut kullanıcıyı token'dan alır
    
    Args:
        db: Database session
        token: JWT token string
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from models import User
    from schemas import TokenData
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama bilgileri doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Token'ı decode et (decode_token zaten HTTPException fırlatıyor)
    payload = decode_token(token)
    user_id_str: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id_str is None or token_type != "access":
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
        
    token_data = TokenData(user_id=user_id)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı hesabı deaktif"
        )
    
    return user


def validate_password_strength(password: str) -> bool:
    """Şifre güçlülüğünü kontrol eder"""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Şifre en az 8 karakter olmalıdır"
        )
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Şifre en az bir büyük harf, bir küçük harf ve bir rakam içermelidir"
        )
    
    return True
