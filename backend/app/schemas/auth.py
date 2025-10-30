"""Authentication schemas."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class Token(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"
    role: str
    business_id: Optional[UUID] = None


class TokenData(BaseModel):
    """Token payload data."""

    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    business_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """User login request."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = Field(default=UserRole.BASE_USER, description="User role")
    business_id: Optional[UUID] = Field(None, description="Business ID (required for non-system admins)")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    role: str
    business_id: Optional[UUID]
    sso_enabled: bool
    sso_provider: Optional[str]
    last_password_change: Optional[datetime]
    password_reset_required: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    business_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    sso_enabled: Optional[bool] = None
    password_reset_required: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class PasswordChange(BaseModel):
    """Password change request."""

    old_password: str
    new_password: str = Field(..., min_length=6)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
