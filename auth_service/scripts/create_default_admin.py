"""
Default süper admin kullanıcısı oluşturma scripti
"""
import sys
import os
from pathlib import Path

# Auth service dizinini path'e ekle
auth_service_path = Path(__file__).parent.parent
sys.path.insert(0, str(auth_service_path))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from utils.auth_utils import get_password_hash


def create_default_admin(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123",
    full_name: str = "Default Admin"
):
    """
    Default süper admin kullanıcısı oluştur
    
    Args:
        username: Kullanıcı adı (default: admin)
        email: Email adresi (default: admin@example.com)
        password: Şifre (default: admin123)
        full_name: Tam ad (default: Default Admin)
    
    Returns:
        bool: Başarılı ise True, aksi halde False
    """
    db = SessionLocal()
    
    try:
        # Kullanıcı zaten var mı kontrol et
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            # Kullanıcı varsa, superuser yap ve bilgileri güncelle
            print(f"⚠️  Kullanıcı zaten mevcut: {existing_user.username}")
            print(f"   Mevcut kullanıcıyı süper admin yapılıyor...")
            
            existing_user.is_superuser = True
            existing_user.is_active = True
            existing_user.is_verified = True
            existing_user.hashed_password = get_password_hash(password)
            
            if existing_user.full_name != full_name:
                existing_user.full_name = full_name
            
            db.commit()
            
            print(f"✅ Mevcut kullanıcı süper admin yapıldı!")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            print(f"   ID: {existing_user.id}")
            print(f"   is_superuser: {existing_user.is_superuser}")
            print(f"   Şifre güncellendi: {password}")
            
            return True
        
        # Yeni kullanıcı oluştur
        hashed_password = get_password_hash(password)
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Default süper admin kullanıcısı oluşturuldu!")
        print(f"   Username: {new_user.username}")
        print(f"   Email: {new_user.email}")
        print(f"   Password: {password}")
        print(f"   Full Name: {new_user.full_name}")
        print(f"   ID: {new_user.id}")
        print(f"   is_superuser: {new_user.is_superuser}")
        print(f"   is_active: {new_user.is_active}")
        print(f"   is_verified: {new_user.is_verified}")
        print()
        print("⚠️  GÜVENLİK UYARISI:")
        print("   Production ortamında şifreyi mutlaka değiştirin!")
        print("   Bu varsayılan şifre sadece development/test için kullanılmalıdır.")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Komut satırı argümanları ile özelleştirilebilir
    username = os.getenv("ADMIN_USERNAME", "admin")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    full_name = os.getenv("ADMIN_FULL_NAME", "Default Admin")
    
    # Komut satırı argümanları varsa kullan
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        email = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
    if len(sys.argv) > 4:
        full_name = sys.argv[4]
    
    print("=" * 60)
    print("Default Süper Admin Kullanıcısı Oluşturma")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Full Name: {full_name}")
    print("=" * 60)
    print()
    
    success = create_default_admin(
        username=username,
        email=email,
        password=password,
        full_name=full_name
    )
    
    if success:
        print()
        print("=" * 60)
        print("✅ İşlem başarıyla tamamlandı!")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ İşlem başarısız oldu!")
        print("=" * 60)
        sys.exit(1)

