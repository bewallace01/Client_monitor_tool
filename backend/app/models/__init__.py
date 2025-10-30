"""SQLAlchemy models for the application."""

from app.models.client import Client
from app.models.event import Event, EventCategory
from app.models.search_cache import SearchCache
from app.models.job_run import JobRun
from app.models.user import User, UserRole
from app.models.business import Business, GUID
from app.models.event_user_interaction import EventUserInteraction
from app.models.audit_log import AuditLog
from app.models.tag import Tag, ClientTag, EventTag
from app.models.notification import Notification
from app.models.api_config import APIConfig
from app.models.user_preference import UserPreference
from app.models.event_raw_data import EventRawData
from app.models.automation_schedule import AutomationSchedule
from app.models.email_log import EmailLog
from app.models.api_request_log import APIRequestLog
from app.models.circuit_breaker import CircuitBreaker, CircuitBreakerState

__all__ = [
    "Client",
    "Event",
    "EventCategory",
    "SearchCache",
    "JobRun",
    "User",
    "UserRole",
    "Business",
    "GUID",
    "EventUserInteraction",
    "AuditLog",
    "Tag",
    "ClientTag",
    "EventTag",
    "Notification",
    "APIConfig",
    "UserPreference",
    "EventRawData",
    "AutomationSchedule",
    "EmailLog",
    "APIRequestLog",
    "CircuitBreaker",
    "CircuitBreakerState",
]
