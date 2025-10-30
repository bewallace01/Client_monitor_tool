"""Base Pydantic schemas with common fields."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = 1
    page_size: int = 50

    model_config = ConfigDict(from_attributes=True)

    @property
    def offset(self) -> int:
        """Calculate offset for SQL queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for SQL queries."""
        return self.page_size


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
