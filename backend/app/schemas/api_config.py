"""
Pydantic schemas for API Configuration
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Supported API Providers
class APIProvider:
    """Supported API provider constants"""
    NEWSAPI = "newsapi"
    OPENAI = "openai"
    GOOGLE_SEARCH = "google_search"
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    SERPER = "serper"
    ANTHROPIC = "anthropic"

    CHOICES = [
        NEWSAPI,
        OPENAI,
        GOOGLE_SEARCH,
        HUBSPOT,
        SALESFORCE,
        SERPER,
        ANTHROPIC,
    ]

    DISPLAY_NAMES = {
        NEWSAPI: "NewsAPI (News & Articles)",
        OPENAI: "OpenAI GPT",
        GOOGLE_SEARCH: "Google Custom Search",
        HUBSPOT: "HubSpot CRM",
        SALESFORCE: "Salesforce CRM",
        SERPER: "Serper Dev (Google Search API)",
        ANTHROPIC: "Anthropic Claude",
    }


class APIConfigBase(BaseModel):
    """Base schema for API configuration"""
    provider: str = Field(..., description="API provider identifier")
    provider_name: str = Field(..., description="Display name of the provider")
    max_tokens_per_month: Optional[int] = Field(None, description="Maximum tokens/requests per month")
    rate_limit_per_hour: Optional[int] = Field(None, description="Maximum requests per hour")
    cost_per_1k_tokens: Optional[float] = Field(None, description="Cost per 1000 tokens")
    is_active: bool = Field(True, description="Whether this API configuration is active")
    config_data: Optional[str] = Field(None, description="Additional JSON configuration")

    @validator('provider')
    def validate_provider(cls, v):
        if v not in APIProvider.CHOICES:
            raise ValueError(f"Provider must be one of: {', '.join(APIProvider.CHOICES)}")
        return v


class APIConfigCreate(APIConfigBase):
    """Schema for creating a new API configuration"""
    business_id: UUID
    api_key: Optional[str] = Field(None, description="Primary API key (will be encrypted)")
    api_secret: Optional[str] = Field(None, description="Secondary API secret (will be encrypted)")
    access_token: Optional[str] = Field(None, description="OAuth access token (will be encrypted)")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token (will be encrypted)")


class APIConfigUpdate(BaseModel):
    """Schema for updating an existing API configuration"""
    provider_name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    max_tokens_per_month: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    cost_per_1k_tokens: Optional[float] = None
    is_active: Optional[bool] = None
    config_data: Optional[str] = None


class APIConfigResponse(APIConfigBase):
    """Schema for API configuration response (public)"""
    id: UUID
    business_id: UUID

    # Usage statistics
    tokens_used_current_month: int = 0
    requests_this_hour: int = 0
    estimated_monthly_cost: Optional[float] = None

    # Connection status
    last_tested_at: Optional[datetime] = None
    last_test_status: Optional[str] = None
    last_test_message: Optional[str] = None

    # Masked credentials
    api_key_masked: Optional[str] = None
    has_secret: bool = False
    has_access_token: bool = False
    has_refresh_token: bool = False

    # Metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIConfigDetailResponse(APIConfigResponse):
    """Schema for detailed API configuration response (includes sensitive data)"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    config_data: Optional[str] = None

    class Config:
        from_attributes = True


class APIConfigTestRequest(BaseModel):
    """Schema for testing API connection"""
    config_id: UUID


class APIConfigTestResponse(BaseModel):
    """Schema for API connection test result"""
    success: bool
    status: str  # "success", "failed", "timeout"
    message: str
    response_time_ms: Optional[float] = None
    tested_at: datetime


class APIUsageStats(BaseModel):
    """Schema for API usage statistics"""
    config_id: UUID
    provider: str
    tokens_used_current_month: int
    max_tokens_per_month: Optional[int]
    requests_this_hour: int
    rate_limit_per_hour: Optional[int]
    estimated_monthly_cost: Optional[float]
    usage_percentage: Optional[float] = None

    @validator('usage_percentage', always=True)
    def calculate_usage_percentage(cls, v, values):
        """Calculate usage percentage if max tokens is set"""
        if values.get('max_tokens_per_month') and values.get('max_tokens_per_month') > 0:
            used = values.get('tokens_used_current_month', 0)
            max_tokens = values['max_tokens_per_month']
            return round((used / max_tokens) * 100, 2)
        return None


class APIProviderInfo(BaseModel):
    """Schema for available API provider information"""
    provider: str
    display_name: str
    description: str
    requires_secret: bool = False
    requires_oauth: bool = False
    documentation_url: Optional[str] = None


# Available API providers with metadata
AVAILABLE_PROVIDERS = [
    APIProviderInfo(
        provider=APIProvider.NEWSAPI,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.NEWSAPI],
        description="Access to news articles from 80,000+ sources worldwide",
        requires_secret=False,
        requires_oauth=False,
        documentation_url="https://newsapi.org/docs"
    ),
    APIProviderInfo(
        provider=APIProvider.OPENAI,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.OPENAI],
        description="OpenAI's GPT models for natural language processing and generation",
        requires_secret=False,
        requires_oauth=False,
        documentation_url="https://platform.openai.com/docs"
    ),
    APIProviderInfo(
        provider=APIProvider.GOOGLE_SEARCH,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.GOOGLE_SEARCH],
        description="Google Custom Search API for web search results",
        requires_secret=True,  # Requires search engine ID
        requires_oauth=False,
        documentation_url="https://developers.google.com/custom-search"
    ),
    APIProviderInfo(
        provider=APIProvider.HUBSPOT,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.HUBSPOT],
        description="HubSpot CRM integration for customer relationship management",
        requires_secret=False,
        requires_oauth=True,
        documentation_url="https://developers.hubspot.com/docs/api/overview"
    ),
    APIProviderInfo(
        provider=APIProvider.SALESFORCE,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.SALESFORCE],
        description="Salesforce CRM integration for enterprise customer management",
        requires_secret=True,
        requires_oauth=True,
        documentation_url="https://developer.salesforce.com/docs"
    ),
    APIProviderInfo(
        provider=APIProvider.SERPER,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.SERPER],
        description="Serper Dev - Fast and cost-effective Google Search API",
        requires_secret=False,
        requires_oauth=False,
        documentation_url="https://serper.dev/docs"
    ),
    APIProviderInfo(
        provider=APIProvider.ANTHROPIC,
        display_name=APIProvider.DISPLAY_NAMES[APIProvider.ANTHROPIC],
        description="Anthropic's Claude AI for advanced language understanding",
        requires_secret=False,
        requires_oauth=False,
        documentation_url="https://docs.anthropic.com/"
    ),
]
