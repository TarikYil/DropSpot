from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from database import engine, Base, get_db
from routers import auth, roles
import os

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="DropSpot Auth Service",
    description="Modern ve güvenli kimlik doğrulama servisi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(roles.router, prefix="/api/roles", tags=["Roles & Permissions"])


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
    from sqlalchemy import text
    try:
        # Veritabanı bağlantısını test et
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

