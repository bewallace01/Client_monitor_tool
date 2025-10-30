"""Search aggregator service for combining results from multiple APIs.

Aggregates search results from:
- Google Custom Search
- Serper (future)
- NewsAPI (future)
- Mock APIs

Handles deduplication, normalization, and result ranking.
"""

import hashlib
import logging
import time
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.api_config import APIConfig
from app.schemas.api_config import APIProvider
from app.services.google_search_service import GoogleSearchService
from app.services.newsapi_service import NewsAPIService
from app.services.mock_api_service import MockAPIService
from app.services.circuit_breaker_service import CircuitBreakerService
from app.services.api_request_logger import APIRequestLogger
from app.services.api_config_service import encryption_service

logger = logging.getLogger(__name__)


class SearchAggregatorService:
    """Aggregates search results from multiple APIs."""

    @staticmethod
    async def search_all_sources(
        db: Session,
        business_id: UUID,
        client: Client,
        days_back: int = 30,
        max_results_per_source: int = 10,
        force_mock: bool = False,
        job_run_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Search across all configured APIs for a client.

        Args:
            db: Database session
            business_id: Business UUID
            client: Client model instance
            days_back: How many days back to search
            max_results_per_source: Maximum results per API source
            force_mock: Force use of mock data (for testing)

        Returns:
            Dict containing aggregated and deduplicated results
        """
        all_results = []
        sources_used = []
        errors = {}

        if force_mock:
            logger.info(f"Using mock search data for client: {client.name}")
            mock_results = SearchAggregatorService._search_mock(client, max_results_per_source)
            all_results.extend(mock_results)
            sources_used.append("mock")
        else:
            # Get all active search API configs for business
            search_configs = SearchAggregatorService._get_search_configs(db, business_id)

            if not search_configs:
                logger.info(f"No search APIs configured for business {business_id}, using mock data")
                mock_results = SearchAggregatorService._search_mock(client, max_results_per_source)
                all_results.extend(mock_results)
                sources_used.append("mock")
            else:
                # Search each configured source
                for config in search_configs:
                    # Initialize circuit breaker for this API
                    breaker = CircuitBreakerService.get_or_create_breaker(
                        db=db,
                        api_config_id=config.id,
                        business_id=business_id,
                        provider=config.provider
                    )

                    # Check if circuit breaker allows requests
                    can_request, block_reason = CircuitBreakerService.should_allow_request(
                        db=db,
                        api_config_id=config.id
                    )

                    if not can_request:
                        logger.warning(f"Circuit breaker blocked {config.provider}: {block_reason}")
                        errors[config.provider] = block_reason
                        continue

                    try:
                        if config.provider == APIProvider.GOOGLE_SEARCH:
                            results = await SearchAggregatorService._search_google(
                                db, config, client, days_back, max_results_per_source, job_run_id
                            )
                            all_results.extend(results)
                            sources_used.append("google_search")
                            logger.info(f"Google Search: {len(results)} results for {client.name}")

                        elif config.provider == APIProvider.SERPER:
                            # Serper integration (future)
                            logger.info("Serper integration not yet implemented")
                            continue

                        elif config.provider == APIProvider.NEWSAPI:
                            results = await SearchAggregatorService._search_newsapi(
                                db, config, client, days_back, max_results_per_source, job_run_id
                            )
                            all_results.extend(results)
                            sources_used.append("newsapi")
                            logger.info(f"NewsAPI: {len(results)} results for {client.name}")

                    except Exception as e:
                        logger.error(f"Error searching {config.provider} for {client.name}: {str(e)}")
                        errors[config.provider] = str(e)

                # Fallback to mock if all sources failed
                if not all_results:
                    logger.warning(f"All search sources failed for {client.name}, using mock data")
                    mock_results = SearchAggregatorService._search_mock(client, max_results_per_source)
                    all_results.extend(mock_results)
                    sources_used.append("mock_fallback")

        # Deduplicate results
        deduplicated = SearchAggregatorService.deduplicate_results(all_results)

        # Sort by date (most recent first)
        sorted_results = SearchAggregatorService._sort_by_date(deduplicated)

        return {
            "client_id": str(client.id),
            "client_name": client.name,
            "total_results": len(sorted_results),
            "sources_used": sources_used,
            "errors": errors if errors else None,
            "results": sorted_results
        }

    @staticmethod
    async def search_multiple_clients(
        db: Session,
        business_id: UUID,
        clients: List[Client],
        days_back: int = 30,
        max_results_per_source: int = 10,
        force_mock: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Search for multiple clients across all configured sources.

        Args:
            db: Database session
            business_id: Business UUID
            clients: List of Client model instances
            days_back: How many days back to search
            max_results_per_source: Maximum results per API source
            force_mock: Force use of mock data

        Returns:
            Dict mapping client IDs to their search results
        """
        results = {}

        for client in clients:
            try:
                logger.info(f"Searching for client: {client.name}")
                client_results = await SearchAggregatorService.search_all_sources(
                    db=db,
                    business_id=business_id,
                    client=client,
                    days_back=days_back,
                    max_results_per_source=max_results_per_source,
                    force_mock=force_mock
                )
                results[str(client.id)] = client_results

            except Exception as e:
                logger.error(f"Failed to search for client {client.name}: {str(e)}")
                results[str(client.id)] = {
                    "client_id": str(client.id),
                    "client_name": client.name,
                    "error": str(e),
                    "total_results": 0,
                    "results": []
                }

        return results

    @staticmethod
    def _get_search_configs(db: Session, business_id: UUID) -> List[APIConfig]:
        """Get all active search API configurations for a business."""
        search_providers = [
            APIProvider.GOOGLE_SEARCH,
            APIProvider.SERPER,
            APIProvider.NEWSAPI
        ]

        return db.query(APIConfig).filter(
            APIConfig.business_id == business_id,
            APIConfig.provider.in_(search_providers),
            APIConfig.is_active == True
        ).all()

    @staticmethod
    async def _search_google(
        db: Session,
        config: APIConfig,
        client: Client,
        days_back: int,
        max_results: int,
        job_run_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API with circuit breaker and logging."""
        start_time = time.time()
        error_type = None
        status_code = None

        try:
            # Decrypt API credentials
            api_key = encryption_service.decrypt(config.api_key) if config.api_key else None
            search_engine_id = encryption_service.decrypt(config.api_secret) if config.api_secret else None

            # Get search results
            response = await GoogleSearchService.search_client(
                api_key=api_key,
                search_engine_id=search_engine_id,  # Search engine ID stored in api_secret
                client=client,
                days_back=days_back,
                num_results=max_results
            )

            # Extract and normalize results
            normalized = GoogleSearchService.extract_results_for_storage(response)

            # Add source metadata
            for result in normalized:
                result["source_api"] = "google_search"
                result["api_config_id"] = str(config.id)

            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            CircuitBreakerService.record_success(db, config.id)
            APIRequestLogger.log_request(
                db=db,
                business_id=config.business_id,
                api_config_id=config.id,
                provider="google_search",
                success=True,
                status_code=200,
                response_time_ms=response_time_ms,
                results_count=len(normalized),
                client_id=client.id,
                client_name=client.name,
                job_run_id=job_run_id
            )

            return normalized

        except Exception as e:
            # Determine error type
            error_message = str(e)
            if "429" in error_message or "rate limit" in error_message.lower():
                error_type = "rate_limit"
                status_code = 429
            elif "timeout" in error_message.lower():
                error_type = "timeout"
            elif "401" in error_message or "403" in error_message or "auth" in error_message.lower():
                error_type = "auth_error"
                status_code = 401 if "401" in error_message else 403
            else:
                error_type = "api_error"

            # Record failure
            response_time_ms = (time.time() - start_time) * 1000
            CircuitBreakerService.record_failure(db, config.id, error_message, error_type)
            APIRequestLogger.log_request(
                db=db,
                business_id=config.business_id,
                api_config_id=config.id,
                provider="google_search",
                success=False,
                status_code=status_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                error_type=error_type,
                client_id=client.id,
                client_name=client.name,
                job_run_id=job_run_id
            )

            logger.error(f"Google Search error for {client.name}: {error_message}")
            raise

    @staticmethod
    async def _search_newsapi(
        db: Session,
        config: APIConfig,
        client: Client,
        days_back: int,
        max_results: int,
        job_run_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Search using NewsAPI with circuit breaker and logging."""
        start_time = time.time()
        error_type = None
        status_code = None

        try:
            # Decrypt API key
            api_key = encryption_service.decrypt(config.api_key) if config.api_key else None

            # Get search results
            response = await NewsAPIService.search_client(
                api_key=api_key,
                client=client,
                days_back=min(days_back, 30),  # NewsAPI free tier max 30 days
                page_size=max_results
            )

            # Extract and normalize results
            normalized = NewsAPIService.extract_results_for_storage(response)

            # Add source metadata
            for result in normalized:
                result["source_api"] = "newsapi"
                result["api_config_id"] = str(config.id)

            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            CircuitBreakerService.record_success(db, config.id)
            APIRequestLogger.log_request(
                db=db,
                business_id=config.business_id,
                api_config_id=config.id,
                provider="newsapi",
                success=True,
                status_code=200,
                response_time_ms=response_time_ms,
                results_count=len(normalized),
                client_id=client.id,
                client_name=client.name,
                job_run_id=job_run_id
            )

            return normalized

        except Exception as e:
            # Determine error type
            error_message = str(e)
            if "429" in error_message or "rate limit" in error_message.lower():
                error_type = "rate_limit"
                status_code = 429
            elif "timeout" in error_message.lower():
                error_type = "timeout"
            elif "401" in error_message or "403" in error_message or "auth" in error_message.lower() or "api" in error_message.lower():
                error_type = "auth_error"
                status_code = 401 if "401" in error_message else 403
            else:
                error_type = "api_error"

            # Record failure
            response_time_ms = (time.time() - start_time) * 1000
            CircuitBreakerService.record_failure(db, config.id, error_message, error_type)
            APIRequestLogger.log_request(
                db=db,
                business_id=config.business_id,
                api_config_id=config.id,
                provider="newsapi",
                success=False,
                status_code=status_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                error_type=error_type,
                client_id=client.id,
                client_name=client.name,
                job_run_id=job_run_id
            )

            logger.error(f"NewsAPI error for {client.name}: {error_message}")
            raise

    @staticmethod
    def _search_mock(client: Client, max_results: int) -> List[Dict[str, Any]]:
        """Search using mock API."""
        response = MockAPIService.mock_search_results(
            client_name=client.name,
            num_results=max_results
        )

        # Extract results
        items = response.get("items", [])
        results = []

        for item in items:
            # Extract published date
            published_date = None
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [])
            if metatags:
                published_date = metatags[0].get("article:published_time")

            result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "displayLink": item.get("displayLink", ""),
                "source": "Mock API",
                "published_date": published_date,
                "source_api": "mock",
                "api_config_id": None
            }
            results.append(result)

        return results

    @staticmethod
    def deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on content similarity.

        Uses multiple strategies:
        1. Exact URL matching
        2. Title similarity
        3. Content hash matching

        Args:
            results: List of search result dictionaries

        Returns:
            Deduplicated list of results
        """
        if not results:
            return []

        seen_urls: Set[str] = set()
        seen_titles: Set[str] = set()
        seen_hashes: Set[str] = set()
        deduplicated = []

        for result in results:
            # Check URL
            url = result.get("link", "").lower().strip()
            if url and url in seen_urls:
                logger.debug(f"Skipping duplicate URL: {url}")
                continue

            # Check title similarity (normalize)
            title = result.get("title", "").lower().strip()
            title_normalized = SearchAggregatorService._normalize_text(title)
            if title_normalized and title_normalized in seen_titles:
                logger.debug(f"Skipping duplicate title: {title}")
                continue

            # Check content hash
            content = f"{title} {result.get('snippet', '')}".lower()
            content_hash = SearchAggregatorService.calculate_content_hash(content)
            if content_hash in seen_hashes:
                logger.debug(f"Skipping duplicate content: {title[:50]}...")
                continue

            # Add to seen sets
            if url:
                seen_urls.add(url)
            if title_normalized:
                seen_titles.add(title_normalized)
            seen_hashes.add(content_hash)

            # Add content hash to result
            result["content_hash"] = content_hash

            # Add to deduplicated list
            deduplicated.append(result)

        logger.info(f"Deduplicated {len(results)} results to {len(deduplicated)}")
        return deduplicated

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        import re
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def calculate_content_hash(content: str) -> str:
        """Generate SHA256 hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def _sort_by_date(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort results by published date (most recent first)."""
        def get_date_key(result):
            published = result.get("published_date")
            if published:
                try:
                    from datetime import datetime
                    # Handle various date formats
                    if isinstance(published, str):
                        # Try ISO format
                        try:
                            return datetime.fromisoformat(published.replace("Z", "+00:00"))
                        except:
                            pass
                    return datetime.min
                except:
                    return datetime.min
            return datetime.min

        try:
            from datetime import datetime
            sorted_results = sorted(results, key=get_date_key, reverse=True)
            return sorted_results
        except Exception as e:
            logger.warning(f"Error sorting by date: {str(e)}, returning unsorted")
            return results

    @staticmethod
    def rank_results(
        results: List[Dict[str, Any]],
        client: Client,
        crm_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank search results by relevance.

        Considers:
        - Recency
        - Source authority
        - Content relevance
        - Client context

        Args:
            results: List of search results
            client: Client model instance
            crm_data: Optional CRM data for context

        Returns:
            Ranked list of results
        """
        # TODO: Implement sophisticated ranking algorithm
        # For now, date sorting is sufficient
        return SearchAggregatorService._sort_by_date(results)
