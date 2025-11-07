from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Drop, Waitlist, Claim, DropStatus
from schemas import DropResponse, DropWithDistance, LocationQuery, MessageResponse
from utils.security import get_current_user, calculate_distance

router = APIRouter()


@router.get("/", response_model=List[DropResponse])
async def list_drops(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[DropStatus] = None,
    db: Session = Depends(get_db)
):
    """Tüm aktif drop'ları listele"""
    query = db.query(Drop).filter(Drop.is_active == True)
    
    if status_filter:
        query = query.filter(Drop.status == status_filter)
    
    drops = query.order_by(Drop.start_time.desc()).offset(skip).limit(limit).all()
    return drops


@router.get("/active", response_model=List[DropResponse])
async def list_active_drops(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Şu anda aktif olan drop'ları listele (başlamış ve bitmemiş)"""
    now = datetime.utcnow()
    
    drops = db.query(Drop).filter(
        and_(
            Drop.is_active == True,
            Drop.status == DropStatus.ACTIVE,
            Drop.start_time <= now,
            Drop.end_time >= now
        )
    ).order_by(Drop.start_time.desc()).offset(skip).limit(limit).all()
    
    return drops


@router.get("/upcoming", response_model=List[DropResponse])
async def list_upcoming_drops(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Yaklaşan drop'ları listele (henüz başlamamış)"""
    now = datetime.utcnow()
    
    drops = db.query(Drop).filter(
        and_(
            Drop.is_active == True,
            Drop.status == DropStatus.ACTIVE,
            Drop.start_time > now
        )
    ).order_by(Drop.start_time.asc()).offset(skip).limit(limit).all()
    
    return drops


@router.post("/nearby", response_model=List[DropWithDistance])
async def list_nearby_drops(
    location: LocationQuery,
    db: Session = Depends(get_db)
):
    """Kullanıcının konumuna yakın drop'ları listele"""
    now = datetime.utcnow()
    
    # Aktif drop'ları al
    drops = db.query(Drop).filter(
        and_(
            Drop.is_active == True,
            Drop.status == DropStatus.ACTIVE,
            Drop.start_time <= now,
            Drop.end_time >= now
        )
    ).all()
    
    # Her drop için mesafeyi hesapla
    drops_with_distance = []
    for drop in drops:
        distance = calculate_distance(
            location.latitude, location.longitude,
            drop.latitude, drop.longitude
        )
        
        # Radius içinde olanları filtrele
        if distance <= (location.radius_km * 1000):  # km'yi metreye çevir
            drop_dict = {
                **drop.__dict__,
                "distance_meters": round(distance, 2)
            }
            drops_with_distance.append(drop_dict)
    
    # Mesafeye göre sırala
    drops_with_distance.sort(key=lambda x: x["distance_meters"])
    
    return drops_with_distance


@router.get("/{drop_id}", response_model=DropResponse)
async def get_drop(
    drop_id: int,
    db: Session = Depends(get_db)
):
    """Belirli bir drop'un detaylarını getir"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    return drop


@router.get("/{drop_id}/my-status")
async def get_my_drop_status(
    drop_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının bu drop için durumunu kontrol et (waitlist'te mi, claim yapmış mı)"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    user_id = current_user["user_id"]
    
    # Waitlist kontrolü
    in_waitlist = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == user_id
        )
    ).first()
    
    # Claim kontrolü
    user_claim = db.query(Claim).filter(
        and_(
            Claim.drop_id == drop_id,
            Claim.user_id == user_id
        )
    ).first()
    
    return {
        "drop_id": drop_id,
        "in_waitlist": in_waitlist is not None,
        "has_claimed": user_claim is not None,
        "claim_status": user_claim.status if user_claim else None,
        "claim_verified": user_claim.is_verified if user_claim else False
    }

