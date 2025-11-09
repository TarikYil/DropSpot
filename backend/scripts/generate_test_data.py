"""
Sentetik test verileri oluşturma scripti
Backend veritabanına test drop'ları, waitlist ve claim'ler ekler
"""
import sys
import os
from pathlib import Path

# Backend dizinini path'e ekle
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Drop, Waitlist, Claim, DropStatus, ClaimStatus
from datetime import datetime, timedelta
import random

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)


def create_test_drops(db: Session, admin_user_id: int = 1, count: int = 5):
    """Sentetik drop'lar oluştur"""
    drops = []
    
    # İstanbul koordinatları
    istanbul_locations = [
        (41.0082, 28.9784, "Taksim, İstanbul"),
        (41.0369, 28.9850, "Kadıköy, İstanbul"),
        (41.0128, 28.9744, "Beşiktaş, İstanbul"),
        (41.0255, 28.9744, "Şişli, İstanbul"),
        (41.0082, 28.9784, "Beyoğlu, İstanbul"),
    ]
    
    drop_titles = [
        "Premium Tişört Koleksiyonu",
        "Sınırlı Sayıda Sneaker",
        "Exclusive Hoodie Drop",
        "Özel Tasarım Çanta",
        "Limited Edition Aksesuar Seti",
        "VIP Koleksiyon Ürünü",
        "Özel Baskılı Poster",
        "Sınırlı Stoklu Ürün",
    ]
    
    descriptions = [
        "Yüksek kaliteli malzemelerden üretilmiş özel tasarım ürün.",
        "Sınırlı sayıda üretilen koleksiyon parçası.",
        "Sadece bu drop'ta bulabileceğiniz özel ürün.",
        "Premium kalite ve özel ambalaj ile.",
        "Koleksiyonerler için özel tasarım.",
    ]
    
    now = datetime.utcnow()
    
    for i in range(count):
        lat, lon, address = random.choice(istanbul_locations)
        
        # Rastgele tarih aralığı (bazıları geçmişte, bazıları gelecekte)
        if i < 2:
            # Aktif drop'lar (şu anda devam eden)
            start_time = now - timedelta(hours=random.randint(1, 24))
            end_time = now + timedelta(hours=random.randint(24, 72))
        elif i < 4:
            # Gelecekteki drop'lar
            start_time = now + timedelta(hours=random.randint(24, 168))
            end_time = start_time + timedelta(hours=random.randint(24, 72))
        else:
            # Geçmiş drop'lar
            start_time = now - timedelta(days=random.randint(7, 30))
            end_time = start_time + timedelta(hours=random.randint(24, 72))
        
        total_quantity = random.randint(50, 200)
        claimed_quantity = random.randint(0, total_quantity // 2)
        remaining_quantity = total_quantity - claimed_quantity
        
        # Görsel URL'leri - Unsplash ve Picsum Photos
        image_urls = [
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
            f"https://picsum.photos/800/600?random={i+1}",
            f"https://picsum.photos/800/600?random={i+10}",
            f"https://picsum.photos/800/600?random={i+20}",
        ]
        
        drop = Drop(
            title=f"{random.choice(drop_titles)} #{i+1}",
            description=random.choice(descriptions),
            image_url=random.choice(image_urls),
            total_quantity=total_quantity,
            claimed_quantity=claimed_quantity,
            remaining_quantity=remaining_quantity,
            latitude=lat + random.uniform(-0.01, 0.01),  # Biraz varyasyon
            longitude=lon + random.uniform(-0.01, 0.01),
            address=address,
            radius_meters=random.randint(500, 5000),
            start_time=start_time,
            end_time=end_time,
            status=DropStatus.ACTIVE if now < end_time else DropStatus.COMPLETED,
            is_active=True if now < end_time else False,
            created_by=admin_user_id
        )
        
        db.add(drop)
        db.flush()  # ID'yi almak için
        drops.append(drop)
    
    db.commit()
    print(f"✓ {len(drops)} adet drop oluşturuldu")
    return drops


def create_test_waitlist(db: Session, drops: list, user_ids: list, count_per_drop: int = 10):
    """Sentetik waitlist kayıtları oluştur"""
    waitlist_entries = []
    
    for drop in drops:
        # Her drop için rastgele kullanıcılar ekle
        selected_users = random.sample(user_ids, min(count_per_drop, len(user_ids)))
        
        for user_id in selected_users:
            # Zaten waitlist'te mi kontrol et
            existing = db.query(Waitlist).filter(
                Waitlist.drop_id == drop.id,
                Waitlist.user_id == user_id
            ).first()
            
            if not existing:
                waitlist = Waitlist(
                    drop_id=drop.id,
                    user_id=user_id,
                    is_notified=random.choice([True, False]),
                    notified_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None
                )
                db.add(waitlist)
                waitlist_entries.append(waitlist)
    
    db.commit()
    print(f"✓ {len(waitlist_entries)} adet waitlist kaydı oluşturuldu")
    return waitlist_entries


def create_test_claims(db: Session, drops: list, user_ids: list, count_per_drop: int = 5):
    """Sentetik claim'ler oluştur"""
    claims = []
    
    for drop in drops:
        if drop.remaining_quantity <= 0:
            continue
        
        # Her drop için rastgele kullanıcılar claim yapsın
        selected_users = random.sample(user_ids, min(count_per_drop, len(user_ids), drop.remaining_quantity))
        
        for user_id in selected_users:
            # Zaten claim var mı kontrol et
            existing = db.query(Claim).filter(
                Claim.drop_id == drop.id,
                Claim.user_id == user_id
            ).first()
            
            if not existing:
                # Drop'un konumuna yakın bir konum
                claim_lat = drop.latitude + random.uniform(-0.005, 0.005)
                claim_lon = drop.longitude + random.uniform(-0.005, 0.005)
                
                # Mesafe hesapla (basit)
                distance = ((claim_lat - drop.latitude) ** 2 + (claim_lon - drop.longitude) ** 2) ** 0.5 * 111000  # Yaklaşık metre
                
                claim = Claim(
                    drop_id=drop.id,
                    user_id=user_id,
                    status=random.choice([ClaimStatus.PENDING, ClaimStatus.APPROVED, ClaimStatus.REJECTED]),
                    quantity=1,
                    claim_latitude=claim_lat,
                    claim_longitude=claim_lon,
                    distance_from_drop=distance,
                    verification_code=f"CODE-{drop.id}-{user_id}-{random.randint(1000, 9999)}",
                    is_verified=random.choice([True, False]),
                    verified_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)) if random.choice([True, False]) else None
                )
                db.add(claim)
                claims.append(claim)
    
    db.commit()
    print(f"✓ {len(claims)} adet claim oluşturuldu")
    return claims


