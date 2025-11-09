"""
Google Gemini AI Service
"""
import google.generativeai as genai
from typing import List, Dict, Optional
from config import settings
import structlog

logger = structlog.get_logger()


class GeminiService:
    """Gemini AI API wrapper"""
    
    def __init__(self):
        """Gemini API'yi initialize et"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Model konfigürasyonu
        self.generation_config = {
            "temperature": settings.TEMPERATURE,
            "top_p": settings.TOP_P,
            "top_k": settings.TOP_K,
            "max_output_tokens": 2048,
        }
        
        # Güvenlik ayarları
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        logger.info("gemini_service_initialized", model=settings.GEMINI_MODEL)
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Gemini ile response oluştur
        
        Args:
            prompt: Kullanıcı sorusu
            context: RAG'den gelen context bilgisi
            chat_history: Önceki konuşma geçmişi
            
        Returns:
            AI'ın cevabı
        """
        try:
            # Tam prompt oluştur
            full_prompt = self._build_prompt(prompt, context, chat_history)
            
            logger.info("generating_response", prompt_length=len(full_prompt))
            
            # Gemini'den cevap al
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                logger.info("response_generated", response_length=len(response.text))
                return response.text
            else:
                logger.warning("empty_response_from_gemini")
                return "Üzgünüm, şu anda bir cevap oluşturamıyorum."
                
        except Exception as e:
            logger.error("gemini_generation_error", error=str(e))
            raise
    
    def _build_prompt(
        self,
        user_question: str,
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """RAG için prompt oluştur"""
        
        system_prompt = """Sen DropSpot platformunun AI asistanısın. 
DropSpot, kullanıcıların sınırlı sayıdaki ürünlere (drops) erişim için bekleme listesine katılmasını ve hak kazanmasını yöneten bir platformdur.

Görevin:
1. Kullanıcılara DropSpot platformu hakkında yardımcı olmak
2. Drop'lar, bekleme listeleri, claim süreçleri hakkında bilgi vermek
3. Kullanıcı ve admin işlemleri hakkında rehberlik etmek
4. Verilen context bilgilerine dayanarak doğru ve yararlı cevaplar vermek

Kurallar:
- Sadece verilen context bilgilerine dayanarak cevap ver
- Context'te bilgi yoksa bunu belirt ve genel bilgi ver
- Türkçe ve açık bir dil kullan
- Kısa ve öz cevaplar ver
"""
        
        # Prompt parçalarını birleştir
        prompt_parts = [system_prompt]
        
        # Context varsa ekle
        if context:
            prompt_parts.append(f"\n--- Platform Bilgileri ---\n{context}\n")
        
        # Chat history varsa ekle
        if chat_history:
            prompt_parts.append("\n--- Önceki Konuşma ---")
            for msg in chat_history[-settings.MAX_CHAT_HISTORY:]:
                role = "Kullanıcı" if msg["role"] == "user" else "Asistan"
                prompt_parts.append(f"{role}: {msg['content']}")
            prompt_parts.append("")
        
        # Kullanıcı sorusunu ekle
        prompt_parts.append(f"\nKullanıcı Sorusu: {user_question}\n")
        prompt_parts.append("Asistan:")
        
        return "\n".join(prompt_parts)
    
    async def check_health(self) -> bool:
        """Gemini API sağlık kontrolü"""
        try:
            response = self.model.generate_content("Test")
            return bool(response.text)
        except Exception as e:
            logger.error("gemini_health_check_failed", error=str(e))
            return False


# Global instance
gemini_service = GeminiService()

