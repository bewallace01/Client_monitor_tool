"""Cache service layer for search result caching and management."""

import hashlib
import json
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models import SearchCache
from app.schemas import SearchCacheCreate


class CacheService:
    """Service for managing search cache entries."""

    @staticmethod
    def generate_query_hash(query_text: str, source: str) -> str:
        """
        Generate a hash for a query to use as cache key.

        Combines query text and source to create unique hash.
        """
        combined = f"{query_text.lower().strip()}:{source}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def get_cached_result(
        db: Session, query_text: str, source: str
    ) -> Optional[SearchCache]:
        """
        Get cached search result if it exists and is not expired.

        Returns None if cache miss or expired.
        """
        query_hash = CacheService.generate_query_hash(query_text, source)

        cache_entry = (
            db.query(SearchCache)
            .filter(SearchCache.query_hash == query_hash)
            .filter(SearchCache.source == source)
            .filter(SearchCache.expires_at > datetime.utcnow())
            .first()
        )

        return cache_entry

    @staticmethod
    def create_cache_entry(
        db: Session,
        query_text: str,
        source: str,
        results: list,
        ttl_hours: int = 24,
    ) -> SearchCache:
        """
        Create a new cache entry for search results.

        Args:
            query_text: The search query
            source: The data source (e.g., 'news_api', 'google')
            results: List of search result dictionaries
            ttl_hours: Time to live in hours (default: 24)
        """
        query_hash = CacheService.generate_query_hash(query_text, source)
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        cache_data = SearchCacheCreate(
            query_hash=query_hash,
            query_text=query_text,
            source=source,
            results_json=json.dumps(results) if results else None,
            result_count=len(results),
            expires_at=expires_at,
        )

        # Check if entry already exists and update it
        existing = (
            db.query(SearchCache)
            .filter(SearchCache.query_hash == query_hash)
            .filter(SearchCache.source == source)
            .first()
        )

        if existing:
            existing.results_json = cache_data.results_json
            existing.result_count = cache_data.result_count
            existing.cached_at = datetime.utcnow()
            existing.expires_at = expires_at
            db.commit()
            db.refresh(existing)
            return existing

        # Create new entry
        db_cache = SearchCache(
            query_hash=query_hash,
            query_text=query_text,
            source=source,
            results_json=cache_data.results_json,
            result_count=cache_data.result_count,
            cached_at=datetime.utcnow(),
            expires_at=expires_at,
        )

        db.add(db_cache)
        db.commit()
        db.refresh(db_cache)
        return db_cache

    @staticmethod
    def get_cache_entries(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        source: Optional[str] = None,
        include_expired: bool = False,
    ) -> Tuple[List[SearchCache], int]:
        """
        Get list of cache entries with optional filtering.

        Returns tuple of (cache_entries, total_count).
        """
        query = db.query(SearchCache)

        # Filter by source
        if source:
            query = query.filter(SearchCache.source == source)

        # Filter expired entries
        if not include_expired:
            query = query.filter(SearchCache.expires_at > datetime.utcnow())

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        cache_entries = (
            query.order_by(SearchCache.cached_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return cache_entries, total

    @staticmethod
    def get_cache_by_id(db: Session, cache_id: int) -> Optional[SearchCache]:
        """Get a single cache entry by ID."""
        return db.query(SearchCache).filter(SearchCache.id == cache_id).first()

    @staticmethod
    def delete_cache_entry(db: Session, cache_id: int) -> bool:
        """
        Delete a cache entry by ID.

        Returns True if deleted, False if not found.
        """
        cache_entry = db.query(SearchCache).filter(SearchCache.id == cache_id).first()
        if not cache_entry:
            return False

        db.delete(cache_entry)
        db.commit()
        return True

    @staticmethod
    def delete_expired_entries(db: Session) -> int:
        """
        Delete all expired cache entries.

        Returns number of entries deleted.
        """
        deleted_count = (
            db.query(SearchCache)
            .filter(SearchCache.expires_at <= datetime.utcnow())
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def clear_cache_by_source(db: Session, source: str) -> int:
        """
        Clear all cache entries for a specific source.

        Returns number of entries deleted.
        """
        deleted_count = (
            db.query(SearchCache)
            .filter(SearchCache.source == source)
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def clear_all_cache(db: Session) -> int:
        """
        Clear all cache entries.

        Returns number of entries deleted.
        """
        deleted_count = db.query(SearchCache).delete()
        db.commit()
        return deleted_count

    @staticmethod
    def get_cache_stats(db: Session) -> dict:
        """
        Get cache statistics and metrics.

        Returns comprehensive cache statistics.
        """
        total_entries = db.query(SearchCache).count()

        # Active vs expired
        now = datetime.utcnow()
        active_entries = (
            db.query(SearchCache)
            .filter(SearchCache.expires_at > now)
            .count()
        )
        expired_entries = total_entries - active_entries

        # Entries by source
        source_stats = (
            db.query(SearchCache.source, func.count(SearchCache.id))
            .group_by(SearchCache.source)
            .all()
        )
        entries_by_source = {source: count for source, count in source_stats}

        # Cache hit rate calculation (would need request tracking for accurate rate)
        # For now, we'll return None as we don't track cache hits/misses yet
        cache_hit_rate = None

        # Total cached results
        total_results = (
            db.query(func.sum(SearchCache.result_count)).scalar() or 0
        )

        # Average results per query
        avg_results = (
            db.query(func.avg(SearchCache.result_count)).scalar() or 0.0
        )

        # Most recent cache time
        most_recent = (
            db.query(func.max(SearchCache.cached_at)).scalar()
        )

        # Oldest cache time
        oldest_active = (
            db.query(func.min(SearchCache.cached_at))
            .filter(SearchCache.expires_at > now)
            .scalar()
        )

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_hit_rate": cache_hit_rate,
            "entries_by_source": entries_by_source,
            "total_cached_results": total_results,
            "avg_results_per_query": round(avg_results, 2),
            "most_recent_cache": most_recent,
            "oldest_active_cache": oldest_active,
        }

    @staticmethod
    def search_cache_entries(
        db: Session,
        query_text: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[SearchCache], int]:
        """
        Search through cache entries by query text.

        Returns tuple of (matching_entries, total_count).
        """
        query = db.query(SearchCache).filter(
            SearchCache.query_text.ilike(f"%{query_text}%")
        )

        total = query.count()

        results = (
            query.order_by(SearchCache.cached_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return results, total
