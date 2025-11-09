"""
DropSpot AI Service - Gemini-based RAG Chatbot
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import structlog
from datetime import datetime

from config import settings
from routers import chat
from schemas import HealthResponse

# Structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

app = FastAPI(
    title="DropSpot AI Service",
    description="Gemini-based RAG Chatbot for DropSpot Platform",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info(
        "ai_service_starting",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        port=settings.PORT,
        gemini_model=settings.GEMINI_MODEL
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("ai_service_shutting_down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "running",
        "description": "Gemini-based RAG Chatbot",
        "endpoints": {
            "docs": "/docs",
            "chat": "/api/chat/ask",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    try:
        # Gemini API kontrolü
        from services.gemini_service import gemini_service
        gemini_healthy = await gemini_service.check_health()
        gemini_status = "healthy" if gemini_healthy else "unhealthy"
        
        # Backend servis kontrolü
        backend_status = "unknown"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.BACKEND_SERVICE_URL}/health",
                    timeout=3.0
                )
                backend_status = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            backend_status = "unreachable"
        
        # Genel durum
        overall_status = "healthy" if gemini_healthy and backend_status == "healthy" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            service=settings.SERVICE_NAME,
            version=settings.VERSION,
            gemini_status=gemini_status,
            backend_status=backend_status
        )
        
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )

