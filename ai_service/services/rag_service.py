"""
RAG (Retrieval Augmented Generation) Service
Backend'den veri çekerek context oluşturur
"""
from typing import Dict, List, Optional
import httpx
from config import settings
import structlog

logger = structlog.get_logger()


class RAGService:
    """Backend'den veri çekip context oluşturan servis"""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_SERVICE_URL
        self.auth_url = settings.AUTH_SERVICE_URL
    
    async def get_context_for_question(
        self,
        question: str,
        user_token: Optional[str] = None
    ) -> str:
        """
        Soruya göre backend'den ilgili bilgileri çekip context oluştur
        
        Args:
            question: Kullanıcının sorusu
            user_token: Kullanıcının auth token'ı (opsiyonel)
            
        Returns:
            Context string
        """
        question_lower = question.lower()
        context_parts = []
        
        try:
            # Drop'larla ilgili soru - VERİTABANINDAN GERÇEK VERİLER
            if any(keyword in question_lower for keyword in ["drop", "ürün", "yayın", "ne var", "aktif", "liste", "tüm"]):
                drops_info = await self._get_all_drops_detailed()
                if drops_info:
                    context_parts.append(f"VERİTABANINDAN ÇEKİLEN DROP VERİLERİ:\n{drops_info}")
            
            # Bekleme listesi ile ilgili - VERİTABANINDAN GERÇEK VERİLER
            if any(keyword in question_lower for keyword in ["waitlist", "bekleme", "sıra", "katıl", "bekleyen"]):
                waitlist_info = await self._get_waitlist_data_detailed(user_token)
                if waitlist_info:
                    context_parts.append(f"VERİTABANINDAN ÇEKİLEN WAITLIST VERİLERİ:\n{waitlist_info}")
            
            # Claim ile ilgili - VERİTABANINDAN GERÇEK VERİLER
            if any(keyword in question_lower for keyword in ["claim", "hak", "kazanma", "alma", "talepler"]):
                claim_info = await self._get_claim_data_detailed(user_token)
                if claim_info:
                    context_parts.append(f"VERİTABANINDAN ÇEKİLEN CLAIM VERİLERİ:\n{claim_info}")
            
            # İstatistikler ile ilgili
            if any(keyword in question_lower for keyword in ["istatistik", "stat", "sayı", "kaç", "toplam", "adet"]):
                stats_info = await self._get_platform_stats(user_token)
                if stats_info:
                    context_parts.append(f"VERİTABANINDAN ÇEKİLEN İSTATİSTİKLER:\n{stats_info}")
            
            # Kullanıcıya özel bilgiler (token varsa)
            if user_token and any(keyword in question_lower for keyword in ["benim", "bana", "kendi", "sizin"]):
                user_info = await self._get_user_specific_data(user_token)
                if user_info:
                    context_parts.append(f"KULLANICI ÖZEL VERİLER:\n{user_info}")
            
            # Admin/Yönetim ile ilgili
            if any(keyword in question_lower for keyword in ["admin", "yönetici", "panel", "yönetim"]):
                admin_info = self._get_admin_info()
                context_parts.append(f"Admin İşlemleri:\n{admin_info}")
            
            # Genel platform bilgisi
            if not context_parts or any(keyword in question_lower for keyword in ["nedir", "nasıl", "ne", "platform"]):
                platform_info = self._get_platform_info()
                context_parts.append(f"Platform Bilgisi:\n{platform_info}")
            
            # Context'leri birleştir
            if context_parts:
                return "\n\n".join(context_parts)
            
            return "Platform hakkında genel bilgi verebilirim."
            
        except Exception as e:
            logger.error("rag_context_building_error", error=str(e))
            return "Platform verilerine şu anda erişilemiyor."
    
    async def _get_all_drops_detailed(self) -> Optional[str]:
        """Backend'den TÜM drop'ları detaylı çek (VERİTABANINDAN)"""
        try:
            async with httpx.AsyncClient() as client:
                # Tüm aktif drop'ları çek
                response = await client.get(
                    f"{self.backend_url}/api/drops/?limit=20",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    drops = response.json()
                    if drops:
                        drop_details = []
                        for drop in drops:
                            # Her drop için waitlist sayısını da çek
                            waitlist_count = await self._get_waitlist_count_for_drop(drop.get('id'))
                            
                            detail = (
                                f"DROP #{drop.get('id')}: {drop.get('title')}\n"
                                f"  Açıklama: {drop.get('description', 'Açıklama yok')}\n"
                                f"  Durum: {drop.get('status')}\n"
                                f"  Stok: {drop.get('remaining_quantity')}/{drop.get('total_quantity')} (Kalan/Toplam)\n"
                                f"  Bekleme Listesinde: {waitlist_count} kişi\n"
                                f"  Başlangıç: {drop.get('start_time')}\n"
                                f"  Bitiş: {drop.get('end_time')}\n"
                                f"  Konum: {drop.get('address', 'Belirtilmemiş')}\n"
                            )
                            drop_details.append(detail)
                        
                        return f"TOPLAM {len(drops)} DROP BULUNDU:\n\n" + "\n".join(drop_details)
                return None
        except Exception as e:
            logger.warning("failed_to_fetch_drops_detailed", error=str(e))
            return None
    
    async def _get_waitlist_count_for_drop(self, drop_id: int) -> int:
        """Bir drop'un waitlist sayısını çek"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/waitlist/{drop_id}/waitlist-count",
                    timeout=3.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('waitlist_count', 0)
        except Exception:
            pass
        return 0
    
    async def _get_waitlist_data_detailed(self, user_token: Optional[str] = None) -> Optional[str]:
        """VERİTABANINDAN bekleme listesi verilerini çek"""
        try:
            info_parts = []
            
            # Tüm drop'lar için waitlist sayılarını çek
            async with httpx.AsyncClient() as client:
                # Aktif drop'ları al
                drops_response = await client.get(
                    f"{self.backend_url}/api/drops/active?limit=10",
                    timeout=5.0
                )
                
                if drops_response.status_code == 200:
                    drops = drops_response.json()
                    if drops:
                        waitlist_summary = []
                        for drop in drops:
                            count = await self._get_waitlist_count_for_drop(drop.get('id'))
                            waitlist_summary.append(
                                f"  - Drop #{drop.get('id')} ({drop.get('title')}): {count} kişi bekliyor"
                            )
                        
                        if waitlist_summary:
                            info_parts.append("WAITLIST İSTATİSTİKLERİ (VERİTABANINDAN):")
                            info_parts.extend(waitlist_summary)
            
            # Kullanıcı token'ı varsa, kullanıcının waitlist'ini de çek
            if user_token:
                user_waitlist = await self._get_user_waitlist(user_token)
                if user_waitlist:
                    info_parts.append(f"\nKULLANICININ WAITLIST'İ:\n{user_waitlist}")
            
            if info_parts:
                return "\n".join(info_parts)
            
            return "Bekleme listesi, drop'lara katılmak isteyen kullanıcıların sırada beklediği sistemdir."
        except Exception as e:
            logger.warning("failed_to_fetch_waitlist_detailed", error=str(e))
            return None
    
    async def _get_user_waitlist(self, token: str) -> Optional[str]:
        """Kullanıcının waitlist'ini çek"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.backend_url}/api/waitlist/my-waitlist",
                    headers=headers,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    waitlist = response.json()
                    if waitlist:
                        entries = []
                        for entry in waitlist:
                            entries.append(
                                f"  - Drop #{entry.get('drop_id')}: Sıra #{entry.get('position', '?')}, "
                                f"Katılım: {entry.get('created_at')}"
                            )
                        return "\n".join(entries)
        except Exception:
            pass
        return None
    
    async def _get_claim_data_detailed(self, user_token: Optional[str] = None) -> Optional[str]:
        """VERİTABANINDAN claim verilerini çek"""
        try:
            info_parts = []
            
            # Kullanıcı token'ı varsa, kullanıcının claim'lerini çek
            if user_token:
                user_claims = await self._get_user_claims(user_token)
                if user_claims:
                    info_parts.append(f"KULLANICININ CLAIM'LERİ (VERİTABANINDAN):\n{user_claims}")
            
            # Genel claim bilgisi
            info_parts.append("""
CLAIM SÜRECİ:
1. Drop zamanı geldiğinde bekleme listesindeki kullanıcılar sırayla hak kazanır
2. Her kullanıcıya benzersiz bir claim_code verilir
3. Claim yapabilmek için belirli bir süre içinde işlem yapılmalıdır
4. Stok biterse claim yapılamaz (403 Forbidden)
5. Aynı kullanıcı bir drop için sadece bir kez claim yapabilir
            """.strip())
            
            return "\n\n".join(info_parts)
        except Exception as e:
            logger.warning("failed_to_fetch_claim_detailed", error=str(e))
            return None
    
    async def _get_user_claims(self, token: str) -> Optional[str]:
        """Kullanıcının claim'lerini çek"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.backend_url}/api/claims/my-claims",
                    headers=headers,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    claims = response.json()
                    if claims:
                        claim_details = []
                        for claim in claims:
                            claim_details.append(
                                f"  - Drop #{claim.get('drop_id')}: "
                                f"Durum: {claim.get('status')}, "
                                f"Kod: {claim.get('claim_code', 'Yok')}, "
                                f"Tarih: {claim.get('created_at')}"
                            )
                        return "\n".join(claim_details)
        except Exception:
            pass
        return None
    
    def _get_admin_info(self) -> str:
        """Admin işlemleri bilgisi"""
        return """Admin yetkisi ile yapılabilecekler:
- Yeni drop oluşturma (POST /api/admin/drops)
- Mevcut drop'ları düzenleme (PUT /api/admin/drops/{id})
- Drop'ları silme (DELETE /api/admin/drops/{id})
- Sistem istatistiklerini görüntüleme
- Kullanıcı rollerini yönetme (Super Admin)"""
    
    def _get_platform_info(self) -> str:
        """Genel platform bilgisi"""
        return """DropSpot Platformu Hakkında:

DropSpot, sınırlı sayıdaki ürünlere (drops) adil erişim sağlayan bir platformdur.

Ana Özellikler:
1. DROP YÖNETİMİ: Markalar sınırlı sayıda ürün yayınlayabilir
2. BEKLEMELİ LİSTESİ: Kullanıcılar drop'lara katılıp sırada bekleyebilir
3. CLAIM SÜRECİ: Drop zamanı geldiğinde sırayla hak kazanma
4. ADİL DAĞITIM: Konum bazlı ve benzersiz seed sistemi ile adil sıralama

Servisler:
- Auth Service (Port 8000): Kullanıcı kimlik doğrulama
- Backend Service (Port 8002): Drop ve claim işlemleri
- AI Service (Port 8004): Chatbot desteği

Kullanıcı Rolleri:
- User: Temel kullanıcı (drop'lara katılabilir)
- Creator: İçerik oluşturucu (drop oluşturabilir)
- Moderator: Moderatör (içerikleri yönetir)
- Admin: Yönetici (tüm yetkilere sahip)"""
    
    async def _get_platform_stats(self, user_token: Optional[str] = None) -> Optional[str]:
        """VERİTABANINDAN platform istatistiklerini çek"""
        try:
            # Admin token'ı varsa detaylı stats çek
            if user_token:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {user_token}"}
                    response = await client.get(
                        f"{self.backend_url}/api/admin/stats",
                        headers=headers,
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        stats = response.json()
                        return f"""
PLATFORM İSTATİSTİKLERİ (VERİTABANINDAN):
- Toplam Drop: {stats.get('total_drops', 0)}
- Aktif Drop: {stats.get('active_drops', 0)}
- Toplam Claim: {stats.get('total_claims', 0)}
- Bekleyen Claim: {stats.get('pending_claims', 0)}
- Onaylanan Claim: {stats.get('approved_claims', 0)}
- Waitlist'teki Toplam Kullanıcı: {stats.get('total_users_on_waitlist', 0)}
                        """.strip()
        except Exception:
            pass
        
        # Admin değilse genel bilgi
        return "İstatistikler için admin yetkisi gereklidir."
    
    async def _get_user_specific_data(self, token: str) -> Optional[str]:
        """Kullanıcıya özel tüm verileri çek"""
        try:
            user_data = []
            
            # Waitlist
            waitlist = await self._get_user_waitlist(token)
            if waitlist:
                user_data.append(f"WAITLIST:\n{waitlist}")
            
            # Claims
            claims = await self._get_user_claims(token)
            if claims:
                user_data.append(f"CLAIM'LER:\n{claims}")
            
            if user_data:
                return "\n\n".join(user_data)
        except Exception as e:
            logger.warning("failed_to_fetch_user_specific_data", error=str(e))
        
        return None
    
    async def get_user_specific_context(
        self,
        user_id: int,
        token: str
    ) -> str:
        """Kullanıcıya özel bilgiler çek (deprecated - _get_user_specific_data kullan)"""
        return await self._get_user_specific_data(token) or "Kullanıcı bilgileri yüklenemedi."


# Global instance
rag_service = RAGService()

