"""NewsAPI service for fetching news articles about clients.

NewsAPI provides access to news articles from thousands of sources.
https://newsapi.org/
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx  # type: ignore

from app.models.client import Client

logger = logging.getLogger(__name__)


class NewsAPIService:
    """Service for NewsAPI integration."""

    BASE_URL = "https://newsapi.org/v2"

    @staticmethod
    def build_search_query(
        client: Client,
        additional_keywords: Optional[List[str]] = None
    ) -> str:
        """
        Build an optimized search query for NewsAPI.

        Args:
            client: Client to search for
            additional_keywords: Additional search terms

        Returns:
            Optimized search query string
        """
        query_parts = []

        # Add client name (required)
        if client.name:
            # Quote the name if it contains spaces
            if " " in client.name:
                query_parts.append(f'"{client.name}"')
            else:
                query_parts.append(client.name)

        # Add domain if available (use OR to broaden search, not AND which is too restrictive)
        if client.domain:
            domain_without_www = client.domain.replace("www.", "").replace("http://", "").replace("https://", "")
            # Only add simple domain name, not full URL
            # Extract just the domain name (e.g., "bankofamerica" from "bankofamerica.com")
            domain_name = domain_without_www.split('.')[0] if '.' in domain_without_www else domain_without_www
            query_parts.append(domain_name)

        # Add additional keywords
        if additional_keywords:
            query_parts.extend(additional_keywords)

        # Use OR to broaden search - NewsAPI free tier works better with broader queries
        query = " OR ".join(query_parts)

        logger.debug(f"Built NewsAPI query for {client.name}: {query}")
        return query

    @staticmethod
    async def search_client(
        api_key: str,
        client: Client,
        days_back: int = 30,
        language: str = "en",
        # sort_by: str = "relevancy",
        sort_by: str = "publishedAt",  # Sort by date to get most recent first        
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Search for news articles about a client.

        Args:
            api_key: NewsAPI API key
            client: Client to search for
            days_back: Number of days to look back (max 30 for free tier)
            language: Language code (e.g., 'en', 'es', 'fr')
            sort_by: Sort by 'relevancy', 'popularity', or 'publishedAt'
            page_size: Number of results (max 100)

        Returns:
            Dict with NewsAPI response format
        """
        try:
            # Build search query
            query = NewsAPIService.build_search_query(client)

            # Calculate from date (NewsAPI requires YYYY-MM-DD)
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            # Build request parameters
            params = {
                "q": query,
                "apiKey": api_key,
                "language": language,
                "sortBy": sort_by,
                "pageSize": min(page_size, 100),  # Max 100 per request
                "from": from_date,
            }

            # Make request
            async with httpx.AsyncClient() as client_http:
                response = await client_http.get(
                    f"{NewsAPIService.BASE_URL}/everything",
                    params=params,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                logger.info(
                    f"NewsAPI search for {client.name}: "
                    f"status={data.get('status')}, "
                    f"totalResults={data.get('totalResults', 0)}"
                )

                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"NewsAPI HTTP error for {client.name}: {e.response.status_code} - {e.response.text}")
            raise Exception(f"NewsAPI error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"NewsAPI request error for {client.name}: {str(e)}")
            raise Exception(f"NewsAPI request failed: {str(e)}")
        except Exception as e:
            logger.error(f"NewsAPI unexpected error for {client.name}: {str(e)}")
            raise

    @staticmethod
    async def get_top_headlines(
        api_key: str,
        query: Optional[str] = None,
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get top headlines from NewsAPI.

        Args:
            api_key: NewsAPI API key
            query: Search query (optional)
            country: Country code (e.g., 'us', 'gb', 'ca')
            category: Category (business, entertainment, general, health, science, sports, technology)
            page_size: Number of results (max 100)

        Returns:
            Dict with NewsAPI response format
        """
        try:
            params = {
                "apiKey": api_key,
                "pageSize": min(page_size, 100),
            }

            if query:
                params["q"] = query

            if country:
                params["country"] = country

            if category:
                params["category"] = category

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{NewsAPIService.BASE_URL}/top-headlines",
                    params=params,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                logger.info(f"NewsAPI top headlines: totalResults={data.get('totalResults', 0)}")
                return data

        except Exception as e:
            logger.error(f"NewsAPI top headlines error: {str(e)}")
            raise

    @staticmethod
    def extract_results_for_storage(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and normalize results from NewsAPI response for storage.

        Args:
            api_response: Raw NewsAPI response

        Returns:
            List of normalized article dicts
        """
        if api_response.get("status") != "ok":
            logger.warning(f"NewsAPI returned non-ok status: {api_response.get('status')}")
            return []

        articles = api_response.get("articles", [])

        normalized_results = []
        for article in articles:
            try:
                # Normalize the article format
                normalized = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author"),
                    "published_at": article.get("publishedAt"),
                    "url_to_image": article.get("urlToImage"),
                    "api_source": "newsapi"
                }

                normalized_results.append(normalized)

            except Exception as e:
                logger.warning(f"Error normalizing NewsAPI article: {str(e)}")
                continue

        logger.debug(f"Normalized {len(normalized_results)} NewsAPI articles")
        return normalized_results

    @staticmethod
    def calculate_relevance_score(
        article: Dict[str, Any],
        client: Client
    ) -> float:
        """
        Calculate relevance score for an article.

        Args:
            article: Normalized article dict
            client: Client being searched

        Returns:
            Relevance score (0.0-1.0)
        """
        score = 0.0
        client_name_lower = client.name.lower() if client.name else ""

        # Check title (high weight)
        title = article.get("title", "").lower()
        if client_name_lower in title:
            score += 0.5

        # Check description (medium weight)
        description = article.get("description", "").lower()
        if client_name_lower in description:
            score += 0.3

        # Check content (lower weight)
        content = article.get("content", "").lower()
        if client_name_lower in content:
            score += 0.2

        # Recency bonus (articles from last 7 days get boost)
        published_at = article.get("published_at")
        if published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                days_ago = (datetime.utcnow().replace(tzinfo=pub_date.tzinfo) - pub_date).days
                if days_ago <= 7:
                    score += 0.1
            except:
                pass

        return min(score, 1.0)