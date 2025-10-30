"""Repository classes for data access."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import Session
from src.models import Client, Event, EventCategory, SearchCache


class ClientRepository:
    """Repository for Client data access."""

    @staticmethod
    def create(session: Session, **kwargs) -> Client:
        """Create a new client."""
        client = Client(**kwargs)
        session.add(client)
        session.flush()
        return client

    @staticmethod
    def get_by_id(session: Session, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        return session.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def get_by_name(session: Session, name: str) -> Optional[Client]:
        """Get client by name."""
        return session.query(Client).filter(Client.name == name).first()

    @staticmethod
    def get_all(session: Session, active_only: bool = True) -> List[Client]:
        """Get all clients."""
        query = session.query(Client)
        if active_only:
            query = query.filter(Client.is_active == True)
        return query.order_by(Client.name).all()

    @staticmethod
    def update(session: Session, client_id: int, **kwargs) -> Optional[Client]:
        """Update a client."""
        client = ClientRepository.get_by_id(session, client_id)
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            client.updated_at = datetime.utcnow()
            session.flush()
        return client

    @staticmethod
    def delete(session: Session, client_id: int) -> bool:
        """Delete a client."""
        client = ClientRepository.get_by_id(session, client_id)
        if client:
            session.delete(client)
            session.flush()
            return True
        return False

    @staticmethod
    def mark_as_checked(session: Session, client_id: int) -> Optional[Client]:
        """Update last_checked_at timestamp."""
        return ClientRepository.update(
            session,
            client_id,
            last_checked_at=datetime.utcnow()
        )


class EventRepository:
    """Repository for Event data access."""

    @staticmethod
    def create(session: Session, **kwargs) -> Event:
        """Create a new event."""
        event = Event(**kwargs)
        session.add(event)
        session.flush()
        return event

    @staticmethod
    def get_by_id(session: Session, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return session.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_by_client(
        session: Session,
        client_id: int,
        limit: int = 100,
        min_relevance: float = 0.0,
        categories: List[str] = None,
    ) -> List[Event]:
        """Get events for a specific client."""
        query = session.query(Event).filter(Event.client_id == client_id)

        if min_relevance > 0:
            query = query.filter(Event.relevance_score >= min_relevance)

        if categories:
            query = query.filter(Event.category.in_(categories))

        return query.order_by(desc(Event.event_date)).limit(limit).all()

    @staticmethod
    def get_recent(
        session: Session,
        days: int = 7,
        min_relevance: float = 0.0,
        limit: int = 100,
    ) -> List[Event]:
        """Get recent events across all clients."""
        since_date = datetime.utcnow() - timedelta(days=days)
        query = session.query(Event).filter(
            and_(
                Event.event_date >= since_date,
                Event.relevance_score >= min_relevance
            )
        )
        return query.order_by(desc(Event.event_date)).limit(limit).all()

    @staticmethod
    def get_by_hash(session: Session, content_hash: str) -> Optional[Event]:
        """Get event by content hash (for deduplication)."""
        return session.query(Event).filter(Event.content_hash == content_hash).first()

    @staticmethod
    def get_unread_count(session: Session, client_id: int = None) -> int:
        """Get count of unread events."""
        query = session.query(Event).filter(Event.is_read == False)
        if client_id:
            query = query.filter(Event.client_id == client_id)
        return query.count()

    @staticmethod
    def mark_as_read(session: Session, event_id: int) -> Optional[Event]:
        """Mark event as read."""
        event = EventRepository.get_by_id(session, event_id)
        if event:
            event.is_read = True
            session.commit()
        return event

    @staticmethod
    def toggle_star(session: Session, event_id: int) -> Optional[Event]:
        """Toggle star status on event."""
        event = EventRepository.get_by_id(session, event_id)
        if event:
            event.is_starred = not event.is_starred
            session.commit()
        return event

    @staticmethod
    def update_notes(session: Session, event_id: int, notes: str) -> Optional[Event]:
        """Update event notes."""
        event = EventRepository.get_by_id(session, event_id)
        if event:
            event.user_notes = notes
            session.commit()
        return event


class SearchCacheRepository:
    """Repository for SearchCache data access."""

    @staticmethod
    def create(session: Session, **kwargs) -> SearchCache:
        """Create a new cache entry."""
        cache = SearchCache(**kwargs)
        session.add(cache)
        session.flush()
        return cache

    @staticmethod
    def get_by_hash(session: Session, query_hash: str) -> Optional[SearchCache]:
        """Get cache entry by query hash."""
        return session.query(SearchCache).filter(
            SearchCache.query_hash == query_hash
        ).first()

    @staticmethod
    def get_valid_cache(session: Session, query_hash: str) -> Optional[SearchCache]:
        """Get cache entry if it exists and is not expired."""
        cache = SearchCacheRepository.get_by_hash(session, query_hash)
        if cache and not cache.is_expired():
            return cache
        return None

    @staticmethod
    def cleanup_expired(session: Session) -> int:
        """Delete expired cache entries. Returns count of deleted entries."""
        now = datetime.utcnow()
        result = session.query(SearchCache).filter(
            SearchCache.expires_at < now
        ).delete()
        session.flush()
        return result

    @staticmethod
    def get_stats(session: Session) -> dict:
        """Get cache statistics."""
        total = session.query(SearchCache).count()
        expired = session.query(SearchCache).filter(
            SearchCache.expires_at < datetime.utcnow()
        ).count()
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
        }
