"""Pydantic schemas for Business model."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class BusinessBase(BaseModel):
    """Base Business schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Business name")
    domain: Optional[str] = Field(None, max_length=255, description="Business website domain")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    size: Optional[str] = Field(None, max_length=50, description="Company size")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    address: Optional[str] = Field(None, description="Business address")
    subscription_tier: Optional[str] = Field(None, max_length=50, description="Subscription tier")
    subscription_status: Optional[str] = Field(None, max_length=50, description="Subscription status")


class BusinessCreate(BusinessBase):
    """Schema for creating a new business."""

    is_active: Optional[bool] = Field(default=True, description="Whether business is active")
    api_key: Optional[str] = Field(None, description="Initial API key (will be hashed)")
    sso_enabled: bool = Field(default=False, description="Enable SSO")
    sso_provider: Optional[str] = Field(None, max_length=50, description="SSO provider")
    sso_domain: Optional[str] = Field(None, max_length=255, description="Email domain for SSO")


class BusinessUpdate(BaseModel):
    """Schema for updating a business."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    subscription_tier: Optional[str] = Field(None, max_length=50)
    subscription_status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    sso_enabled: Optional[bool] = None
    sso_provider: Optional[str] = Field(None, max_length=50)
    sso_domain: Optional[str] = Field(None, max_length=255)


class BusinessResponse(BusinessBase):
    """Schema for business response."""

    id: UUID
    is_active: bool
    sso_enabled: bool = False
    sso_provider: Optional[str] = None
    sso_domain: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    has_api_key: bool = Field(default=False, description="Whether business has an API key set")

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_key(cls, business):
        """Create response with has_api_key flag."""
        data = {
            **business.__dict__,
            "has_api_key": business.api_key_hash is not None
        }
        return cls(**data)


class BusinessSummary(BaseModel):
    """Summary schema for business (for dropdowns, etc.)."""

    id: UUID
    name: str
    subscription_tier: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class BusinessStats(BaseModel):
    """Business statistics."""

    total_users: int
    active_users: int
    total_clients: int
    total_events: int
    api_key_set: bool


class BusinessWithStats(BusinessResponse):
    """Business response with statistics."""

    stats: BusinessStats


class BusinessListResponse(BaseModel):
    """Paginated list of businesses."""

    items: list[BusinessResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class APIKeyResponse(BaseModel):
    """Response when generating a new API key."""

    api_key: str = Field(..., description="The newly generated API key (plain text, show once)")
    business_id: UUID
    message: str = Field(default="API key generated successfully. Save it securely, it won't be shown again.")
