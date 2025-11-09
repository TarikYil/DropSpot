"""
AI Service Configuration
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AI Service ayarları"""
    
    # Service Info
    SERVICE_NAME: str = "DropSpot AI Service"
    VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("PORT", 8004))
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyCjy1PrC-Sqbs5ELXnQpH94Z3i3WU_Yppg")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Backend Services
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
    BACKEND_SERVICE_URL: str = os.getenv("BACKEND_SERVICE_URL", "http://backend:8002")
    
    # RAG Settings
    MAX_CONTEXT_LENGTH: int = 4000
    MAX_CHAT_HISTORY: int = 10
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dropspot-ai-secret-key-2024")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

