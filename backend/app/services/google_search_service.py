"""Google Custom Search API integration service.

Provides interface to Google Custom Search API for finding recent news and information
about client companies. Handles rate limiting, error handling, and usage tracking.
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.client import Client

logger = logging.getLogger(__name__)


class GoogleSearchService:
    """Integration with Google Custom Search API."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"
    DEFAULT_NUM_RESULTS = 10
    MAX_RESULTS_PER_REQUEST = 10  # Google API limit
    REQUEST_TIMEOUT = 30

    @staticmethod
    async def search(
        api_key: str,
        search_engine_id: str,
        query: str,
        date_restrict: str = "m1",  # Last month by default
        num_results: int = 10,
        start_index: int = 1,
        sort_by_date: bool = True
    ) -> Dict[str, Any]:
        """
        Perform Google Custom Search query.

        Args:
            api_key: Google API key
            search_engine_id: Custom Search Engine ID (cx parameter)
            query: Search query string
            date_restrict: Date restriction (d[number]=days, w[number]=weeks, m[number]=months, y[number]=years)
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for pagination (1-based)
            sort_by_date: Sort results by date (most recent first)

        Returns:
            Dict containing search results in Google API format

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If parameters are invalid
        """
        if not api_key or not search_engine_id:
            raise ValueError("API key and search engine ID are required")

        if num_results > GoogleSearchService.MAX_RESULTS_PER_REQUEST:
            logger.warning(
                f"Requested {num_results} results but Google API max is {GoogleSearchService.MAX_RESULTS_PER_REQUEST}. "
                f"Using max value."
            )
            num_results = GoogleSearchService.MAX_RESULTS_PER_REQUEST

        # Build query parameters
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": num_results,
            "start": start_index,
        }

        # Add date restriction
        if date_restrict:
            params["dateRestrict"] = date_restrict

        # Add date sorting
        if sort_by_date:
            params["sort"] = "date"

        try:
            async with httpx.AsyncClient(timeout=GoogleSearchService.REQUEST_TIMEOUT) as client:
                logger.info(f"Google Search API request: query='{query}', num={num_results}")
                response = await client.get(GoogleSearchService.BASE_URL, params=params)
                response.raise_for_status()

                data = response.json()
                logger.info(
                    f"Google Search API success: {data.get('searchInformation', {}).get('totalResults', 0)} total results"
                )

                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Google Search API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise Exception("Google Search API rate limit exceeded")
            elif e.response.status_code == 403:
                raise Exception("Google Search API authentication failed - check API key")
            elif e.response.status_code == 400:
                raise Exception(f"Google Search API bad request: {e.response.text}")
            else:
                raise Exception(f"Google Search API error: {e.response.status_code}")

        except httpx.TimeoutException:
            logger.error(f"Google Search API timeout after {GoogleSearchService.REQUEST_TIMEOUT}s")
            raise Exception("Google Search API request timed out")

        except Exception as e:
            logger.error(f"Google Search API unexpected error: {str(e)}")
            raise

    @staticmethod
    async def search_client(
        api_key: str,
        search_engine_id: str,
        client: Client,
        additional_keywords: List[str] = None,
        days_back: int = 30,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for information about a specific client.

        Args:
            api_key: Google API key
            search_engine_id: Custom Search Engine ID
            client: Client model instance
            additional_keywords: Optional additional search keywords
            days_back: How many days back to search
            num_results: Number of results to return

        Returns:
            Dict containing search results
        """
        # Build optimized search query
        query = GoogleSearchService.build_search_query(client, additional_keywords)

        # Determine date restriction
        if days_back <= 7:
            date_restrict = f"d{days_back}"
        elif days_back <= 31:
            date_restrict = f"m1"
        elif days_back <= 365:
            months = days_back // 30
            date_restrict = f"m{months}"
        else:
            years = days_back // 365
            date_restrict = f"y{years}"

        return await GoogleSearchService.search(
            api_key=api_key,
            search_engine_id=search_engine_id,
            query=query,
            date_restrict=date_restrict,
            num_results=num_results,
            sort_by_date=True
        )

    @staticmethod
    def build_search_query(client: Client, additional_keywords: List[str] = None) -> str:
        """
        Build optimized search query for a client.

        Args:
            client: Client model instance
            additional_keywords: Optional additional keywords

        Returns:
            Optimized search query string
        """
        query_parts = []

        # Start with client name (quoted for exact match)
        query_parts.append(f'"{client.name}"')

        # Add domain if available (helps disambiguate common names)
        if client.domain:
            # Extract main domain without subdomain
            domain = client.domain.replace("www.", "").replace("http://", "").replace("https://", "")
            query_parts.append(f'"{domain}"')

        # Add search keywords from client profile if available
        if client.search_keywords:
            try:
                import json
                keywords = json.loads(client.search_keywords) if isinstance(client.search_keywords, str) else client.search_keywords
                if keywords and isinstance(keywords, list):
                    # Add up to 3 keywords to avoid over-constraining
                    for keyword in keywords[:3]:
                        if keyword and keyword.strip():
                            query_parts.append(keyword.strip())
            except (json.JSONDecodeError, TypeError):
                pass

        # Add additional keywords
        if additional_keywords:
            for keyword in additional_keywords:
                if keyword and keyword.strip():
                    query_parts.append(keyword.strip())

        # Combine with OR for broader results, focusing on news/announcements
        query = " ".join(query_parts)

        # Add relevant terms to filter for news-worthy content
        query += ' (news OR announcement OR press OR launch OR funding OR acquisition OR partnership)'

        return query

    @staticmethod
    async def search_multiple_clients(
        api_key: str,
        search_engine_id: str,
        clients: List[Client],
        days_back: int = 30,
        num_results_per_client: int = 10
    ) -> Dict[str, Dict[str, Any]]:
        """
        Search for information about multiple clients.

        Args:
            api_key: Google API key
            search_engine_id: Custom Search Engine ID
            clients: List of Client model instances
            days_back: How many days back to search
            num_results_per_client: Number of results per client

        Returns:
            Dict mapping client IDs to their search results
        """
        results = {}

        for client in clients:
            try:
                logger.info(f"Searching for client: {client.name} (ID: {client.id})")
                client_results = await GoogleSearchService.search_client(
                    api_key=api_key,
                    search_engine_id=search_engine_id,
                    client=client,
                    days_back=days_back,
                    num_results=num_results_per_client
                )
                results[str(client.id)] = {
                    "success": True,
                    "client_name": client.name,
                    "results": client_results
                }

            except Exception as e:
                logger.error(f"Failed to search for client {client.name}: {str(e)}")
                results[str(client.id)] = {
                    "success": False,
                    "client_name": client.name,
                    "error": str(e)
                }

        return results

    @staticmethod
    def extract_results_for_storage(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and normalize search results for database storage.

        Args:
            api_response: Raw Google API response

        Returns:
            List of normalized result dictionaries
        """
        items = api_response.get("items", [])
        normalized_results = []

        for item in items:
            # Extract published date from metadata if available
            published_date = None
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [])
            if metatags:
                for metatag in metatags:
                    # Try different date fields
                    date_fields = [
                        "article:published_time",
                        "og:article:published_time",
                        "date",
                        "publishdate",
                        "dc.date"
                    ]
                    for field in date_fields:
                        if field in metatag:
                            published_date = metatag[field]
                            break
                    if published_date:
                        break

            normalized = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "displayLink": item.get("displayLink", ""),
                "source": item.get("displayLink", "Unknown"),
                "published_date": published_date,
                "image": None,
                "pagemap": pagemap
            }

            # Try to extract image
            if "cse_image" in pagemap and pagemap["cse_image"]:
                normalized["image"] = pagemap["cse_image"][0].get("src")
            elif "cse_thumbnail" in pagemap and pagemap["cse_thumbnail"]:
                normalized["image"] = pagemap["cse_thumbnail"][0].get("src")

            normalized_results.append(normalized)

        return normalized_results

    @staticmethod
    async def test_connection(api_key: str, search_engine_id: str) -> Dict[str, Any]:
        """
        Test Google Search API connection with a simple query.

        Args:
            api_key: Google API key
            search_engine_id: Custom Search Engine ID

        Returns:
            Dict with test results
        """
        try:
            start_time = datetime.utcnow()

            # Simple test query
            result = await GoogleSearchService.search(
                api_key=api_key,
                search_engine_id=search_engine_id,
                query="test",
                num_results=1
            )

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "status": "success",
                "message": "Google Search API connection successful",
                "response_time_ms": round(response_time, 2),
                "total_results": result.get("searchInformation", {}).get("totalResults", "0")
            }

        except Exception as e:
            return {
                "success": False,
                "status": "failed",
                "message": f"Google Search API connection failed: {str(e)}",
                "response_time_ms": None
            }
