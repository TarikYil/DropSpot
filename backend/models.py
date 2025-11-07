from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum


class DropStatus(str, enum.Enum):
    """Drop durumları"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClaimStatus(str, enum.Enum):
    """Claim durumları"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Drop(Base):
    """Drop tablosu - ürün/hizmet drop'ları"""
    __tablename__ = "drops"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Drop bilgileri
    total_quantity = Column(Integer, nullable=False)
    claimed_quantity = Column(Integer, default=0)
    remaining_quantity = Column(Integer, nullable=False)
    
    # Lokasyon bilgileri
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    radius_meters = Column(Integer, default=100)  # Drop'un geçerli olduğu yarıçap (metre)
    
    # Zaman bilgileri
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Durum
    status = Column(Enum(DropStatus), default=DropStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    
    # Oluşturan kullanıcı (auth servisinden user_id)
    created_by = Column(Integer, nullable=False)
    
    # Timestamp'ler
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    claims = relationship("Claim", back_populates="drop")
    waitlist_entries = relationship("Waitlist", back_populates="drop")

    def __repr__(self):
        return f"<Drop(id={self.id}, title={self.title}, status={self.status})>"


class Claim(Base):
    """Claim tablosu - kullanıcıların drop talepları"""
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    drop_id = Column(Integer, ForeignKey("drops.id"), nullable=False)
    user_id = Column(Integer, nullable=False)  # Auth servisinden
    
    # Claim bilgileri
    status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    quantity = Column(Integer, default=1)
    
    # Konum doğrulama
    claim_latitude = Column(Float, nullable=False)
    claim_longitude = Column(Float, nullable=False)
    distance_from_drop = Column(Float, nullable=True)  # Metre cinsinden
    
    # QR kod veya doğrulama kodu
    verification_code = Column(String(50), unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp'ler
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    drop = relationship("Drop", back_populates="claims")

    def __repr__(self):
        return f"<Claim(id={self.id}, drop_id={self.drop_id}, user_id={self.user_id}, status={self.status})>"


class Waitlist(Base):
    """Waitlist tablosu - drop'lar için bekleme listesi"""
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    drop_id = Column(Integer, ForeignKey("drops.id"), nullable=False)
    user_id = Column(Integer, nullable=False)  # Auth servisinden
    
    # Waitlist bilgileri
    is_notified = Column(Boolean, default=False)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp'ler
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    drop = relationship("Drop", back_populates="waitlist_entries")

    def __repr__(self):
        return f"<Waitlist(id={self.id}, drop_id={self.drop_id}, user_id={self.user_id})>"

