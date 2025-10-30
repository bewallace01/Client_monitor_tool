"""
Configuration settings for Client Intelligence Monitoring Tool.
Uses Pydantic for validation and environment variable support.
"""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Client Intelligence Monitor"
    environment: Literal["development", "production"] = "development"
    debug: bool = True

    # Database
    database_url: str = f"sqlite:///{PROJECT_ROOT}/data/client_intelligence.db"

    # Data collection
    collector_type: Literal["mock", "real"] = "mock"  # Default to mock for zero-cost development
    search_lookback_days: int = 7  # How many days back to search for news
    cache_ttl_hours: int = 24  # How long to cache search results

    # Event processing
    min_relevance_score: float = 0.3  # Minimum score to show events (0-1)
    event_categories: list[str] = [
        "funding",
        "acquisition",
        "leadership_change",
        "product_launch",
        "partnership",
        "financial_results",
        "regulatory",
        "award",
        "other"
    ]

    # Scheduling
    enable_scheduler: bool = False  # Disable by default for development
    update_interval_hours: int = 24  # How often to check for updates

    # UI
    dashboard_title: str = "Client Intelligence Dashboard"
    items_per_page: int = 20
    default_date_range_days: int = 30

    # API Keys (for real implementations - keep empty for mock)
    newsapi_key: str = ""
    google_news_api_key: str = ""
    openai_api_key: str = ""


    def get_data_dir(self) -> Path:
        """Get the data directory path, creating it if needed."""
        data_dir = PROJECT_ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir


# Global settings instance
settings = Settings()
