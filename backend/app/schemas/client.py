"""Client Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientBase(BaseModel):
    """Base Client schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Client name")
    domain: Optional[str] = Field(None, max_length=200, description="Client domain/website")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    description: Optional[str] = Field(None, description="Client description")

    # Company Details
    company_size: Optional[str] = Field(None, max_length=50, description="Company size (e.g., 1-10, 11-50)")
    revenue_range: Optional[str] = Field(None, max_length=50, description="Revenue range (e.g., $1M-$10M)")
    headquarters_location: Optional[str] = Field(None, max_length=200, description="HQ location")
    founded_year: Optional[int] = Field(None, ge=1800, le=2100, description="Year founded")

    # Search configuration
    search_keywords: Optional[str] = Field(None, description="Comma-separated search keywords")
    monitoring_frequency: str = Field(default="daily", description="Monitoring frequency (hourly, daily, weekly)")

    # Customer Success
    tier: Optional[str] = Field(None, max_length=50, description="Client tier (e.g., Enterprise, Mid-Market, SMB)")
    health_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Client health score (0-100)")
    notes: Optional[str] = Field(None, description="Internal notes")

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize domain."""
        if v:
            # Remove protocol if present
            v = v.replace('https://', '').replace('http://', '')
            # Remove trailing slash
            v = v.rstrip('/')
            # Convert to lowercase
            v = v.lower()
        return v

    @field_validator('search_keywords')
    @classmethod
    def validate_keywords(cls, v: Optional[str]) -> Optional[str]:
        """Validate search keywords format."""
        if v:
            # Trim whitespace around keywords
            keywords = [k.strip() for k in v.split(',') if k.strip()]
            v = ', '.join(keywords)
        return v


class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    is_active: bool = Field(default=True, description="Whether client monitoring is active")
    assigned_to_user_id: Optional[int] = Field(None, description="User ID of assigned account owner")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acme Corporation",
                "domain": "acme.com",
                "industry": "Technology",
                "description": "Leading provider of enterprise software",
                "company_size": "51-200",
                "revenue_range": "$10M-$50M",
                "headquarters_location": "San Francisco, CA",
                "founded_year": 2015,
                "search_keywords": "Acme Corp, ACME, Acme Software",
                "monitoring_frequency": "daily",
                "tier": "Enterprise",
                "health_score": 85.0,
                "is_active": True,
                "assigned_to_user_id": 1,
                "notes": "Key strategic account"
            }
        }
    )


class ClientUpdate(BaseModel):
    """Schema for updating an existing client (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    domain: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    # Company Details
    company_size: Optional[str] = Field(None, max_length=50)
    revenue_range: Optional[str] = Field(None, max_length=50)
    headquarters_location: Optional[str] = Field(None, max_length=200)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)

    # Search configuration
    search_keywords: Optional[str] = None
    monitoring_frequency: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

    # Customer Success
    assigned_to_user_id: Optional[int] = None
    tier: Optional[str] = Field(None, max_length=50)
    health_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    notes: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": False,
                "health_score": 65.0,
                "notes": "Account temporarily paused"
            }
        }
    )

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize domain."""
        if v:
            v = v.replace('https://', '').replace('http://', '')
            v = v.rstrip('/')
            v = v.lower()
        return v

    @field_validator('search_keywords')
    @classmethod
    def validate_keywords(cls, v: Optional[str]) -> Optional[str]:
        """Validate search keywords format."""
        if v:
            keywords = [k.strip() for k in v.split(',') if k.strip()]
            v = ', '.join(keywords)
        return v


class ClientResponse(ClientBase):
    """Schema for client response with all fields including metadata."""
    id: UUID
    business_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None

    # Ownership
    assigned_to_user_id: Optional[int] = None
    created_by_user_id: Optional[int] = None

    # Soft delete
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Acme Corporation",
                "domain": "acme.com",
                "industry": "Technology",
                "description": "Leading provider of enterprise software",
                "company_size": "51-200",
                "revenue_range": "$10M-$50M",
                "headquarters_location": "San Francisco, CA",
                "founded_year": 2015,
                "search_keywords": "Acme Corp, ACME, Acme Software",
                "monitoring_frequency": "daily",
                "is_active": True,
                "created_at": "2025-10-16T10:30:00Z",
                "updated_at": "2025-10-16T10:30:00Z",
                "last_checked_at": "2025-10-16T15:45:00Z",
                "assigned_to_user_id": 1,
                "created_by_user_id": 1,
                "tier": "Enterprise",
                "health_score": 85.0,
                "notes": "Key strategic account",
                "is_deleted": False,
                "deleted_at": None
            }
        }
    )


class ClientListResponse(BaseModel):
    """Schema for paginated list of clients."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ClientResponse]

    model_config = ConfigDict(from_attributes=True)


class ClientSummary(BaseModel):
    """Minimal client info for dropdowns and references."""
    id: UUID
    name: str
    domain: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ClientStats(BaseModel):
    """Client statistics and metrics."""
    total_clients: int
    active_clients: int
    inactive_clients: int
    clients_by_tier: dict[str, int]
    clients_by_industry: dict[str, int]

    model_config = ConfigDict(from_attributes=True)
