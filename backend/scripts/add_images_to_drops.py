"""
Mevcut drop'lara görsel URL'leri ekle
Unsplash API veya placeholder servislerinden görseller kullanır
"""
import sys
import os
from pathlib import Path

# Backend dizinini path'e ekle
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Drop
import random

# Unsplash ve diğer placeholder servislerinden görsel URL'leri
IMAGE_URLS = [
    # Unsplash - Ürün fotoğrafları
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1607344645866-009c7d0a8d00?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1607345367223-5b0c3c3c3c3c?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1607345367223-5b0c3c3c3c3c?w=800&h=600&fit=crop",
    # Picsum Photos - Rastgele görseller
    "https://picsum.photos/800/600?random=1",
    "https://picsum.photos/800/600?random=2",
    "https://picsum.photos/800/600?random=3",
    "https://picsum.photos/800/600?random=4",
    "https://picsum.photos/800/600?random=5",
    "https://picsum.photos/800/600?random=6",
    "https://picsum.photos/800/600?random=7",
    "https://picsum.photos/800/600?random=8",
    "https://picsum.photos/800/600?random=9",
    "https://picsum.photos/800/600?random=10",
    # Placeholder servisleri
    "https://via.placeholder.com/800x600/6366f1/ffffff?text=Drop+Product",
    "https://via.placeholder.com/800x600/8b5cf6/ffffff?text=Exclusive+Drop",
    "https://via.placeholder.com/800x600/ec4899/ffffff?text=Limited+Edition",
    "https://via.placeholder.com/800x600/f59e0b/ffffff?text=Premium+Product",
    "https://via.placeholder.com/800x600/10b981/ffffff?text=Special+Drop",
]


def add_images_to_drops():
    """Mevcut drop'lara rastgele görsel URL'leri ekle"""
    db = SessionLocal()
    
    try:
        # Tüm drop'ları al
        drops = db.query(Drop).all()
        
        if not drops:
            print("Drop bulunamadı. Önce drop oluşturun.")
            return
        
        updated_count = 0
        for drop in drops:
            # Eğer zaten görsel varsa atla (isteğe bağlı - yorum satırını kaldırabilirsiniz)
            # if drop.image_url:
            #     continue
            
            # Rastgele bir görsel seç
            image_url = random.choice(IMAGE_URLS)
            drop.image_url = image_url
            updated_count += 1
        
        db.commit()
        
        print(f"✅ {updated_count} adet drop'a görsel eklendi!")
        print("\nGörseller şu kaynaklardan alındı:")
        print("- Unsplash (ücretsiz, yüksek kaliteli)")
        print("- Picsum Photos (rastgele görseller)")
        print("- Placeholder (test görselleri)")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_images_to_drops()

