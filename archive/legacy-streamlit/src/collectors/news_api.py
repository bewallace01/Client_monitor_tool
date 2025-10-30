"""NewsAPI collector with rate limiting and error handling."""

import time
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from dataclasses import dataclass

from src.collectors.base import BaseCollector
from src.models.event_dto import EventDTO
from src.models.client_dto import ClientDTO
from src.collectors.google_search import RateLimiter


class NewsAPICollector(BaseCollector):
    """
    Collector that uses NewsAPI to find client-related news events.

    Features:
    - Real NewsAPI integration (newsapi.org)
    - Rate limiting (configurable, default 100/day for free tier)
    - Automatic fallback to mock collector on error
    - Graceful error handling
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit: int = 100,
        use_mock_fallback: bool = True
    ):
        """
        Initialize NewsAPI collector.

        Args:
            api_key: NewsAPI API key (get from newsapi.org)
            rate_limit: Maximum API calls per day
            use_mock_fallback: Whether to fallback to mock collector on error
        """
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_calls=rate_limit)
        self.use_mock_fallback = use_mock_fallback
        self.base_url = "https://newsapi.org/v2/everything"
        self.mock_collector = None

        # Initialize mock collector for fallback
        if use_mock_fallback:
            from src.collectors.mock import MockCollector
            self.mock_collector = MockCollector()

    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key)

    def collect_events(
        self,
        client: ClientDTO,
        lookback_days: int = 30,
        max_results: int = 10
    ) -> List[EventDTO]:
        """
        Collect events for a client using NewsAPI.

        Args:
            client: Client to collect events for
            lookback_days: Number of days to look back
            max_results: Maximum number of results to return

        Returns:
            List of EventDTO objects
        """
        # Check if API is configured
        if not self.is_configured():
            print(f"⚠️ NewsAPI not configured, using mock collector")
            if self.mock_collector:
                return self.mock_collector.collect_events(client, lookback_days, max_results)
            return []

        # Check rate limit
        if not self.rate_limiter.can_make_call():
            remaining = self.rate_limiter.get_remaining_calls()
            print(f"⚠️ Rate limit exceeded (0/{self.rate_limiter.max_calls} remaining), using mock collector")
            if self.mock_collector:
                return self.mock_collector.collect_events(client, lookback_days, max_results)
            return []

        try:
            # Build search query
            query = self._build_search_query(client)

            # Calculate date range
            from_date = (datetime.utcnow() - timedelta(days=lookback_days)).date()
            to_date = datetime.utcnow().date()

            # Make API request with retries
            events = self._search_with_retry(
                query=query,
                from_date=from_date,
                to_date=to_date,
                page_size=min(max_results, 100),  # NewsAPI max is 100
                client=client
            )

            return events

        except Exception as e:
            print(f"❌ Error collecting events from NewsAPI: {e}")
            if self.use_mock_fallback and self.mock_collector:
                print(f"🔄 Falling back to mock collector")
                return self.mock_collector.collect_events(client, lookback_days, max_results)
            return []

    def _build_search_query(self, client: ClientDTO) -> str:
        """
        Build optimized search query for client.

        Args:
            client: Client to build query for

        Returns:
            Search query string
        """
        # NewsAPI supports complex queries with AND/OR/NOT operators
        query_parts = [f'"{client.name}"']

        # Add industry context if available
        if client.industry:
            # Use OR to include industry news
            query_parts.append(f'OR {client.industry}')

        # Focus on business news
        query = " ".join(query_parts)

        return query

    def _search_with_retry(
        self,
        query: str,
        from_date: datetime.date,
        to_date: datetime.date,
        page_size: int,
        client: ClientDTO,
        max_retries: int = 3
    ) -> List[EventDTO]:
        """
        Execute search with retry logic and exponential backoff.

        Args:
            query: Search query
            from_date: Start date for search
            to_date: End date for search
            page_size: Number of results per page
            client: Client being searched
            max_retries: Maximum retry attempts

        Returns:
            List of EventDTO objects
        """
        events = []
        retry_delay = 1  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                # Build request parameters
                params = {
                    'apiKey': self.api_key,
                    'q': query,
                    'from': from_date.isoformat(),
                    'to': to_date.isoformat(),
                    'pageSize': page_size,
                    'sortBy': 'publishedAt',  # Sort by date
                    'language': 'en'
                }

                # Record the API call for rate limiting
                self.rate_limiter.record_call()

                # Make request
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=10
                )

                # Check for rate limit errors
                if response.status_code == 429:
                    print(f"⚠️ Rate limit hit, attempt {attempt + 1}/{max_retries}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                # Parse response
                data = response.json()

                if data.get('status') != 'ok':
                    error_msg = data.get('message', 'Unknown error')
                    raise Exception(f"NewsAPI error: {error_msg}")

                events = self._parse_news_results(data, client)

                print(f"✅ NewsAPI: Found {len(events)} events for {client.name}")
                return events

            except requests.exceptions.Timeout:
                print(f"⏱️ Request timeout, attempt {attempt + 1}/{max_retries}")
                time.sleep(retry_delay)
                retry_delay *= 2

            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                raise

        return events

    def _parse_news_results(self, data: dict, client: ClientDTO) -> List[EventDTO]:
        """
        Parse NewsAPI response into EventDTO objects.

        Args:
            data: API response data
            client: Client the events belong to

        Returns:
            List of EventDTO objects
        """
        events = []
        articles = data.get('articles', [])

        for article in articles:
            try:
                # Extract article data
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                url = article.get('url', '')
                source = article.get('source', {}).get('name', 'Unknown')
                published_at = article.get('publishedAt', '')
                author = article.get('author', '')
                url_to_image = article.get('urlToImage', '')

                # Skip if title is missing
                if not title:
                    continue

                # Parse publication date
                try:
                    published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_date = datetime.utcnow()

                # Use description or content for summary
                summary = description or content or ""
                if len(summary) > 500:
                    summary = summary[:497] + "..."

                # Determine event type from content
                event_type = self._classify_event_type(title, summary)

                # Calculate relevance score
                relevance_score = self._calculate_relevance(title, summary, client)

                # Determine sentiment
                sentiment = self._analyze_sentiment(title, summary)

                # Build metadata
                metadata = {}
                if author:
                    metadata['author'] = author
                if url_to_image:
                    metadata['image_url'] = url_to_image

                # Create event
                event = EventDTO(
                    id=self._generate_event_id(url),
                    client_id=client.id,
                    event_type=event_type,
                    title=title,
                    summary=summary,
                    source_url=url,
                    source_name=source,
                    published_date=published_date,
                    discovered_date=datetime.utcnow(),
                    relevance_score=relevance_score,
                    sentiment=sentiment,
                    status="new",
                    tags=self._extract_tags(title, summary),
                    metadata=metadata
                )

                events.append(event)

            except Exception as e:
                print(f"⚠️ Error parsing article: {e}")
                continue

        return events

    def _classify_event_type(self, title: str, summary: str) -> str:
        """Classify event type based on content."""
        text = f"{title} {summary}".lower()

        if any(word in text for word in ['funding', 'raised', 'investment', 'series', 'round', 'capital']):
            return 'funding'
        elif any(word in text for word in ['acquire', 'acquisition', 'merger', 'bought', 'takeover']):
            return 'acquisition'
        elif any(word in text for word in ['ceo', 'cfo', 'cto', 'executive', 'appoint', 'hire', 'leadership', 'chief']):
            return 'leadership'
        elif any(word in text for word in ['launch', 'release', 'product', 'feature', 'update', 'unveil']):
            return 'product'
        elif any(word in text for word in ['partner', 'partnership', 'collaboration', 'alliance', 'team up']):
            return 'partnership'
        elif any(word in text for word in ['revenue', 'earnings', 'profit', 'financial', 'quarter', 'ipo']):
            return 'financial'
        elif any(word in text for word in ['award', 'recognition', 'honor', 'prize', 'win']):
            return 'award'
        elif any(word in text for word in ['regulation', 'compliance', 'legal', 'lawsuit', 'court']):
            return 'regulatory'
        else:
            return 'news'

    def _calculate_relevance(self, title: str, summary: str, client: ClientDTO) -> float:
        """Calculate relevance score for event."""
        text = f"{title} {summary}".lower()
        client_name_lower = client.name.lower()
        score = 0.3  # Base score

        # Boost if company name appears multiple times
        name_count = text.count(client_name_lower)
        if name_count > 0:
            score += min(0.3 * name_count, 0.6)  # Cap boost at 0.6

        # Boost if company name is in title
        if client_name_lower in title.lower():
            score += 0.2

        # Boost for high-value keywords
        high_value_keywords = [
            'funding', 'acquisition', 'partnership', 'launch', 'ipo',
            'expansion', 'growth', 'milestone', 'breakthrough'
        ]
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.05

        # Reduce score if it seems like generic industry news
        if client_name_lower not in text:
            score *= 0.5

        # Cap at 1.0
        return min(score, 1.0)

    def _analyze_sentiment(self, title: str, summary: str) -> str:
        """Simple sentiment analysis."""
        text = f"{title} {summary}".lower()

        positive_words = [
            'success', 'growth', 'launch', 'win', 'award', 'partner',
            'funding', 'breakthrough', 'expansion', 'milestone', 'achieve',
            'innovative', 'leading', 'profit', 'gain', 'increase'
        ]
        negative_words = [
            'loss', 'decline', 'lawsuit', 'layoff', 'struggle', 'fail',
            'crash', 'scandal', 'fraud', 'breach', 'hack', 'downgrade',
            'cut', 'decrease', 'drop', 'fall'
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count + 1:
            return 'positive'
        elif negative_count > positive_count + 1:
            return 'negative'
        else:
            return 'neutral'

    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """Extract relevant tags from content."""
        text = f"{title} {summary}".lower()
        tags = []

        tag_keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning', 'deep learning'],
            'Cloud': ['cloud', 'aws', 'azure', 'gcp', 'saas'],
            'Enterprise': ['enterprise', 'b2b', 'business'],
            'Mobile': ['mobile', 'ios', 'android', 'app'],
            'Security': ['security', 'cybersecurity', 'privacy', 'encryption'],
            'Finance': ['finance', 'fintech', 'payment', 'banking'],
            'Healthcare': ['health', 'healthcare', 'medical', 'biotech'],
            'E-commerce': ['ecommerce', 'e-commerce', 'retail', 'shopping'],
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags[:5]  # Limit to 5 tags

    def _generate_event_id(self, url: str) -> str:
        """Generate unique event ID from URL."""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status."""
        return {
            'max_calls': self.rate_limiter.max_calls,
            'remaining_calls': self.rate_limiter.get_remaining_calls(),
            'calls_made': len(self.rate_limiter.calls)
        }

    def get_top_headlines(
        self,
        category: Optional[str] = 'business',
        country: str = 'us',
        page_size: int = 20
    ) -> List[dict]:
        """
        Get top headlines (useful for general market news).

        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            page_size: Number of results

        Returns:
            List of article dictionaries
        """
        if not self.is_configured():
            return []

        if not self.rate_limiter.can_make_call():
            return []

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.api_key,
                'category': category,
                'country': country,
                'pageSize': page_size
            }

            self.rate_limiter.record_call()
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') == 'ok':
                return data.get('articles', [])

        except Exception as e:
            print(f"❌ Error fetching top headlines: {e}")

        return []
