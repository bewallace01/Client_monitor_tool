/**
 * Search API Service
 * Handles all search and cache-related API calls
 */

import { apiClient } from './api';

export interface SearchResult {
  title: string;
  description: string | null;
  url: string;
  source: string;
  published_at: string | null;
  relevance_score: number | null;
}

export interface SearchQuery {
  query: string;
  source?: string;
  use_cache?: boolean;
  max_results?: number;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  cached: boolean;
  cached_at: string | null;
  results: SearchResult[];
}

export interface SearchCacheEntry {
  id: number;
  query_text: string;
  query_hash: string;
  source: string;
  results_json: string | null;
  result_count: number;
  cached_at: string;
  expires_at: string;
}

export interface SearchCacheListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: SearchCacheEntry[];
}

export interface SearchCacheStats {
  total_entries: number;
  active_entries: number;
  expired_entries: number;
  cache_hit_rate: number | null;
  entries_by_source: Record<string, number>;
}

/**
 * Perform a search query
 */
export async function performSearch(query: SearchQuery): Promise<SearchResponse> {
  const response = await apiClient.post<SearchResponse>('/api/v1/search/query', query);
  return response.data;
}

/**
 * Get list of cached search entries
 */
export async function getCacheEntries(params?: {
  skip?: number;
  limit?: number;
  source?: string;
  include_expired?: boolean;
}): Promise<SearchCacheListResponse> {
  const response = await apiClient.get<SearchCacheListResponse>('/api/v1/search/cache', {
    params,
  });
  return response.data;
}

/**
 * Get cache statistics
 */
export async function getCacheStats(): Promise<SearchCacheStats> {
  const response = await apiClient.get<SearchCacheStats>('/api/v1/search/cache/stats');
  return response.data;
}

/**
 * Get a single cache entry by ID
 */
export async function getCacheEntry(cacheId: number): Promise<SearchCacheEntry> {
  const response = await apiClient.get<SearchCacheEntry>(
    `/api/v1/search/cache/${cacheId}`
  );
  return response.data;
}

/**
 * Search through cached entries
 */
export async function searchCache(
  queryText: string,
  params?: { skip?: number; limit?: number }
): Promise<SearchCacheListResponse> {
  const response = await apiClient.get<SearchCacheListResponse>(
    `/api/v1/search/cache/search/${encodeURIComponent(queryText)}`,
    { params }
  );
  return response.data;
}

/**
 * Delete a cache entry
 */
export async function deleteCacheEntry(cacheId: number): Promise<void> {
  await apiClient.delete(`/api/v1/search/cache/${cacheId}`);
}

/**
 * Cleanup expired cache entries
 */
export async function cleanupExpiredCache(): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    '/api/v1/search/cache/expired/cleanup'
  );
  return response.data;
}

/**
 * Clear cache by source
 */
export async function clearCacheBySource(source: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `/api/v1/search/cache/source/${source}`
  );
  return response.data;
}

/**
 * Clear all cache
 */
export async function clearAllCache(): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    '/api/v1/search/cache/all'
  );
  return response.data;
}
