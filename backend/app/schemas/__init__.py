"""Pydantic schemas for request/response validation."""

# Base schemas
from .base import (
    TimestampMixin,
    PaginationParams,
    PaginatedResponse,
    MessageResponse,
    HealthResponse,
)

# Client schemas
from .client import (
    ClientBase,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    ClientSummary,
    ClientStats,
)

# Event schemas
from .event import (
    EventCategory,
    EventBase,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventWithClient,
    EventListResponse,
    EventFilters,
    EventStats,
    BulkEventUpdate,
)

# SearchCache schemas
from .search_cache import (
    SearchCacheBase,
    SearchCacheCreate,
    SearchCacheResponse,
    SearchCacheStats,
    SearchQuery,
    SearchResult,
    SearchResponse,
)

# JobRun schemas
from .job_run import (
    JobStatus,
    JobRunBase,
    JobRunCreate,
    JobRunUpdate,
    JobRunResponse,
    JobRunListResponse,
    JobRunFilters,
    JobRunStats,
    JobScheduleInfo,
    TriggerJobRequest,
)

# Analytics schemas
from .analytics import (
    TimeSeriesDataPoint,
    CategoryDistribution,
    SentimentDistribution,
    ClientActivityMetrics,
    TopClientsResponse,
    EventTimelineResponse,
    CategoryAnalytics,
    SentimentAnalytics,
    RelevanceMetrics,
    DashboardSummary,
    TrendData,
    GrowthMetrics,
)

# Auth schemas
from .auth import (
    Token,
    TokenData,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
    PasswordChange,
)

# Business schemas
from .business import (
    BusinessBase,
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessSummary,
    BusinessStats,
    BusinessWithStats,
    BusinessListResponse,
    APIKeyResponse,
)

# Event Interaction schemas
from .event_interaction import (
    EventInteractionBase,
    EventInteractionCreate,
    EventInteractionUpdate,
    EventInteractionResponse,
    BulkInteractionUpdate,
)

# Audit schemas
from .audit import (
    AuditLogResponse,
    AuditLogFilters,
    AuditLogListResponse,
)

# Tag schemas
from .tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
    ClientTagCreate,
    ClientTagResponse,
    EventTagCreate,
    EventTagResponse,
)

# Notification schemas
from .notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationFilters,
    BulkNotificationUpdate,
)

# User Preference schemas
from .user_preference import (
    UserPreferenceBase,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    UserPreferenceDefaults,
)

# Event Raw Data schemas
from .event_raw_data import (
    EventRawDataBase,
    EventRawDataCreate,
    EventRawDataUpdate,
    EventRawDataResponse,
    EventRawDataListResponse,
    EventRawDataStats,
)

# Automation Schedule schemas
from .automation_schedule import (
    AutomationScheduleBase,
    AutomationScheduleCreate,
    AutomationScheduleUpdate,
    AutomationScheduleResponse,
    AutomationScheduleListResponse,
    AutomationScheduleStats,
    ScheduleTypeInfo,
    JobTypeInfo,
)

# Email Log schemas
from .email_log import (
    EmailLogBase,
    EmailLogCreate,
    EmailLogUpdate,
    EmailLogResponse,
    EmailLogListResponse,
    EmailLogStats,
    EmailResendRequest,
)

__all__ = [
    # Base
    "TimestampMixin",
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "HealthResponse",
    # Client
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",
    "ClientSummary",
    "ClientStats",
    # Event
    "EventCategory",
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "EventWithClient",
    "EventListResponse",
    "EventFilters",
    "EventStats",
    "BulkEventUpdate",
    # SearchCache
    "SearchCacheBase",
    "SearchCacheCreate",
    "SearchCacheResponse",
    "SearchCacheStats",
    "SearchQuery",
    "SearchResult",
    "SearchResponse",
    # JobRun
    "JobStatus",
    "JobRunBase",
    "JobRunCreate",
    "JobRunUpdate",
    "JobRunResponse",
    "JobRunListResponse",
    "JobRunFilters",
    "JobRunStats",
    "JobScheduleInfo",
    "TriggerJobRequest",
    # Analytics
    "TimeSeriesDataPoint",
    "CategoryDistribution",
    "SentimentDistribution",
    "ClientActivityMetrics",
    "TopClientsResponse",
    "EventTimelineResponse",
    "CategoryAnalytics",
    "SentimentAnalytics",
    "RelevanceMetrics",
    "DashboardSummary",
    "TrendData",
    "GrowthMetrics",
    # Auth
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    # Business
    "BusinessBase",
    "BusinessCreate",
    "BusinessUpdate",
    "BusinessResponse",
    "BusinessSummary",
    "BusinessStats",
    "BusinessWithStats",
    "BusinessListResponse",
    "APIKeyResponse",
    # Event Interaction
    "EventInteractionBase",
    "EventInteractionCreate",
    "EventInteractionUpdate",
    "EventInteractionResponse",
    "BulkInteractionUpdate",
    # Audit
    "AuditLogResponse",
    "AuditLogFilters",
    "AuditLogListResponse",
    # Tag
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagListResponse",
    "ClientTagCreate",
    "ClientTagResponse",
    "EventTagCreate",
    "EventTagResponse",
    # Notification
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationFilters",
    "BulkNotificationUpdate",
    # User Preference
    "UserPreferenceBase",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    "UserPreferenceDefaults",
    # Event Raw Data
    "EventRawDataBase",
    "EventRawDataCreate",
    "EventRawDataUpdate",
    "EventRawDataResponse",
    "EventRawDataListResponse",
    "EventRawDataStats",
    # Automation Schedule
    "AutomationScheduleBase",
    "AutomationScheduleCreate",
    "AutomationScheduleUpdate",
    "AutomationScheduleResponse",
    "AutomationScheduleListResponse",
    "AutomationScheduleStats",
    "ScheduleTypeInfo",
    "JobTypeInfo",
    # Email Log
    "EmailLogBase",
    "EmailLogCreate",
    "EmailLogUpdate",
    "EmailLogResponse",
    "EmailLogListResponse",
    "EmailLogStats",
    "EmailResendRequest",
]
