import hashlib
import os
from datetime import datetime
from typing import Optional


class SeedManager:
    """
    DropSpot projesine özgü benzersiz seed yöneticisi.
    
    Seed Hesaplama Formülü:
    -----------------------
    SEED = SHA256(GITHUB_URL + FIRST_COMMIT_EPOCH + PROJECT_START_TIME)[:12]
    
    Kullanım Alanları:
    - Claim code üretimi (her kullanıcı için benzersiz)
    - Priority score hesaplama (waitlist sıralaması)
    - Adil ve tekrarlanabilir rastgelelik
    """
    
    def __init__(self):
        # Proje bilgileri (environment'tan veya config'den)
        self.github_url = os.getenv("GITHUB_REPO_URL", "https://github.com/dropspot/platform")
        self.first_commit_epoch = os.getenv("FIRST_COMMIT_EPOCH", "1699000000")  # Örnek epoch
        self.project_start_time = os.getenv("PROJECT_START_TIME", "202411071200")  # YYYYMMDDHHmm
        
        # Seed'i hesapla
        self._seed = self._generate_seed()
    
    def _generate_seed(self) -> str:
        """Proje bilgilerinden benzersiz seed oluştur"""
        # Tüm bilgileri birleştir
        seed_input = f"{self.github_url}{self.first_commit_epoch}{self.project_start_time}"
        
        # SHA-256 hash
        hash_object = hashlib.sha256(seed_input.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # İlk 12 karakteri al
        seed = hash_hex[:12]
        
        return seed
    
    @property
    def seed(self) -> str:
        """Projenin benzersiz seed'ini döndür"""
        return self._seed
    
    def generate_claim_code(self, user_id: int, drop_id: int, timestamp: Optional[datetime] = None) -> str:
        """
        Kullanıcı için benzersiz claim code üret
        
        Args:
            user_id: Kullanıcı ID
            drop_id: Drop ID
            timestamp: Claim zamanı (opsiyonel, default: şimdi)
        
        Returns:
            str: Benzersiz claim code (örn: "DC-A3F5B7C2")
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Claim code input: seed + user_id + drop_id + timestamp
        claim_input = f"{self._seed}{user_id}{drop_id}{timestamp.isoformat()}"
        
        # Hash
        hash_object = hashlib.sha256(claim_input.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # İlk 8 karakteri al ve formatla
        code = hash_hex[:8].upper()
        claim_code = f"DC-{code[:4]}{code[4:]}"  # DC-XXXX-XXXX formatı
        
        return claim_code
    
    def calculate_priority_score(self, user_id: int, drop_id: int, waitlist_position: int) -> float:
        """
        Kullanıcının öncelik skorunu hesapla
        
        Bu skor, aynı drop için bekleme listesindeki kullanıcıların
        claim hakkı kazanma önceliğini belirler.
        
        Formula:
        --------
        score = hash(seed + user_id + drop_id) % 10000 + waitlist_position * 10
        
        - Hash: Rastgele ama tekrarlanabilir
        - Waitlist position: Erken katılanlar avantajlı
        
        Args:
            user_id: Kullanıcı ID
            drop_id: Drop ID
            waitlist_position: Bekleme listesindeki sıra (1'den başlar)
        
        Returns:
            float: Öncelik skoru (düşük = yüksek öncelik)
        """
        # Priority input: seed + user_id + drop_id
        priority_input = f"{self._seed}{user_id}{drop_id}"
        
        # Hash
        hash_object = hashlib.sha256(priority_input.encode('utf-8'))
        hash_int = int(hash_object.hexdigest()[:8], 16)  # İlk 8 hex char'ı integer'a çevir
        
        # Rastgele bileşen (0-9999)
        random_component = hash_int % 10000
        
        # Waitlist position bileşeni (erken katılanlar avantajlı)
        position_component = waitlist_position * 10
        
        # Final score
        priority_score = random_component + position_component
        
        return float(priority_score)
    
    def get_seed_info(self) -> dict:
        """Seed bilgilerini döndür (debug/info amaçlı)"""
        return {
            "seed": self._seed,
            "github_url": self.github_url,
            "first_commit_epoch": self.first_commit_epoch,
            "project_start_time": self.project_start_time,
            "seed_length": len(self._seed)
        }


# Global seed manager instance
seed_manager = SeedManager()

