"""API Request Log model for tracking API usage and failures."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.business import GUID


class APIRequestLog(Base):
    """Track all API requests for monitoring and rate limiting."""

    __tablename__ = "api_request_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id = Column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    api_config_id = Column(GUID(), ForeignKey("api_configs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Request details
    provider = Column(String(50), nullable=False, index=True)  # google_search, newsapi, etc.
    endpoint = Column(String(500), nullable=True)  # API endpoint called
    method = Column(String(10), nullable=False, default="GET")  # HTTP method

    # Client context (if applicable)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    client_name = Column(String(255), nullable=True)

    # Job context (if part of automation)
    job_run_id = Column(GUID(), ForeignKey("job_runs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Response details
    status_code = Column(Integer, nullable=True)  # HTTP status code
    success = Column(Boolean, nullable=False, default=False, index=True)
    response_time_ms = Column(Float, nullable=True)  # Response time in milliseconds

    # Results
    results_count = Column(Integer, nullable=True, default=0)  # Number of results returned

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True, index=True)  # rate_limit, timeout, auth_error, etc.

    # Rate limiting info
    rate_limit_remaining = Column(Integer, nullable=True)  # Remaining requests in current window
    rate_limit_reset = Column(DateTime, nullable=True)  # When rate limit resets

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    business = relationship("Business", back_populates="api_request_logs")
    api_config = relationship("APIConfig", back_populates="request_logs")
    client = relationship("Client", back_populates="api_request_logs")
    job_run = relationship("JobRun", back_populates="api_request_logs")

    def __repr__(self):
        return f"<APIRequestLog {self.provider} - {self.success} - {self.created_at}>"
