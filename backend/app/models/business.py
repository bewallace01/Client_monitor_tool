"""Business model for multi-tenancy support."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.connection import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Business(Base):
    """Business/Organization model for multi-tenant data isolation."""

    __tablename__ = "businesses"

    # Primary Key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Business Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # Company size
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tier = Column(String(50), nullable=True)  # e.g., "free", "starter", "professional", "enterprise"
    subscription_status = Column(String(50), nullable=True)  # e.g., "trial", "active", "suspended", "cancelled"
    trial_ends_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # API Key Management (hashed)
    api_key_hash = Column(String(255), nullable=True)

    # SSO Configuration (prepared for future use)
    sso_enabled = Column(Boolean, default=False, nullable=False)
    sso_provider = Column(String(50), nullable=True)  # "google", "microsoft", "okta", etc.
    sso_config = Column(Text, nullable=True)  # JSON string for provider-specific config
    sso_domain = Column(String(255), nullable=True)  # Email domain for SSO (e.g., "company.com")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="business", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="business", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="business", cascade="all, delete-orphan")
    api_configs = relationship("APIConfig", back_populates="business", cascade="all, delete-orphan")
    job_runs = relationship("JobRun", back_populates="business", cascade="all, delete-orphan")
    api_request_logs = relationship("APIRequestLog", back_populates="business", cascade="all, delete-orphan")
    circuit_breakers = relationship("CircuitBreaker", back_populates="business", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.name}', tier='{self.tier}', active={self.is_active})>"
