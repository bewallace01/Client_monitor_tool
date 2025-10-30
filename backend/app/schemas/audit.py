"""AuditLog Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: UUID
    business_id: Optional[UUID] = None
    user_id: Optional[int] = None

    # What changed
    table_name: str
    record_id: str
    action: str  # "CREATE", "UPDATE", "DELETE"

    # Change details (JSON strings)
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    changed_fields: Optional[str] = None

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    notes: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440006",
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": 1,
                "table_name": "clients",
                "record_id": "550e8400-e29b-41d4-a716-446655440000",
                "action": "UPDATE",
                "old_values": '{"health_score": 75.0}',
                "new_values": '{"health_score": 85.0}',
                "changed_fields": '["health_score"]',
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "notes": None,
                "created_at": "2025-10-16T12:00:00Z"
            }
        }
    )


class AuditLogFilters(BaseModel):
    """Query parameters for filtering audit logs."""
    business_id: Optional[UUID] = None
    user_id: Optional[int] = None
    table_name: Optional[str] = None
    record_id: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Schema for paginated list of audit logs."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[AuditLogResponse]

    model_config = ConfigDict(from_attributes=True)
