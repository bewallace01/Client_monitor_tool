"""Search and Cache API endpoints for managing cached search results."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import json

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.cache_service import CacheService
from app.schemas import (
    SearchCacheResponse,
    SearchCacheStats,
    SearchQuery,
    SearchResponse,
    SearchResult,
    MessageResponse,
)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/query", response_model=SearchResponse)
def perform_search(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Perform a search query with optional caching.

    This endpoint performs a search and caches the results. If the same query
    was made recently and is still cached, returns the cached results.

    - **query**: Search query string (required)
    - **source**: Data source (default: news_api)
    - **use_cache**: Whether to use cached results (default: true)
    - **max_results**: Maximum number of results to return (default: 20)

    Note: This is a placeholder endpoint. In a real implementation,
    this would call external APIs like NewsAPI, Google News, etc.
    """
    # Check cache first if use_cache is True
    cached_result = None
    if search_query.use_cache:
        cached_result = CacheService.get_cached_result(
            db, search_query.query, search_query.source
        )

    if cached_result:
        # Return cached results
        results = []
        if cached_result.results_json:
            try:
                results_data = json.loads(cached_result.results_json)
                results = [SearchResult(**item) for item in results_data]
            except json.JSONDecodeError:
                results = []

        return SearchResponse(
            query=search_query.query,
            total_results=cached_result.result_count,
            cached=True,
            cached_at=cached_result.cached_at,
            results=results[: search_query.max_results],
        )

    # In a real implementation, this would call the actual search API
    # For now, return a placeholder response and cache it
    mock_results = [
        {
            "title": f"Sample result for: {search_query.query}",
            "description": "This is a placeholder search result. In production, this would come from a real API.",
            "url": "https://example.com/article",
            "source": search_query.source,
            "published_at": None,
            "relevance_score": 0.85,
        }
    ]

    # Cache the results
    CacheService.create_cache_entry(
        db=db,
        query_text=search_query.query,
        source=search_query.source,
        results=mock_results,
        ttl_hours=24,
    )

    return SearchResponse(
        query=search_query.query,
        total_results=len(mock_results),
        cached=False,
        cached_at=None,
        results=[SearchResult(**r) for r in mock_results][: search_query.max_results],
    )


@router.get("/cache", response_model=dict)
def list_cache_entries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    source: Optional[str] = Query(None, description="Filter by source"),
    include_expired: bool = Query(
        False, description="Include expired cache entries"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List cached search entries with pagination.

    Returns a paginated list of search cache entries with optional filtering.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (1-100, default: 50)
    - **source**: Filter by search source
    - **include_expired**: Include expired entries (default: false)
    """
    cache_entries, total = CacheService.get_cache_entries(
        db=db,
        skip=skip,
        limit=limit,
        source=source,
        include_expired=include_expired,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages,
        "items": [
            SearchCacheResponse.model_validate(entry) for entry in cache_entries
        ],
    }


@router.get("/cache/stats", response_model=SearchCacheStats)
def get_cache_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get cache statistics and metrics.

    Returns comprehensive cache statistics including:
    - Total entries (active and expired)
    - Entries by source
    - Cache hit rate (if available)
    - Other cache metrics
    """
    stats = CacheService.get_cache_stats(db)
    return SearchCacheStats(**stats)


@router.get("/cache/{cache_id}", response_model=SearchCacheResponse)
def get_cache_entry(
    cache_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a single cache entry by ID.

    - **cache_id**: The ID of the cache entry to retrieve
    """
    cache_entry = CacheService.get_cache_by_id(db, cache_id)
    if not cache_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cache entry with id {cache_id} not found",
        )
    return SearchCacheResponse.model_validate(cache_entry)


@router.get("/cache/search/{query_text}")
def search_cache(
    query_text: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Search through cached entries by query text.

    Finds cache entries that contain the specified query text.

    - **query_text**: Text to search for in cached queries
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (1-100, default: 50)
    """
    results, total = CacheService.search_cache_entries(
        db=db,
        query_text=query_text,
        skip=skip,
        limit=limit,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages,
        "items": [SearchCacheResponse.model_validate(entry) for entry in results],
    }


@router.delete("/cache/{cache_id}", response_model=MessageResponse)
def delete_cache_entry(
    cache_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific cache entry.

    - **cache_id**: The ID of the cache entry to delete
    """
    deleted = CacheService.delete_cache_entry(db, cache_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cache entry with id {cache_id} not found",
        )
    return MessageResponse(message=f"Cache entry {cache_id} deleted successfully")


@router.delete("/cache/expired/cleanup", response_model=MessageResponse)
def cleanup_expired_cache(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete all expired cache entries.

    This endpoint cleans up cache entries that have passed their expiration time.
    Returns the number of entries deleted.
    """
    deleted_count = CacheService.delete_expired_entries(db)
    return MessageResponse(
        message=f"Deleted {deleted_count} expired cache entries"
    )


@router.delete("/cache/source/{source}", response_model=MessageResponse)
def clear_cache_by_source(
    source: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Clear all cache entries for a specific source.

    Deletes all cached searches from the specified source.

    - **source**: The data source to clear cache for (e.g., 'news_api', 'google')
    """
    deleted_count = CacheService.clear_cache_by_source(db, source)
    return MessageResponse(
        message=f"Deleted {deleted_count} cache entries for source '{source}'"
    )


@router.delete("/cache/all", response_model=MessageResponse)
def clear_all_cache(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Clear all cache entries.

    WARNING: This deletes ALL cached search results.
    Use with caution.
    """
    deleted_count = CacheService.clear_all_cache(db)
    return MessageResponse(message=f"Deleted {deleted_count} cache entries (all cache cleared)")
