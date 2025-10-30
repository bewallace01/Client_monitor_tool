"""Audit log model for tracking all data changes."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class AuditLog(Base):
    """Track all data changes for compliance, debugging, and security.

    This model logs all CREATE, UPDATE, and DELETE operations across the platform,
    providing a complete audit trail for regulatory compliance and incident investigation.
    """

    __tablename__ = "audit_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Context - Who and What Business
    business_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("businesses.id"),
        nullable=True,
        index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # What changed
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # UUID or int as string
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # "CREATE", "UPDATE", "DELETE"

    # Change details (JSON)
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object of old field values
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object of new field values
    changed_fields: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of field names that changed

    # Context metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Additional context
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Optional description of the change

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    business = relationship("Business")
    user = relationship("User")

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_audit_table_record", "table_name", "record_id"),
        Index("ix_audit_business_created", "business_id", "created_at"),
        Index("ix_audit_user_created", "user_id", "created_at"),
        Index("ix_audit_action_created", "action", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', table='{self.table_name}', record_id='{self.record_id}')>"
