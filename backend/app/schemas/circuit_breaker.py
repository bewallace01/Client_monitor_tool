"""Circuit Breaker schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class CircuitBreakerStatus(BaseModel):
    """Circuit breaker status response."""

    api_config_id: str
    provider: str
    state: str  # closed, open, half_open
    manually_disabled: bool
    disabled_reason: Optional[str] = None
    can_make_requests: bool
    block_reason: Optional[str] = None

    # Stats
    failure_count: int
    consecutive_failures: int
    success_count: int
    consecutive_successes: int
    failure_threshold: int
    success_threshold: int
    timeout_seconds: int

    # Timestamps
    last_failure_at: Optional[datetime] = None
    last_failure_reason: Optional[str] = None
    last_failure_type: Optional[str] = None
    last_success_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CircuitBreakerList(BaseModel):
    """List of circuit breaker statuses."""

    items: list[CircuitBreakerStatus]
    total: int


class CircuitBreakerManualControl(BaseModel):
    """Manual control for circuit breaker."""

    action: str = Field(..., pattern="^(enable|disable|reset)$")
    reason: Optional[str] = None
