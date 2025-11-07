from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from models import DropStatus, ClaimStatus


# Drop Schemas
class DropBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = None
    total_quantity: int = Field(..., gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    radius_meters: int = Field(default=100, gt=0)
    start_time: datetime
    end_time: datetime


class DropCreate(DropBase):
    pass


class DropUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = None
    total_quantity: Optional[int] = Field(None, gt=0)
    status: Optional[DropStatus] = None
    is_active: Optional[bool] = None


class DropResponse(DropBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    claimed_quantity: int
    remaining_quantity: int
    status: DropStatus
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DropWithDistance(DropResponse):
    """Kullanıcının konumuna göre mesafe bilgisi eklenmiş drop"""
    distance_meters: float


# Claim Schemas
class ClaimBase(BaseModel):
    drop_id: int
    quantity: int = Field(default=1, gt=0)
    claim_latitude: float = Field(..., ge=-90, le=90)
    claim_longitude: float = Field(..., ge=-180, le=180)


class ClaimCreate(ClaimBase):
    pass


class ClaimResponse(ClaimBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    status: ClaimStatus
    distance_from_drop: Optional[float] = None
    verification_code: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClaimVerify(BaseModel):
    verification_code: str


# Waitlist Schemas
class WaitlistCreate(BaseModel):
    drop_id: int


class WaitlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    drop_id: int
    user_id: int
    is_notified: bool
    notified_at: Optional[datetime] = None
    created_at: datetime


# Utility Schemas
class LocationQuery(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=100)


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class StatsResponse(BaseModel):
    total_drops: int
    active_drops: int
    total_claims: int
    pending_claims: int
    approved_claims: int
    total_users_on_waitlist: int

