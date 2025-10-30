"""SearchCache Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class SearchCacheBase(BaseModel):
    """Base SearchCache schema with common fields."""
    query_text: str = Field(..., min_length=1, max_length=500, description="Search query")
    source: str = Field(..., max_length=50, description="Search source (e.g., news_api, google)")


class SearchCacheCreate(SearchCacheBase):
    """Schema for creating a new search cache entry."""
    query_hash: str = Field(..., min_length=1, max_length=64, description="Hash of the query")
    results_json: Optional[str] = Field(None, description="JSON string of search results")
    result_count: int = Field(default=0, ge=0, description="Number of results")
    expires_at: datetime = Field(..., description="When this cache entry expires")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query_hash": "a1b2c3d4e5f6...",
                "query_text": "Acme Corporation funding news",
                "results_json": "[{\"title\": \"...\", \"url\": \"...\"}]",
                "result_count": 15,
                "source": "news_api",
                "expires_at": "2025-10-17T10:30:00Z"
            }
        }
    )


class SearchCacheResponse(SearchCacheBase):
    """Schema for search cache response."""
    id: int
    query_hash: str
    results_json: Optional[str] = None
    result_count: int
    cached_at: datetime
    expires_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "query_hash": "a1b2c3d4e5f6...",
                "query_text": "Acme Corporation funding news",
                "results_json": "[{\"title\": \"...\", \"url\": \"...\"}]",
                "result_count": 15,
                "cached_at": "2025-10-16T10:30:00Z",
                "expires_at": "2025-10-17T10:30:00Z",
                "source": "news_api"
            }
        }
    )


class SearchCacheStats(BaseModel):
    """Search cache statistics."""
    total_entries: int
    active_entries: int  # Not expired
    expired_entries: int
    cache_hit_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    entries_by_source: dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    """Schema for search requests."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    source: Optional[str] = Field(default="news_api", max_length=50, description="Search source")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum number of results")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Acme Corporation product launch",
                "source": "news_api",
                "use_cache": True,
                "max_results": 20
            }
        }
    )


class SearchResult(BaseModel):
    """Individual search result item."""
    title: str
    description: Optional[str] = None
    url: str
    source: str
    published_at: Optional[datetime] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Response for search requests."""
    query: str
    total_results: int
    cached: bool
    cached_at: Optional[datetime] = None
    results: list[SearchResult]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "query": "Acme Corporation product launch",
                "total_results": 15,
                "cached": True,
                "cached_at": "2025-10-16T10:30:00Z",
                "results": [
                    {
                        "title": "Acme Launches Revolutionary New Product",
                        "description": "Acme Corporation today announced...",
                        "url": "https://techcrunch.com/...",
                        "source": "TechCrunch",
                        "published_at": "2025-10-15T14:30:00Z",
                        "relevance_score": 0.92
                    }
                ]
            }
        }
    )
