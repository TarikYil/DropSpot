"""
Kullanıcı şifresini sıfırlama scripti
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

def reset_password(username_or_email: str, new_password: str):
    """Kullanıcı şifresini sıfırla"""
    db = SessionLocal()
    
    try:
        # Kullanıcıyı bul
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"❌ Kullanıcı bulunamadı: {username_or_email}")
            return False
        
        # Şifreyi hash'le ve güncelle
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        print(f"✅ Şifre başarıyla sıfırlandı!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Yeni şifre: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python reset_password.py <username_or_email> <yeni_sifre>")
        print("Örnek: python reset_password.py tarik YeniSifre123")
        print("Örnek: python reset_password.py admin@test.com YeniSifre123")
        sys.exit(1)
    
    username_or_email = sys.argv[1]
    new_password = sys.argv[2]
    reset_password(username_or_email, new_password)