def main():
    """Ana fonksiyon"""
    print("=" * 50)
    print("SENTETIK TEST VERİLERİ OLUŞTURULUYOR")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Admin user ID (auth servisinden 1 numaralı kullanıcıyı varsayıyoruz)
        admin_user_id = 1
        
        # Test kullanıcı ID'leri (auth servisinden olması gereken)
        # Gerçek kullanıcılar yoksa, sadece ID'leri kullanacağız
        test_user_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        print(f"\n1. Drop'lar oluşturuluyor...")
        drops = create_test_drops(db, admin_user_id=admin_user_id, count=8)
        
        print(f"\n2. Waitlist kayıtları oluşturuluyor...")
        waitlist_entries = create_test_waitlist(db, drops, test_user_ids, count_per_drop=8)
        
        print(f"\n3. Claim'ler oluşturuluyor...")
        claims = create_test_claims(db, drops, test_user_ids, count_per_drop=3)
        
        print("\n" + "=" * 50)
        print("ÖZET:")
        print(f"  - Drop'lar: {len(drops)}")
        print(f"  - Waitlist kayıtları: {len(waitlist_entries)}")
        print(f"  - Claim'ler: {len(claims)}")
        print("=" * 50)
        print("\n✓ Test verileri başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"\n✗ Hata: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

