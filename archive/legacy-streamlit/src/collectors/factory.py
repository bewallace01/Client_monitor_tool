"""Collector factory - creates appropriate collector based on configuration."""

import os
import logging
from typing import Optional
from .base import BaseCollector
from .mock_collector import MockCollector
from .google_search import GoogleSearchCollector
from .news_api import NewsAPICollector

logger = logging.getLogger(__name__)


def _get_settings_from_streamlit():
    """
    Try to get settings from Streamlit session state.

    Returns:
        Dictionary of settings or empty dict if not available
    """
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'settings' in st.session_state:
            return st.session_state.settings
    except:
        pass
    return {}


def _validate_google_credentials(api_key: str, search_engine_id: str) -> bool:
    """
    Validate Google Custom Search credentials.

    Args:
        api_key: Google API key
        search_engine_id: Google Search Engine ID

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not search_engine_id:
        return False
    if len(api_key) < 20:  # Basic validation
        logger.warning("Google API key appears invalid (too short)")
        return False
    if len(search_engine_id) < 10:  # Basic validation
        logger.warning("Google Search Engine ID appears invalid (too short)")
        return False
    return True


def _validate_newsapi_credentials(api_key: str) -> bool:
    """
    Validate NewsAPI credentials.

    Args:
        api_key: NewsAPI API key

    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    if len(api_key) < 20:  # Basic validation
        logger.warning("NewsAPI key appears invalid (too short)")
        return False
    return True


def get_collector(collector_type: Optional[str] = None) -> BaseCollector:
    """
    Get the appropriate collector based on environment configuration and settings.

    Priority order:
    1. Explicit collector_type parameter
    2. Streamlit session settings (use_mock_apis flag)
    3. Environment variables (APP_MODE, COLLECTOR_TYPE)
    4. Default to mock

    Args:
        collector_type: Override collector type (mock, newsapi, google, auto)
                       If None, reads from settings or environment

    Returns:
        BaseCollector instance (always succeeds, falls back to mock)
    """
    # Get settings from Streamlit if available
    settings = _get_settings_from_streamlit()

    # Determine if we should use mock APIs
    use_mock = True

    if collector_type is None:
        # Check Streamlit settings first
        if 'use_mock_apis' in settings:
            use_mock = settings['use_mock_apis']
            logger.info(f"Using mock APIs from settings: {use_mock}")
        else:
            # Fall back to environment variables
            app_mode = os.getenv("APP_MODE", "").lower()
            use_mock = app_mode in ["", "mock", "development"]
            logger.info(f"Using mock APIs from environment: {use_mock}")
    else:
        # Explicit collector type provided
        use_mock = collector_type.lower() == "mock"

    # If mock is requested, return it immediately
    if use_mock:
        logger.info("✅ Using MockCollector (zero-cost, simulated data)")
        return MockCollector()

    # Try to use real collectors
    logger.info("🔌 Attempting to use real API collectors...")

    # Get API credentials from settings or environment
    google_api_key = settings.get('google_api_key') or os.getenv('GOOGLE_API_KEY', '')
    google_search_engine_id = settings.get('google_search_engine_id') or os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
    google_rate_limit = settings.get('google_rate_limit', 100)

    newsapi_key = settings.get('newsapi_key') or os.getenv('NEWSAPI_KEY', '')
    newsapi_rate_limit = settings.get('newsapi_rate_limit', 100)

    # Determine which collector to use based on what's configured
    if collector_type and collector_type.lower() == "google":
        # Explicitly requested Google
        if _validate_google_credentials(google_api_key, google_search_engine_id):
            logger.info(f"✅ Using GoogleSearchCollector (rate limit: {google_rate_limit}/day)")
            return GoogleSearchCollector(
                api_key=google_api_key,
                search_engine_id=google_search_engine_id,
                rate_limit=google_rate_limit,
                use_mock_fallback=True
            )
        else:
            logger.warning("⚠️ Google API credentials invalid, falling back to MockCollector")
            return MockCollector()

    elif collector_type and collector_type.lower() == "newsapi":
        # Explicitly requested NewsAPI
        if _validate_newsapi_credentials(newsapi_key):
            logger.info(f"✅ Using NewsAPICollector (rate limit: {newsapi_rate_limit}/day)")
            return NewsAPICollector(
                api_key=newsapi_key,
                rate_limit=newsapi_rate_limit,
                use_mock_fallback=True
            )
        else:
            logger.warning("⚠️ NewsAPI credentials invalid, falling back to MockCollector")
            return MockCollector()

    else:
        # Auto-select: Try Google first, then NewsAPI, then mock
        if _validate_google_credentials(google_api_key, google_search_engine_id):
            logger.info(f"✅ Auto-selected GoogleSearchCollector (rate limit: {google_rate_limit}/day)")
            return GoogleSearchCollector(
                api_key=google_api_key,
                search_engine_id=google_search_engine_id,
                rate_limit=google_rate_limit,
                use_mock_fallback=True
            )
        elif _validate_newsapi_credentials(newsapi_key):
            logger.info(f"✅ Auto-selected NewsAPICollector (rate limit: {newsapi_rate_limit}/day)")
            return NewsAPICollector(
                api_key=newsapi_key,
                rate_limit=newsapi_rate_limit,
                use_mock_fallback=True
            )
        else:
            logger.warning("⚠️ No real API credentials configured, using MockCollector")
            return MockCollector()


def list_available_collectors() -> dict:
    """
    List all available collectors and their status.

    Checks actual configuration to determine availability.

    Returns:
        Dictionary mapping collector names to their status
    """
    settings = _get_settings_from_streamlit()

    # Check Google credentials
    google_api_key = settings.get('google_api_key') or os.getenv('GOOGLE_API_KEY', '')
    google_search_engine_id = settings.get('google_search_engine_id') or os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
    google_available = _validate_google_credentials(google_api_key, google_search_engine_id)

    # Check NewsAPI credentials
    newsapi_key = settings.get('newsapi_key') or os.getenv('NEWSAPI_KEY', '')
    newsapi_available = _validate_newsapi_credentials(newsapi_key)

    return {
        "mock": {
            "available": True,
            "description": "Mock collector with simulated data (zero-cost, no API required)",
            "requires_api_key": False,
            "configured": True,
        },
        "google": {
            "available": True,
            "description": "Google Custom Search API collector (requires API key and Search Engine ID)",
            "requires_api_key": True,
            "configured": google_available,
            "rate_limit": settings.get('google_rate_limit', 100),
        },
        "newsapi": {
            "available": True,
            "description": "NewsAPI.org collector (requires API key from newsapi.org)",
            "requires_api_key": True,
            "configured": newsapi_available,
            "rate_limit": settings.get('newsapi_rate_limit', 100),
        },
    }


def get_active_collector_info() -> dict:
    """
    Get information about the currently active collector.

    Returns:
        Dictionary with collector info
    """
    collector = get_collector()
    collector_type = type(collector).__name__

    info = {
        "type": collector_type,
        "is_mock": isinstance(collector, MockCollector),
        "is_configured": False,
        "rate_limit": None,
    }

    # Get additional info for real collectors
    if isinstance(collector, (GoogleSearchCollector, NewsAPICollector)):
        info["is_configured"] = collector.is_configured()
        if hasattr(collector, 'get_rate_limit_status'):
            info["rate_limit"] = collector.get_rate_limit_status()

    return info
