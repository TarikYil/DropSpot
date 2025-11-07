from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str = Field(..., description="Email veya kullanıcı adı")
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

