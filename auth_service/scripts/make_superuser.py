"""
Kullanıcıyı superuser yapmak için script
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

def make_superuser(username_or_email: str):
    """Kullanıcıyı superuser yap"""
    db = SessionLocal()
    
    try:
        # Kullanıcıyı bul
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"❌ Kullanıcı bulunamadı: {username_or_email}")
            return False
        
        # Superuser yap
        user.is_superuser = True
        db.commit()
        
        print(f"✅ Kullanıcı superuser yapıldı!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   is_superuser: {user.is_superuser}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python make_superuser.py <username_or_email>")
        print("Örnek: python make_superuser.py admin")
        print("Örnek: python make_superuser.py admin@example.com")
        sys.exit(1)
    
    username_or_email = sys.argv[1]
    make_superuser(username_or_email)

