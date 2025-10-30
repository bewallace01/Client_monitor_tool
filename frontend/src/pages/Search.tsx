/**
 * Search Page
 * Search and browse cached intelligence data
 */

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  performSearch,
  getCacheStats,
  cleanupExpiredCache,
  type SearchResponse,
} from '../services/search';
import SearchBar, { type SearchOptions } from '../components/Search/SearchBar';
import SearchResults from '../components/Search/SearchResults';

export default function Search() {
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [currentQuery, setCurrentQuery] = useState('');

  // Fetch cache stats
  const { data: stats } = useQuery({
    queryKey: ['search-cache-stats'],
    queryFn: getCacheStats,
    refetchInterval: 60000, // Refresh every minute
  });

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: (params: { query: string; options: SearchOptions }) =>
      performSearch({
        query: params.query,
        source: params.options.source,
        use_cache: params.options.useCache,
        max_results: params.options.maxResults,
      }),
    onSuccess: (data) => {
      setSearchData(data);
    },
  });

  // Cleanup mutation
  const cleanupMutation = useMutation({
    mutationFn: cleanupExpiredCache,
    onSuccess: () => {
      // Refetch stats after cleanup
      window.location.reload();
    },
  });

  const handleSearch = (query: string, options: SearchOptions) => {
    setCurrentQuery(query);
    searchMutation.mutate({ query, options });
  };

  const handleCleanup = () => {
    if (
      window.confirm(
        'This will delete all expired cache entries. Are you sure?'
      )
    ) {
      cleanupMutation.mutate();
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Search</h1>
            <p className="text-gray-600 mt-2">
              Search for intelligence data and browse cached results
            </p>
          </div>
          {stats && (
            <div className="flex gap-4">
              <div className="text-right">
                <div className="text-sm text-gray-500">Cache Entries</div>
                <div className="text-2xl font-bold text-gray-900">
                  {stats.active_entries}
                </div>
              </div>
              {stats.expired_entries > 0 && (
                <button
                  onClick={handleCleanup}
                  disabled={cleanupMutation.isPending}
                  className="px-4 py-2 text-sm border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                >
                  {cleanupMutation.isPending ? 'Cleaning...' : `Clean ${stats.expired_entries} Expired`}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Cache Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Total Entries</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats.total_entries}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Active</div>
            <div className="text-2xl font-bold text-green-600">
              {stats.active_entries}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Expired</div>
            <div className="text-2xl font-bold text-red-600">
              {stats.expired_entries}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Hit Rate</div>
            <div className="text-2xl font-bold text-blue-600">
              {stats.cache_hit_rate !== null
                ? `${Math.round(stats.cache_hit_rate * 100)}%`
                : 'N/A'}
            </div>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6">
        <SearchBar
          onSearch={handleSearch}
          isLoading={searchMutation.isPending}
        />
      </div>

      {/* Error Message */}
      {searchMutation.isError && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">
            Failed to perform search. Please try again.
          </p>
        </div>
      )}

      {/* Search Results or Empty State */}
      {searchData ? (
        <SearchResults
          results={searchData.results}
          query={currentQuery}
          totalResults={searchData.total_results}
          cached={searchData.cached}
          cachedAt={searchData.cached_at}
          loading={searchMutation.isPending}
        />
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Ready to Search
          </h3>
          <p className="text-gray-600">
            Enter a search query above to find news, events, and intelligence data.
          </p>
          <div className="mt-6 text-left max-w-2xl mx-auto">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Search Tips:
            </h4>
            <ul className="text-sm text-gray-600 space-y-2">
              <li>• Use specific keywords for better results</li>
              <li>• Try company names, products, or industry terms</li>
              <li>• Enable caching to get faster results for repeated searches</li>
              <li>• Adjust the data source in advanced options</li>
            </ul>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400 text-xl">ℹ️</span>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              Search results are cached to improve performance and reduce API calls.
              Cached results are reused when the same query is made within 24 hours.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
