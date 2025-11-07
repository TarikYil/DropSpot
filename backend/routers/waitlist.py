from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from database import get_db
from models import Drop, Waitlist, DropStatus
from schemas import WaitlistCreate, WaitlistResponse, MessageResponse
from utils.security import get_current_user

router = APIRouter()


@router.post("/join", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def join_waitlist(
    waitlist_data: WaitlistCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bir drop için bekleme listesine katıl
    
    İdempotent: Aynı kullanıcı aynı drop'a birden fazla kez katılamaz
    """
    drop_id = waitlist_data.drop_id
    user_id = current_user["user_id"]
    
    # Drop kontrolü
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    # Drop aktif mi kontrol et
    if not drop.is_active or drop.status != DropStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu drop aktif değil"
        )
    
    # Drop henüz başlamadı mı kontrol et
    now = datetime.utcnow()
    if now > drop.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu drop'un süresi dolmuş"
        )
    
    # Kullanıcı zaten waitlist'te mi kontrol et (İdempotent)
    existing_entry = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == user_id
        )
    ).first()
    
    if existing_entry:
        # Zaten waitlist'te - mevcut kaydı döndür (idempotent)
        return existing_entry
    
    # Yeni waitlist kaydı oluştur
    new_entry = Waitlist(
        drop_id=drop_id,
        user_id=user_id
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    return new_entry


@router.delete("/leave/{drop_id}", response_model=MessageResponse)
async def leave_waitlist(
    drop_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bir drop'un bekleme listesinden ayrıl"""
    user_id = current_user["user_id"]
    
    # Drop kontrolü
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    # Waitlist kaydını bul
    waitlist_entry = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == user_id
        )
    ).first()
    
    if not waitlist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bekleme listesinde kayıt bulunamadı"
        )
    
    # Kaydı sil
    db.delete(waitlist_entry)
    db.commit()
    
    return MessageResponse(
        message="Bekleme listesinden başarıyla ayrıldınız",
        detail=f"Drop ID: {drop_id}"
    )


@router.get("/my-waitlist", response_model=list[WaitlistResponse])
async def get_my_waitlist(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının katıldığı tüm bekleme listelerini getir"""
    user_id = current_user["user_id"]
    
    waitlist_entries = db.query(Waitlist).filter(
        Waitlist.user_id == user_id
    ).order_by(Waitlist.created_at.desc()).all()
    
    return waitlist_entries


@router.get("/{drop_id}/waitlist-count")
async def get_waitlist_count(
    drop_id: int,
    db: Session = Depends(get_db)
):
    """Bir drop'un bekleme listesindeki kişi sayısını döndür"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    count = db.query(Waitlist).filter(Waitlist.drop_id == drop_id).count()
    
    return {
        "drop_id": drop_id,
        "waitlist_count": count
    }


@router.get("/{drop_id}/my-position")
async def get_my_waitlist_position(
    drop_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının bekleme listesindeki sırasını döndür"""
    user_id = current_user["user_id"]
    
    # Kullanıcının kaydı var mı
    user_entry = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == user_id
        )
    ).first()
    
    if not user_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bekleme listesinde kayıt bulunamadı"
        )
    
    # Kullanıcıdan önce kaydolan kaç kişi var
    position = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.created_at < user_entry.created_at
        )
    ).count() + 1  # +1 çünkü sıra 1'den başlıyor
    
    total = db.query(Waitlist).filter(Waitlist.drop_id == drop_id).count()
    
    return {
        "drop_id": drop_id,
        "position": position,
        "total": total
    }

