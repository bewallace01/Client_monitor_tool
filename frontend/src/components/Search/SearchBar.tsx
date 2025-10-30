/**
 * SearchBar Component
 * Search input with advanced options
 */

import { useState } from 'react';

interface SearchBarProps {
  onSearch: (query: string, options: SearchOptions) => void;
  isLoading?: boolean;
}

export interface SearchOptions {
  source: string;
  useCache: boolean;
  maxResults: number;
}

export default function SearchBar({ onSearch, isLoading = false }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [options, setOptions] = useState<SearchOptions>({
    source: 'news_api',
    useCache: true,
    maxResults: 20,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, options);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for news, events, and information..."
              className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              disabled={isLoading}
            />
            <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">
              🔍
            </span>
          </div>
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Advanced Options Toggle */}
        <div className="mt-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            {showAdvanced ? '▼' : '▶'} Advanced Options
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Source
              </label>
              <select
                value={options.source}
                onChange={(e) =>
                  setOptions((prev) => ({ ...prev, source: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="news_api">News API</option>
                <option value="google">Google Search</option>
                <option value="bing">Bing Search</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Results
              </label>
              <select
                value={options.maxResults}
                onChange={(e) =>
                  setOptions((prev) => ({
                    ...prev,
                    maxResults: parseInt(e.target.value),
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Caching
              </label>
              <div className="flex items-center h-10">
                <input
                  type="checkbox"
                  checked={options.useCache}
                  onChange={(e) =>
                    setOptions((prev) => ({ ...prev, useCache: e.target.checked }))
                  }
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  Use cached results
                </label>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
