# backend/app/services/news_collector.py

"""
News Collector Service

Fetches news articles about clients from NewsAPI and stores them as events in the database.
Handles deduplication (URL + title) and relevance scoring.
"""

import logging
from typing import List
from uuid import UUID
from datetime import datetime
import asyncio

from typing import Any, Protocol

# Lightweight Protocol to avoid hard import requirement during static analysis environments
class Session(Protocol):  # type: ignore
    def add(self, *args: Any, **kwargs: Any) -> None: ...
    def commit(self) -> None: ...
    def query(self, *args: Any, **kwargs: Any) -> Any: ...
from app.models.client import Client
from app.schemas import EventCreate
from app.services.event_service import EventService
from app.services.newsapi_service import NewsAPIService

logger = logging.getLogger(__name__)


class NewsCollector:
    """Service to fetch and store news articles for clients."""

    @staticmethod
    async def fetch_and_store_news(
        db: Session,
        api_key: str,
        clients: List[Client],
        business_id: UUID,
        user_id: int,
        days_back: int = 30,
        min_relevance: float = 0.0
    ) -> int:
        """
        Fetch news articles for a list of clients and store as new events.

        Args:
            db: SQLAlchemy session
            api_key: NewsAPI API key
            clients: List of Client objects
            business_id: UUID of business
            user_id: ID of user performing import
            days_back: Lookback window in days
            min_relevance: Minimum relevance score to store article

        Returns:
            Number of new events added
        """
        new_events_count = 0

        for client in clients:
            try:
                api_response = await NewsAPIService.search_client(
                    api_key=api_key,
                    client=client,
                    days_back=days_back
                )
                articles = NewsAPIService.extract_results_for_storage(api_response)
            except Exception as e:
                logger.error(f"Failed to fetch news for {client.name}: {str(e)}")
                continue

            if not articles:
                logger.info(f"No articles found for {client.name}")
                continue

            # Fetch existing events for deduplication
            existing_events = EventService.get_events_for_client(
                db=db,
                client_id=client.id,
                business_id=business_id,
                limit=1000
            )
            existing_urls = {e.url for e in existing_events}
            existing_titles = {(e.title or "").strip().lower() for e in existing_events}

            for article in articles:
                url = article.get("url")
                title_norm = (article.get("title") or "").strip().lower()

                if url in existing_urls or title_norm in existing_titles:
                    logger.debug(f"Skipping duplicate: {article.get('title')}")
                    continue

                relevance_score = NewsAPIService.calculate_relevance_score(article, client)
                if relevance_score < min_relevance:
                    logger.debug(f"Skipping low relevance ({relevance_score}): {article.get('title')}")
                    continue

                event_create = EventCreate(
                    client_id=client.id,
                    title=article.get("title"),
                    description=article.get("description"),
                    url=url,
                    source=article.get("source"),
                    category="News",
                    relevance_score=relevance_score,
                    sentiment_score=0.0,
                    event_date=datetime.fromisoformat(article["published_at"].replace("Z", "+00:00"))
                        if article.get("published_at") else datetime.utcnow(),
                    content_hash=None
                )

                EventService.create_event(db, event_create, business_id, user_id)
                new_events_count += 1
                logger.info(f"Added new article for {client.name}: {article.get('title')}")

        logger.info(f"Finished fetching news. {new_events_count} new events added.")
        return new_events_count


# Helper to run from CLI or scheduled task
def run_news_collection(db: Session, api_key: str, business_id: UUID, user_id: int, days_back=7, min_relevance=0.5):
    import asyncio
    from app.models.client import Client

    clients = db.query(Client).all()
    return asyncio.run(
        NewsCollector.fetch_and_store_news(
            db=db,
            api_key=api_key,
            clients=clients,
            business_id=business_id,
            user_id=user_id,
            days_back=days_back,
            min_relevance=min_relevance
        )
    )
