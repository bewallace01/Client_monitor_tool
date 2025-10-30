"""Circuit Breaker model for API failure management."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database.connection import Base
from app.models.business import GUID


class CircuitBreakerState(str, enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Circuit tripped, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker(Base):
    """Track circuit breaker state for each API configuration."""

    __tablename__ = "circuit_breakers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id = Column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    api_config_id = Column(GUID(), ForeignKey("api_configs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Provider info
    provider = Column(String(50), nullable=False, index=True)

    # Circuit breaker state
    state = Column(SQLEnum(CircuitBreakerState), nullable=False, default=CircuitBreakerState.CLOSED, index=True)

    # Failure tracking
    failure_count = Column(Integer, nullable=False, default=0)
    consecutive_failures = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    consecutive_successes = Column(Integer, nullable=False, default=0)

    # Thresholds (configurable per API)
    failure_threshold = Column(Integer, nullable=False, default=5)  # Open circuit after N failures
    success_threshold = Column(Integer, nullable=False, default=2)  # Close circuit after N successes in half-open
    timeout_seconds = Column(Integer, nullable=False, default=60)  # How long to wait before trying half-open

    # Last failure info
    last_failure_at = Column(DateTime, nullable=True, index=True)
    last_failure_reason = Column(Text, nullable=True)
    last_failure_type = Column(String(100), nullable=True)  # rate_limit, timeout, auth_error, etc.

    # Last success info
    last_success_at = Column(DateTime, nullable=True)

    # Circuit opened/closed times
    opened_at = Column(DateTime, nullable=True)
    half_opened_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Manual override
    manually_disabled = Column(Boolean, nullable=False, default=False)  # Manually disable API
    disabled_reason = Column(Text, nullable=True)
    disabled_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    disabled_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="circuit_breakers")
    api_config = relationship("APIConfig", back_populates="circuit_breaker", uselist=False)
    disabled_by_user = relationship("User", foreign_keys=[disabled_by_user_id])

    def __repr__(self):
        return f"<CircuitBreaker {self.provider} - {self.state}>"

    def should_allow_request(self) -> bool:
        """Determine if requests should be allowed based on circuit state."""
        if self.manually_disabled:
            return False

        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has elapsed to try half-open
            if self.opened_at:
                elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
                return elapsed >= self.timeout_seconds
            return False

        if self.state == CircuitBreakerState.HALF_OPEN:
            return True

        return False

    def can_transition_to_half_open(self) -> bool:
        """Check if enough time has passed to transition to half-open."""
        if self.state != CircuitBreakerState.OPEN:
            return False

        if not self.opened_at:
            return True

        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        return elapsed >= self.timeout_seconds
