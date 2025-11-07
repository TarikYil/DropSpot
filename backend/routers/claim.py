from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from database import get_db
from models import Drop, Claim, Waitlist, DropStatus, ClaimStatus
from schemas import ClaimCreate, ClaimResponse, ClaimVerify, MessageResponse
from utils.security import get_current_user, calculate_distance
from utils.seed_manager import seed_manager

router = APIRouter()


@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Drop için claim (hak talebi) oluştur
    
    İdempotent: Aynı kullanıcı aynı drop için birden fazla claim yapamaz
    Stok kontrolü: Stok biterse 403 döner
    """
    drop_id = claim_data.drop_id
    user_id = current_user["user_id"]
    
    # Drop kontrolü
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop bulunamadı"
        )
    
    # Drop aktif mi ve claim zamanı geldi mi kontrol et
    now = datetime.utcnow()
    if not drop.is_active or drop.status != DropStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu drop aktif değil"
        )
    
    if now < drop.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drop henüz başlamadı"
        )
    
    if now > drop.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drop süresi dolmuş"
        )
    
    # Kullanıcı waitlist'te mi kontrol et (opsiyonel zorunlu kılabilirsiniz)
    in_waitlist = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == user_id
        )
    ).first()
    
    if not in_waitlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Önce bekleme listesine katılmalısınız"
        )
    
    # Kullanıcı zaten claim yapmış mı kontrol et (İdempotent)
    existing_claim = db.query(Claim).filter(
        and_(
            Claim.drop_id == drop_id,
            Claim.user_id == user_id
        )
    ).first()
    
    if existing_claim:
        # Zaten claim yapmış - mevcut claim'i döndür (idempotent)
        return existing_claim
    
    # Stok kontrolü
    if drop.remaining_quantity < claim_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Yetersiz stok. Kalan: {drop.remaining_quantity}"
        )
    
    # Mesafe kontrolü
    distance = calculate_distance(
        claim_data.claim_latitude, claim_data.claim_longitude,
        drop.latitude, drop.longitude
    )
    
    if distance > drop.radius_meters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Drop lokasyonuna çok uzaksınız. Mesafe: {round(distance, 2)}m, Gerekli: {drop.radius_meters}m"
        )
    
    # Benzersiz doğrulama kodu oluştur (seed-based)
    verification_code = seed_manager.generate_claim_code(
        user_id=user_id,
        drop_id=drop_id,
        timestamp=now
    )
    
    # Yeni claim oluştur
    new_claim = Claim(
        drop_id=drop_id,
        user_id=user_id,
        quantity=claim_data.quantity,
        claim_latitude=claim_data.claim_latitude,
        claim_longitude=claim_data.claim_longitude,
        distance_from_drop=round(distance, 2),
        verification_code=verification_code,
        status=ClaimStatus.PENDING
    )
    
    db.add(new_claim)
    
    # Drop stok güncelle
    drop.claimed_quantity += claim_data.quantity
    drop.remaining_quantity -= claim_data.quantity
    
    # Stok bittiyse drop'u tamamlandı olarak işaretle
    if drop.remaining_quantity <= 0:
        drop.status = DropStatus.COMPLETED
    
    db.commit()
    db.refresh(new_claim)
    
    return new_claim


@router.post("/{claim_id}/verify", response_model=ClaimResponse)
async def verify_claim(
    claim_id: int,
    verify_data: ClaimVerify,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim'i doğrulama kodu ile onayla"""
    user_id = current_user["user_id"]
    
    # Claim kontrolü
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim bulunamadı"
        )
    
    # Kullanıcı kontrolü
    if claim.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu claim size ait değil"
        )
    
    # Zaten doğrulanmış mı
    if claim.is_verified:
        return claim
    
    # Doğrulama kodu kontrolü
    if claim.verification_code != verify_data.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz doğrulama kodu"
        )
    
    # Claim'i onayla
    claim.is_verified = True
    claim.verified_at = datetime.utcnow()
    claim.status = ClaimStatus.APPROVED
    
    db.commit()
    db.refresh(claim)
    
    return claim


@router.get("/my-claims", response_model=list[ClaimResponse])
async def get_my_claims(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının tüm claim'lerini listele"""
    user_id = current_user["user_id"]
    
    claims = db.query(Claim).filter(
        Claim.user_id == user_id
    ).order_by(Claim.created_at.desc()).all()
    
    return claims


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir claim'in detaylarını getir"""
    user_id = current_user["user_id"]
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim bulunamadı"
        )
    
    # Kullanıcı kontrolü (veya admin)
    if claim.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu claim'e erişim yetkiniz yok"
        )
    
    return claim


@router.delete("/{claim_id}", response_model=MessageResponse)
async def cancel_claim(
    claim_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim'i iptal et (henüz doğrulanmamışsa)"""
    user_id = current_user["user_id"]
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim bulunamadı"
        )
    
    if claim.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu claim size ait değil"
        )
    
    if claim.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doğrulanmış claim iptal edilemez"
        )
    
    # Drop stok geri al
    drop = db.query(Drop).filter(Drop.id == claim.drop_id).first()
    if drop:
        drop.claimed_quantity -= claim.quantity
        drop.remaining_quantity += claim.quantity
        
        # Eğer drop tamamlandı ise tekrar aktif yap
        if drop.status == DropStatus.COMPLETED:
            drop.status = DropStatus.ACTIVE
    
    # Claim'i sil
    db.delete(claim)
    db.commit()
    
    return MessageResponse(
        message="Claim başarıyla iptal edildi",
        detail=f"Claim ID: {claim_id}"
    )

