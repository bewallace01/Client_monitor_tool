"""
API Configuration Model
Multi-tenant API configuration storage with encryption support
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.business import GUID


class APIConfig(Base):
    """
    API Configuration for each business
    Stores API keys, tokens, and configuration for various third-party services
    """
    __tablename__ = "api_configs"

    # Primary Key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign Key to Business (multi-tenancy)
    business_id = Column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # API Provider Information
    provider = Column(String(100), nullable=False)  # e.g., "newsapi", "openai", "hubspot", "salesforce"
    provider_name = Column(String(200), nullable=False)  # Display name: "NewsAPI", "OpenAI GPT-4", "HubSpot CRM"

    # API Credentials (encrypted)
    api_key = Column(Text, nullable=True)  # Primary API key (encrypted)
    api_secret = Column(Text, nullable=True)  # Secondary secret if needed (encrypted)
    access_token = Column(Text, nullable=True)  # OAuth access token (encrypted)
    refresh_token = Column(Text, nullable=True)  # OAuth refresh token (encrypted)

    # Additional Configuration (JSON)
    config_data = Column(Text, nullable=True)  # JSON string for provider-specific settings

    # Usage & Rate Limiting
    max_tokens_per_month = Column(Integer, nullable=True)  # Token/request limit
    tokens_used_current_month = Column(Integer, default=0)
    last_reset_date = Column(DateTime, nullable=True)  # For monthly reset
    rate_limit_per_hour = Column(Integer, nullable=True)  # Requests per hour
    requests_this_hour = Column(Integer, default=0)
    last_request_time = Column(DateTime, nullable=True)

    # Cost Tracking
    cost_per_1k_tokens = Column(Float, nullable=True)  # For cost estimation
    estimated_monthly_cost = Column(Float, nullable=True)

    # Connection Status
    is_active = Column(Boolean, default=True)  # Can be disabled without deletion
    last_tested_at = Column(DateTime, nullable=True)
    last_test_status = Column(String(50), nullable=True)  # "success", "failed", "pending"
    last_test_message = Column(Text, nullable=True)  # Error message or success details

    # File Storage Reference
    config_file_path = Column(String(500), nullable=True)  # Path to JSON config file

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_user_id = Column(Integer, nullable=True)
    updated_by_user_id = Column(Integer, nullable=True)

    # Relationships
    business = relationship("Business", back_populates="api_configs")
    request_logs = relationship("APIRequestLog", back_populates="api_config", cascade="all, delete-orphan")
    circuit_breaker = relationship("CircuitBreaker", back_populates="api_config", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<APIConfig(id={self.id}, business_id={self.business_id}, provider={self.provider})>"

    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary, optionally masking sensitive data"""
        data = {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "provider": self.provider,
            "provider_name": self.provider_name,
            "max_tokens_per_month": self.max_tokens_per_month,
            "tokens_used_current_month": self.tokens_used_current_month,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "requests_this_hour": self.requests_this_hour,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "is_active": self.is_active,
            "last_tested_at": self.last_tested_at.isoformat() if self.last_tested_at else None,
            "last_test_status": self.last_test_status,
            "last_test_message": self.last_test_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            data.update({
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "config_data": self.config_data,
            })
        else:
            # Mask sensitive data
            data.update({
                "api_key_masked": self._mask_key(self.api_key) if self.api_key else None,
                "has_secret": bool(self.api_secret),
                "has_access_token": bool(self.access_token),
                "has_refresh_token": bool(self.refresh_token),
            })

        return data

    @staticmethod
    def _mask_key(key: Optional[str]) -> Optional[str]:
        """Mask API key showing only first 4 and last 4 characters"""
        if not key or len(key) < 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"
