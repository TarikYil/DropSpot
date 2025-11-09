#!/usr/bin/env python3
"""Varsayılan rolleri oluştur"""

from database import SessionLocal
from models import Role

def init_roles():
    """Varsayılan rolleri veritabanına ekle"""
    db = SessionLocal()
    
    try:
        # Mevcut roller
        existing_roles = {role.name for role in db.query(Role).all()}
        
        # Varsayılan roller
        default_roles = [
            {
                "name": "admin",
                "display_name": "Admin",
                "description": "Tam yetki - tüm işlemleri yapabilir",
                "can_create_drops": True,
                "can_edit_drops": True,
                "can_delete_drops": True,
                "can_approve_claims": True,
                "can_manage_users": True,
                "can_view_analytics": True
            },
            {
                "name": "moderator",
                "display_name": "Moderatör",
                "description": "Drop yönetimi ve claim onaylama yetkisi",
                "can_create_drops": True,
                "can_edit_drops": True,
                "can_delete_drops": False,
                "can_approve_claims": True,
                "can_manage_users": False,
                "can_view_analytics": True
            },
            {
                "name": "creator",
                "display_name": "İçerik Üreticisi",
                "description": "Sadece drop oluşturabilir",
                "can_create_drops": True,
                "can_edit_drops": True,
                "can_delete_drops": False,
                "can_approve_claims": False,
                "can_manage_users": False,
                "can_view_analytics": False
            },
            {
                "name": "user",
                "display_name": "Kullanıcı",
                "description": "Normal kullanıcı - drop'lara katılabilir",
                "can_create_drops": False,
                "can_edit_drops": False,
                "can_delete_drops": False,
                "can_approve_claims": False,
                "can_manage_users": False,
                "can_view_analytics": False
            }
        ]
        
        created_count = 0
        for role_data in default_roles:
            if role_data["name"] not in existing_roles:
                role = Role(**role_data)
                db.add(role)
                created_count += 1
                print(f"✅ Rol oluşturuldu: {role_data['display_name']}")
            else:
                print(f"⚠️  Rol zaten mevcut: {role_data['display_name']}")
        
        db.commit()
        print(f"\n🎉 {created_count} yeni rol oluşturuldu!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Varsayılan Rolleri Oluştur")
    print("=" * 60)
    init_roles()

