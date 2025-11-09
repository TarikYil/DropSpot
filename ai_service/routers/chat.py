"""
Chat Router - AI Chatbot endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
import structlog

from schemas import ChatRequest, ChatResponse
from services.gemini_service import gemini_service
from services.rag_service import rag_service
from utils.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    chat_request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    AI'ya soru sor
    
    - Token opsiyonel: Token varsa kullanıcıya özel bilgiler de verilebilir
    - Token yoksa genel bilgiler verilir
    """
    try:
        user_info = ""
        if current_user:
            user_info = f" (User: {current_user['username']})"
        
        logger.info(
            "chat_request_received",
            message=chat_request.message[:50],
            has_user=bool(current_user),
            history_length=len(chat_request.chat_history)
        )
        
        # Context oluştur (RAG)
        context = None
        context_used = False
        
        if chat_request.include_context:
            try:
                # Backend'den ilgili bilgileri çek
                user_token = current_user["token"] if current_user else None
                context = await rag_service.get_context_for_question(
                    chat_request.message,
                    user_token
                )
                context_used = bool(context)
                logger.info("rag_context_retrieved", context_length=len(context) if context else 0)
            except Exception as e:
                logger.warning("rag_context_retrieval_failed", error=str(e))
                context = None
        
        # Chat history'yi dict listesine çevir
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.chat_history
        ]
        
        # Gemini'den cevap al
        response_text = await gemini_service.generate_response(
            prompt=chat_request.message,
            context=context,
            chat_history=history
        )
        
        logger.info(
            "chat_response_generated",
            response_length=len(response_text),
            context_used=context_used
        )
        
        return ChatResponse(
            response=response_text,
            context_used=context_used,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("chat_request_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat işlemi başarısız: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Chat servisi sağlık kontrolü"""
    try:
        gemini_healthy = await gemini_service.check_health()
        
        return {
            "status": "healthy" if gemini_healthy else "degraded",
            "gemini_api": "connected" if gemini_healthy else "disconnected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error("chat_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

