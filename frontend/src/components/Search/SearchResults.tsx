/**
 * SearchResults Component
 * Display search results in a list
 */

import type { SearchResult } from '../../services/search';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  totalResults: number;
  cached: boolean;
  cachedAt: string | null;
  loading?: boolean;
}

export default function SearchResults({
  results,
  query,
  totalResults,
  cached,
  cachedAt,
  loading = false,
}: SearchResultsProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
        <p className="text-gray-600">
          Try different keywords or check your spelling.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Results Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {totalResults} {totalResults === 1 ? 'result' : 'results'} for "{query}"
            </h2>
            {cached && cachedAt && (
              <p className="text-sm text-gray-500 mt-1">
                Cached results from {new Date(cachedAt).toLocaleString()}
              </p>
            )}
          </div>
          {cached && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              Cached
            </span>
          )}
        </div>
      </div>

      {/* Results List */}
      <div className="divide-y divide-gray-200">
        {results.map((result, index) => (
          <div
            key={index}
            className="px-6 py-5 hover:bg-gray-50 transition-colors"
          >
            {/* Title */}
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {result.title}
              </a>
            </h3>

            {/* Description */}
            {result.description && (
              <p className="text-gray-700 mb-3 line-clamp-3">
                {result.description}
              </p>
            )}

            {/* Metadata */}
            <div className="flex items-center gap-4 text-sm text-gray-500">
              {result.source && (
                <span className="flex items-center gap-1">
                  <span className="text-gray-400">📰</span>
                  {result.source}
                </span>
              )}
              {result.published_at && (
                <span className="flex items-center gap-1">
                  <span className="text-gray-400">📅</span>
                  {new Date(result.published_at).toLocaleDateString()}
                </span>
              )}
              {result.relevance_score !== null && (
                <span className="flex items-center gap-1">
                  <span className="text-gray-400">⭐</span>
                  {Math.round(result.relevance_score * 100)}% relevant
                </span>
              )}
            </div>

            {/* URL */}
            <div className="mt-2">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-green-700 hover:underline break-all"
              >
                {result.url}
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
