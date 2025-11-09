from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from database import engine, Base, get_db, SessionLocal
from routers import auth
from models import User
from utils.auth_utils import get_password_hash
import os

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)


def create_default_admin_if_not_exists():
    """Default admin kullanıcısını oluştur (yoksa)"""
    db = SessionLocal()
    try:
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        full_name = os.getenv("ADMIN_FULL_NAME", "Default Admin")
        
        # Kullanıcı zaten var mı kontrol et
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            # Kullanıcı varsa, superuser yap ve bilgileri güncelle
            existing_user.is_superuser = True
            existing_user.is_active = True
            existing_user.is_verified = True
            existing_user.hashed_password = get_password_hash(password)
            if existing_user.full_name != full_name:
                existing_user.full_name = full_name
            db.commit()
            print(f"✅ Default admin kullanıcısı güncellendi: {username}")
        else:
            # Yeni kullanıcı oluştur
            hashed_password = get_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                is_active=True,
                is_superuser=True,
                is_verified=True
            )
            db.add(new_user)
            db.commit()
            print(f"✅ Default admin kullanıcısı oluşturuldu: {username}")
    except Exception as e:
        print(f"❌ Default admin oluşturulurken hata: {str(e)}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup ve shutdown event'leri"""
    # Startup
    print("🚀 Auth Service başlatılıyor...")
    create_default_admin_if_not_exists()
    yield
    # Shutdown
    print("🛑 Auth Service kapatılıyor...")


# FastAPI uygulamasını oluştur
app = FastAPI(
    title="DropSpot Auth Service",
    description="Modern ve güvenli kimlik doğrulama servisi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domainler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları dahil et
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint - servis sağlık kontrolü"""
    return {
        "service": "DropSpot Auth Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Sağlık kontrolü endpoint'i - veritabanı bağlantısını da kontrol eder"""
    try:
        # Veritabanı bağlantısını test et
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

