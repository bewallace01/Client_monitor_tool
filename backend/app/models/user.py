"""User model for authentication."""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.business import GUID  # Import GUID from business model


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control."""

    SYSTEM_ADMIN = "system_admin"  # Global access to entire platform
    BUSINESS_ADMIN = "business_admin"  # Business-level admin, manages users and business
    BASE_USER = "base_user"  # Limited access, read-only for dashboard, clients, events


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)  # Kept for backwards compatibility

    # Role-Based Access Control
    role = Column(Enum(UserRole), default=UserRole.BASE_USER, nullable=False, index=True)

    # Business/Organization Association (nullable for SYSTEM_ADMIN)
    business_id = Column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True, index=True)

    # SSO Configuration
    sso_enabled = Column(Boolean, default=False, nullable=False)
    sso_provider = Column(String(50), nullable=True)

    # Password Management
    last_password_change = Column(DateTime, default=datetime.utcnow, nullable=True)
    password_reset_required = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    business = relationship("Business", back_populates="users")
    assigned_clients = relationship(
        "Client",
        foreign_keys="Client.assigned_to_user_id",
        back_populates="assigned_to_user"
    )
    event_interactions = relationship("EventUserInteraction", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', business_id='{self.business_id}')>"

    @property
    def is_system_admin(self) -> bool:
        """Check if user is a system administrator."""
        return self.role == UserRole.SYSTEM_ADMIN

    @property
    def is_business_admin(self) -> bool:
        """Check if user is a business administrator."""
        return self.role == UserRole.BUSINESS_ADMIN

    @property
    def is_base_user(self) -> bool:
        """Check if user is a base user."""
        return self.role == UserRole.BASE_USER
