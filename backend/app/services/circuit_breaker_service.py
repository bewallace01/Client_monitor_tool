"""Circuit Breaker Service for API failure management."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.circuit_breaker import CircuitBreaker, CircuitBreakerState
from app.models.api_config import APIConfig

logger = logging.getLogger(__name__)


class CircuitBreakerService:
    """Manage circuit breaker states for API integrations."""

    @staticmethod
    def get_or_create_breaker(
        db: Session,
        api_config_id: UUID,
        business_id: UUID,
        provider: str
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create a new one.

        Args:
            db: Database session
            api_config_id: API config UUID
            business_id: Business UUID
            provider: API provider name

        Returns:
            CircuitBreaker instance
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if not breaker:
            breaker = CircuitBreaker(
                business_id=business_id,
                api_config_id=api_config_id,
                provider=provider,
                state=CircuitBreakerState.CLOSED
            )
            db.add(breaker)
            db.commit()
            db.refresh(breaker)
            logger.info(f"Created new circuit breaker for {provider}")

        return breaker

    @staticmethod
    def should_allow_request(
        db: Session,
        api_config_id: UUID
    ) -> tuple[bool, Optional[str]]:
        """
        Check if requests should be allowed for this API.

        Args:
            db: Database session
            api_config_id: API config UUID

        Returns:
            Tuple of (should_allow, reason_if_blocked)
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if not breaker:
            # No circuit breaker exists yet, allow request
            return True, None

        if breaker.manually_disabled:
            return False, f"API manually disabled: {breaker.disabled_reason}"

        if breaker.state == CircuitBreakerState.CLOSED:
            return True, None

        if breaker.state == CircuitBreakerState.OPEN:
            # Check if timeout has elapsed to try half-open
            if breaker.can_transition_to_half_open():
                CircuitBreakerService._transition_to_half_open(db, breaker)
                logger.info(f"Circuit breaker {breaker.provider} transitioned to HALF_OPEN")
                return True, None
            else:
                elapsed = (datetime.utcnow() - breaker.opened_at).total_seconds() if breaker.opened_at else 0
                remaining = breaker.timeout_seconds - elapsed
                return False, f"Circuit open due to failures. Retry in {int(remaining)}s. Last error: {breaker.last_failure_reason}"

        if breaker.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited requests to test if service recovered
            return True, None

        return True, None

    @staticmethod
    def record_success(
        db: Session,
        api_config_id: UUID
    ) -> None:
        """
        Record a successful API request.

        Args:
            db: Database session
            api_config_id: API config UUID
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if not breaker:
            return

        breaker.success_count += 1
        breaker.consecutive_successes += 1
        breaker.consecutive_failures = 0
        breaker.last_success_at = datetime.utcnow()

        # If in HALF_OPEN state and enough successes, close the circuit
        if breaker.state == CircuitBreakerState.HALF_OPEN:
            if breaker.consecutive_successes >= breaker.success_threshold:
                CircuitBreakerService._transition_to_closed(db, breaker)
                logger.info(f"Circuit breaker {breaker.provider} recovered and closed")

        db.commit()

    @staticmethod
    def record_failure(
        db: Session,
        api_config_id: UUID,
        error_message: str,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record a failed API request.

        Args:
            db: Database session
            api_config_id: API config UUID
            error_message: Error message
            error_type: Type of error (rate_limit, timeout, etc.)
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if not breaker:
            return

        breaker.failure_count += 1
        breaker.consecutive_failures += 1
        breaker.consecutive_successes = 0
        breaker.last_failure_at = datetime.utcnow()
        breaker.last_failure_reason = error_message[:500]  # Truncate if too long
        breaker.last_failure_type = error_type

        # If in CLOSED or HALF_OPEN state and threshold exceeded, open the circuit
        if breaker.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN]:
            if breaker.consecutive_failures >= breaker.failure_threshold:
                CircuitBreakerService._transition_to_open(db, breaker)
                logger.error(
                    f"Circuit breaker {breaker.provider} opened after {breaker.consecutive_failures} "
                    f"consecutive failures. Last error: {error_message}"
                )

        db.commit()

    @staticmethod
    def manually_disable(
        db: Session,
        api_config_id: UUID,
        reason: str,
        user_id: Optional[int] = None
    ) -> CircuitBreaker:
        """
        Manually disable an API.

        Args:
            db: Database session
            api_config_id: API config UUID
            reason: Reason for disabling
            user_id: User who disabled it

        Returns:
            Updated CircuitBreaker
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if breaker:
            breaker.manually_disabled = True
            breaker.disabled_reason = reason
            breaker.disabled_by_user_id = user_id
            breaker.disabled_at = datetime.utcnow()
            db.commit()
            db.refresh(breaker)
            logger.info(f"Circuit breaker {breaker.provider} manually disabled by user {user_id}")

        return breaker

    @staticmethod
    def manually_enable(
        db: Session,
        api_config_id: UUID
    ) -> CircuitBreaker:
        """
        Manually re-enable an API.

        Args:
            db: Database session
            api_config_id: API config UUID

        Returns:
            Updated CircuitBreaker
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if breaker:
            breaker.manually_disabled = False
            breaker.disabled_reason = None
            breaker.disabled_by_user_id = None
            breaker.disabled_at = None
            # Reset to closed state
            CircuitBreakerService._transition_to_closed(db, breaker)
            logger.info(f"Circuit breaker {breaker.provider} manually enabled")

        return breaker

    @staticmethod
    def reset_breaker(
        db: Session,
        api_config_id: UUID
    ) -> CircuitBreaker:
        """
        Reset circuit breaker to closed state and clear counters.

        Args:
            db: Database session
            api_config_id: API config UUID

        Returns:
            Updated CircuitBreaker
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if breaker:
            breaker.consecutive_failures = 0
            breaker.consecutive_successes = 0
            CircuitBreakerService._transition_to_closed(db, breaker)
            logger.info(f"Circuit breaker {breaker.provider} manually reset")

        return breaker

    @staticmethod
    def get_breaker_status(
        db: Session,
        api_config_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get current status of a circuit breaker.

        Args:
            db: Database session
            api_config_id: API config UUID

        Returns:
            Status dict or None if not found
        """
        breaker = db.query(CircuitBreaker).filter(
            CircuitBreaker.api_config_id == api_config_id
        ).first()

        if not breaker:
            return None

        can_request, block_reason = CircuitBreakerService.should_allow_request(db, api_config_id)

        return {
            "api_config_id": str(breaker.api_config_id),
            "provider": breaker.provider,
            "state": breaker.state.value,
            "manually_disabled": breaker.manually_disabled,
            "disabled_reason": breaker.disabled_reason,
            "can_make_requests": can_request,
            "block_reason": block_reason,
            "failure_count": breaker.failure_count,
            "consecutive_failures": breaker.consecutive_failures,
            "success_count": breaker.success_count,
            "consecutive_successes": breaker.consecutive_successes,
            "failure_threshold": breaker.failure_threshold,
            "success_threshold": breaker.success_threshold,
            "timeout_seconds": breaker.timeout_seconds,
            "last_failure_at": breaker.last_failure_at.isoformat() if breaker.last_failure_at else None,
            "last_failure_reason": breaker.last_failure_reason,
            "last_failure_type": breaker.last_failure_type,
            "last_success_at": breaker.last_success_at.isoformat() if breaker.last_success_at else None,
            "opened_at": breaker.opened_at.isoformat() if breaker.opened_at else None,
        }

    @staticmethod
    def get_all_breaker_statuses(
        db: Session,
        business_id: UUID
    ) -> list[Dict[str, Any]]:
        """
        Get status of all circuit breakers for a business.

        Args:
            db: Database session
            business_id: Business UUID

        Returns:
            List of status dicts
        """
        breakers = db.query(CircuitBreaker).filter(
            CircuitBreaker.business_id == business_id
        ).all()

        statuses = []
        for breaker in breakers:
            status = CircuitBreakerService.get_breaker_status(db, breaker.api_config_id)
            if status:
                statuses.append(status)

        return statuses

    # Private helper methods for state transitions

    @staticmethod
    def _transition_to_open(db: Session, breaker: CircuitBreaker) -> None:
        """Transition breaker to OPEN state."""
        breaker.state = CircuitBreakerState.OPEN
        breaker.opened_at = datetime.utcnow()
        breaker.half_opened_at = None
        breaker.closed_at = None

    @staticmethod
    def _transition_to_half_open(db: Session, breaker: CircuitBreaker) -> None:
        """Transition breaker to HALF_OPEN state."""
        breaker.state = CircuitBreakerState.HALF_OPEN
        breaker.half_opened_at = datetime.utcnow()
        breaker.consecutive_successes = 0
        breaker.consecutive_failures = 0

    @staticmethod
    def _transition_to_closed(db: Session, breaker: CircuitBreaker) -> None:
        """Transition breaker to CLOSED state."""
        breaker.state = CircuitBreakerState.CLOSED
        breaker.closed_at = datetime.utcnow()
        breaker.opened_at = None
        breaker.half_opened_at = None
        breaker.consecutive_failures = 0
