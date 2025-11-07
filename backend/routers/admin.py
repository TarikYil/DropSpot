from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from database import get_db
from models import Drop, Claim, Waitlist, DropStatus, ClaimStatus
from schemas import (
    DropCreate, DropUpdate, DropResponse, ClaimResponse, 
    MessageResponse, StatsResponse
)
from utils.security import require_admin

router = APIRouter()


@router.post("/drops", response_model=DropResponse, status_code=status.HTTP_201_CREATED)
async def create_drop(
    drop_data: DropCreate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Yeni drop oluştur (Sadece Admin)"""
    
    # Zaman kontrolü
    if drop_data.end_time <= drop_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır"
        )
    
    # Yeni drop oluştur
    new_drop = Drop(
        title=drop_data.title,
        description=drop_data.description,
        image_url=drop_data.image_url,
        total_quantity=drop_data.total_quantity,
        remaining_quantity=drop_data.total_quantity,
        claimed_quantity=0,
        latitude=drop_data.latitude,
        longitude=drop_data.longitude,
        address=drop_data.address,
        radius_meters=drop_data.radius_meters,
        start_time=drop_data.start_time,
        end_time=drop_data.end_time,
        status=DropStatus.ACTIVE,
        is_active=True,
        created_by=current_user["user_id"]
    )
    
    db.add(new_drop)
    db.commit()
    db.refresh(new_drop)
    
    return new_drop


@router.put("/drops/{drop_id}", response_model=DropResponse)
async def update_drop(
    drop_id: int,
    drop_data: DropUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Drop'u güncelle (Sadece Admin)"""
    
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    # Güncelle
    if drop_data.title is not None:
        drop.title = drop_data.title
    if drop_data.description is not None:
        drop.description = drop_data.description
    if drop_data.image_url is not None:
        drop.image_url = drop_data.image_url
    if drop_data.total_quantity is not None:
        # Stok artırılırsa remaining_quantity'yi de güncelle
        difference = drop_data.total_quantity - drop.total_quantity
        drop.total_quantity = drop_data.total_quantity
        drop.remaining_quantity += difference
    if drop_data.status is not None:
        drop.status = drop_data.status
    if drop_data.is_active is not None:
        drop.is_active = drop_data.is_active
    
    drop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(drop)
    
    return drop


@router.delete("/drops/{drop_id}", response_model=MessageResponse)
async def delete_drop(
    drop_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Drop'u sil (Soft delete - is_active = False) (Sadece Admin)"""
    
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    # Soft delete
    drop.is_active = False
    drop.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(
        message="Drop başarıyla silindi",
        detail=f"Drop ID: {drop_id}"
    )


@router.get("/claims", response_model=List[ClaimResponse])
async def list_all_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: ClaimStatus = None,
    drop_id: int = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tüm claim'leri listele (Sadece Admin)"""
    
    query = db.query(Claim)
    
    if status_filter:
        query = query.filter(Claim.status == status_filter)
    
    if drop_id:
        query = query.filter(Claim.drop_id == drop_id)
    
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return claims


@router.put("/claims/{claim_id}/approve", response_model=ClaimResponse)
async def approve_claim(
    claim_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Claim'i manuel olarak onayla (Sadece Admin)"""
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim bulunamadı"
        )
    
    if claim.status == ClaimStatus.APPROVED:
        return claim  # Zaten onaylanmış
    
    claim.status = ClaimStatus.APPROVED
    claim.is_verified = True
    claim.verified_at = datetime.utcnow()
    claim.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(claim)
    
    return claim


@router.put("/claims/{claim_id}/reject", response_model=ClaimResponse)
async def reject_claim(
    claim_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Claim'i reddet (Sadece Admin)"""
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim bulunamadı"
        )
    
    if claim.status == ClaimStatus.REJECTED:
        return claim  # Zaten reddedilmiş
    
    # Stok geri al
    drop = db.query(Drop).filter(Drop.id == claim.drop_id).first()
    if drop:
        drop.claimed_quantity -= claim.quantity
        drop.remaining_quantity += claim.quantity
        
        # Drop tamamlandı ise tekrar aktif yap
        if drop.status == DropStatus.COMPLETED and drop.remaining_quantity > 0:
            drop.status = DropStatus.ACTIVE
    
    claim.status = ClaimStatus.REJECTED
    claim.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(claim)
    
    return claim


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Platform istatistiklerini getir (Sadece Admin)"""
    
    total_drops = db.query(Drop).count()
    active_drops = db.query(Drop).filter(
        Drop.is_active == True,
        Drop.status == DropStatus.ACTIVE
    ).count()
    
    total_claims = db.query(Claim).count()
    pending_claims = db.query(Claim).filter(Claim.status == ClaimStatus.PENDING).count()
    approved_claims = db.query(Claim).filter(Claim.status == ClaimStatus.APPROVED).count()
    
    total_waitlist = db.query(Waitlist).count()
    
    return StatsResponse(
        total_drops=total_drops,
        active_drops=active_drops,
        total_claims=total_claims,
        pending_claims=pending_claims,
        approved_claims=approved_claims,
        total_users_on_waitlist=total_waitlist
    )


@router.get("/drops/{drop_id}/waitlist")
async def get_drop_waitlist(
    drop_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Drop'un bekleme listesini getir (Sadece Admin)"""
    
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    waitlist = db.query(Waitlist).filter(
        Waitlist.drop_id == drop_id
    ).order_by(Waitlist.created_at.asc()).offset(skip).limit(limit).all()
    
    return waitlist


@router.get("/drops/{drop_id}/claims")
async def get_drop_claims(
    drop_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Drop'un claim'lerini getir (Sadece Admin)"""
    
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    claims = db.query(Claim).filter(
        Claim.drop_id == drop_id
    ).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    
    return claims

