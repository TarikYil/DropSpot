"""
Pydantic Schemas for AI Service
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat mesajı"""
    role: str = Field(..., description="user veya assistant")
    content: str = Field(..., description="Mesaj içeriği")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request şeması"""
    message: str = Field(..., min_length=1, max_length=1000, description="Kullanıcı mesajı")
    chat_history: Optional[List[ChatMessage]] = Field(default=[], description="Önceki konuşma geçmişi")
    include_context: bool = Field(default=True, description="Backend'den context çekilsin mi?")


class ChatResponse(BaseModel):
    """Chat response şeması"""
    response: str = Field(..., description="AI'ın cevabı")
    context_used: bool = Field(..., description="Context kullanıldı mı?")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    gemini_status: str
    backend_status: str

