from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    can_create_drops: bool = False
    can_edit_drops: bool = False
    can_delete_drops: bool = False
    can_approve_claims: bool = False
    can_manage_users: bool = False
    can_view_analytics: bool = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    can_create_drops: Optional[bool] = None
    can_edit_drops: Optional[bool] = None
    can_delete_drops: Optional[bool] = None
    can_approve_claims: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_analytics: Optional[bool] = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


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
    roles: List[RoleResponse] = []


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    roles: List[RoleResponse] = []


class UserWithPermissions(UserResponse):
    """Kullanıcı + yetkileri"""
    permissions: dict


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


# Role Assignment Schemas
class UserRoleAssign(BaseModel):
    role_id: int


class UserRoleRemove(BaseModel):
    role_id: int
