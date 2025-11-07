from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import User, RefreshToken
from schemas import (
    UserCreate, UserResponse, UserInDB, Token, 
    LoginRequest, RefreshTokenRequest, MessageResponse,
    PasswordReset, UserUpdate
)
from utils.auth_utils import (
    get_password_hash, verify_password, 
    create_access_token, create_refresh_token,
    decode_token, get_current_user, oauth2_scheme,
    validate_password_strength,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""
    
    # Email kontrolü
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Username kontrolü
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    
    # Şifre güçlülük kontrolü
    validate_password_strength(user_data.password)
    
    # Yeni kullanıcı oluştur
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Kullanıcı girişi - email veya username ile"""
    
    # Email veya username ile kullanıcıyı bul
    user = db.query(User).filter(
        (User.email == login_data.username) | (User.username == login_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Şifre kontrolü
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcı aktif mi kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı hesabı deaktif"
        )
    
    # Token'ları oluştur
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "is_superuser": user.is_superuser}
    )
    refresh_token_str = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Refresh token'ı veritabanına kaydet
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token_record)
    
    # Son giriş zamanını güncelle
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh token ile yeni access token al"""
    
    try:
        # Token'ı decode et
        payload = decode_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz token türü"
            )
        
        # Veritabanında token'ı kontrol et
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_data.refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token geçersiz veya iptal edilmiş"
            )
        
        # Token süresi dolmuş mu kontrol et
        if db_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token süresi dolmuş"
            )
        
        # Kullanıcıyı al
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı bulunamadı veya aktif değil"
            )
        
        # Yeni token'ları oluştur
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "is_superuser": user.is_superuser}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Eski refresh token'ı iptal et
        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()
        
        # Yeni refresh token'ı kaydet
        new_token_record = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_token_record)
        db.commit()
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token işleme hatası"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcı çıkışı - refresh token'ı iptal et"""
    current_user = get_current_user(db, token)
    
    # Refresh token'ı iptal et
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if db_token and not db_token.revoked:
        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()
        db.commit()
    
    return MessageResponse(message="Başarıyla çıkış yapıldı")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Mevcut kullanıcı bilgilerini getir"""
    current_user = get_current_user(db, token)
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Kullanıcı bilgilerini güncelle"""
    current_user = get_current_user(db, token)
    
    # Email güncellemesi varsa, benzersiz mi kontrol et
    if user_update.email and user_update.email != current_user.email:
        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email adresi zaten kullanılıyor"
            )
        current_user.email = user_update.email
    
    # Username güncellemesi varsa, benzersiz mi kontrol et
    if user_update.username and user_update.username != current_user.username:
        existing_username = db.query(User).filter(User.username == user_update.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu kullanıcı adı zaten kullanılıyor"
            )
        current_user.username = user_update.username
    
    # Full name güncellemesi
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    # Şifre güncellemesi
    if user_update.password:
        validate_password_strength(user_update.password)
        current_user.hashed_password = get_password_hash(user_update.password)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordReset,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Şifre değiştir"""
    current_user = get_current_user(db, token)
    
    # Eski şifreyi doğrula
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mevcut şifre hatalı"
        )
    
    # Yeni şifre güçlülük kontrolü
    validate_password_strength(password_data.new_password)
    
    # Şifreyi güncelle
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Şifre başarıyla değiştirildi")


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Hesabı sil (soft delete - is_active = False)"""
    current_user = get_current_user(db, token)
    
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    
    # Tüm refresh token'ları iptal et
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).all()
    
    for token in tokens:
        token.revoked = True
        token.revoked_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(message="Hesap başarıyla deaktif edildi")


# Admin endpoints
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Tüm kullanıcıları listele (Sadece admin)"""
    current_user = get_current_user(db, token)
    
    # Superuser kontrolü
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yetersiz yetki. Superuser erişimi gerekli."
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Belirli bir kullanıcıyı getir (Sadece admin)"""
    current_user = get_current_user(db, token)
    
    # Superuser kontrolü
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yetersiz yetki. Superuser erişimi gerekli."
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    return user

