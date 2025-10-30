"""Google Custom Search API collector with rate limiting and error handling."""

import time
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from dataclasses import dataclass

from src.collectors.base import BaseCollector
from src.models.event_dto import EventDTO
from src.models.client_dto import ClientDTO


@dataclass
class RateLimiter:
    """Simple rate limiter for API calls."""
    max_calls: int
    time_window: int = 86400  # 24 hours in seconds
    calls: List[float] = None

    def __post_init__(self):
        if self.calls is None:
            self.calls = []

    def can_make_call(self) -> bool:
        """Check if we can make another API call."""
        now = time.time()
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        return len(self.calls) < self.max_calls

    def record_call(self):
        """Record an API call."""
        self.calls.append(time.time())

    def get_remaining_calls(self) -> int:
        """Get remaining calls in current time window."""
        now = time.time()
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        return max(0, self.max_calls - len(self.calls))


class GoogleSearchCollector(BaseCollector):
    """
    Collector that uses Google Custom Search API to find client-related events.

    Features:
    - Real Google Custom Search API integration
    - Rate limiting (configurable, default 100/day)
    - Automatic fallback to mock collector on error
    - Graceful error handling
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None,
        rate_limit: int = 100,
        use_mock_fallback: bool = True
    ):
        """
        Initialize Google Search collector.

        Args:
            api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
            rate_limit: Maximum API calls per day
            use_mock_fallback: Whether to fallback to mock collector on error
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.rate_limiter = RateLimiter(max_calls=rate_limit)
        self.use_mock_fallback = use_mock_fallback
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.mock_collector = None

        # Initialize mock collector for fallback
        if use_mock_fallback:
            from src.collectors.mock import MockCollector
            self.mock_collector = MockCollector()

    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.search_engine_id)

    def collect_events(
        self,
        client: ClientDTO,
        lookback_days: int = 30,
        max_results: int = 10
    ) -> List[EventDTO]:
        """
        Collect events for a client using Google Custom Search API.

        Args:
            client: Client to collect events for
            lookback_days: Number of days to look back
            max_results: Maximum number of results to return

        Returns:
            List of EventDTO objects
        """
        # Check if API is configured
        if not self.is_configured():
            print(f"⚠️ Google Search API not configured, using mock collector")
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
            date_restrict = f"d{lookback_days}"  # Google's date format

            # Make API request with retries
            events = self._search_with_retry(
                query=query,
                date_restrict=date_restrict,
                num_results=max_results,
                client=client
            )

            return events

        except Exception as e:
            print(f"❌ Error collecting events from Google Search API: {e}")
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
        # Start with company name
        query_parts = [f'"{client.name}"']

        # Add industry context if available
        if client.industry:
            query_parts.append(client.industry)

        # Add keywords to focus on relevant events
        event_keywords = [
            "news", "announcement", "launch", "funding", "acquisition",
            "partnership", "product", "executive", "revenue", "growth"
        ]
        query_parts.append(f"({' OR '.join(event_keywords)})")

        return " ".join(query_parts)

    def _search_with_retry(
        self,
        query: str,
        date_restrict: str,
        num_results: int,
        client: ClientDTO,
        max_retries: int = 3
    ) -> List[EventDTO]:
        """
        Execute search with retry logic and exponential backoff.

        Args:
            query: Search query
            date_restrict: Date restriction parameter
            num_results: Number of results to fetch
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
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': query,
                    'dateRestrict': date_restrict,
                    'num': min(num_results, 10),  # Google max is 10 per request
                    'sort': 'date'  # Sort by date
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
                events = self._parse_search_results(data, client)

                print(f"✅ Google Search API: Found {len(events)} events for {client.name}")
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

    def _parse_search_results(self, data: dict, client: ClientDTO) -> List[EventDTO]:
        """
        Parse Google Search API response into EventDTO objects.

        Args:
            data: API response data
            client: Client the events belong to

        Returns:
            List of EventDTO objects
        """
        events = []
        items = data.get('items', [])

        for item in items:
            try:
                # Extract event data
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                url = item.get('link', '')

                # Try to extract date from metadata
                published_date = self._extract_date(item)

                # Determine event type from content
                event_type = self._classify_event_type(title, snippet)

                # Calculate relevance score
                relevance_score = self._calculate_relevance(title, snippet, client)

                # Determine sentiment
                sentiment = self._analyze_sentiment(title, snippet)

                # Create event
                event = EventDTO(
                    id=self._generate_event_id(url),
                    client_id=client.id,
                    event_type=event_type,
                    title=title,
                    summary=snippet,
                    source_url=url,
                    source_name=self._extract_source_name(url),
                    published_date=published_date,
                    discovered_date=datetime.utcnow(),
                    relevance_score=relevance_score,
                    sentiment=sentiment,
                    status="new",
                    tags=self._extract_tags(title, snippet)
                )

                events.append(event)

            except Exception as e:
                print(f"⚠️ Error parsing search result: {e}")
                continue

        return events

    def _extract_date(self, item: dict) -> datetime:
        """Extract publication date from search result."""
        # Try various date fields
        date_str = None

        # Check pagemap metadata
        pagemap = item.get('pagemap', {})
        metatags = pagemap.get('metatags', [{}])[0]

        date_fields = [
            'article:published_time',
            'datePublished',
            'publishdate',
            'date'
        ]

        for field in date_fields:
            if field in metatags:
                date_str = metatags[field]
                break

        if date_str:
            try:
                # Try parsing ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass

        # Default to now if no date found
        return datetime.utcnow()

    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. prefix
            domain = domain.replace('www.', '')
            # Capitalize first letter
            return domain.split('.')[0].capitalize()
        except:
            return "Web"

    def _classify_event_type(self, title: str, snippet: str) -> str:
        """Classify event type based on content."""
        text = f"{title} {snippet}".lower()

        if any(word in text for word in ['funding', 'raised', 'investment', 'series', 'round']):
            return 'funding'
        elif any(word in text for word in ['acquire', 'acquisition', 'merger', 'bought']):
            return 'acquisition'
        elif any(word in text for word in ['ceo', 'executive', 'appoint', 'hire', 'leadership']):
            return 'leadership'
        elif any(word in text for word in ['launch', 'release', 'product', 'feature', 'update']):
            return 'product'
        elif any(word in text for word in ['partner', 'collaboration', 'team up']):
            return 'partnership'
        elif any(word in text for word in ['revenue', 'earnings', 'profit', 'financial']):
            return 'financial'
        else:
            return 'news'

    def _calculate_relevance(self, title: str, snippet: str, client: ClientDTO) -> float:
        """Calculate relevance score for event."""
        text = f"{title} {snippet}".lower()
        score = 0.5  # Base score

        # Boost if company name is in title
        if client.name.lower() in title.lower():
            score += 0.2

        # Boost for high-value keywords
        high_value_keywords = ['funding', 'acquisition', 'partnership', 'launch']
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.1

        # Cap at 1.0
        return min(score, 1.0)

    def _analyze_sentiment(self, title: str, snippet: str) -> str:
        """Simple sentiment analysis."""
        text = f"{title} {snippet}".lower()

        positive_words = ['success', 'growth', 'launch', 'win', 'award', 'partner', 'funding']
        negative_words = ['loss', 'decline', 'lawsuit', 'layoff', 'struggle', 'fail']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _extract_tags(self, title: str, snippet: str) -> List[str]:
        """Extract relevant tags from content."""
        text = f"{title} {snippet}".lower()
        tags = []

        tag_keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning'],
            'Cloud': ['cloud', 'aws', 'azure', 'gcp'],
            'Enterprise': ['enterprise', 'b2b'],
            'Mobile': ['mobile', 'ios', 'android'],
            'Security': ['security', 'cybersecurity', 'privacy'],
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
