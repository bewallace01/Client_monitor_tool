/**
 * EventFilters Component
 * Sidebar filters for events
 */

import type { EventsFilters, EventCategory } from '../../services/events';

interface EventFiltersProps {
  filters: EventsFilters;
  onFilterChange: (key: string, value: any) => void;
  categories?: string[];
}

export default function EventFilters({
  filters,
  onFilterChange,
  categories = [],
}: EventFiltersProps) {
  const categoryOptions: EventCategory[] = [
    'funding',
    'acquisition',
    'leadership',
    'leadership_change',
    'product',
    'product_launch',
    'partnership',
    'financial',
    'financial_results',
    'regulatory',
    'award',
    'news',
    'other',
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Filters</h3>

      {/* Search */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Search
        </label>
        <input
          type="text"
          placeholder="Search events..."
          value={filters.search || ''}
          onChange={(e) => onFilterChange('search', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        />
      </div>

      {/* Category Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Category
        </label>
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange('category', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        >
          <option value="">All Categories</option>
          {(categories.length > 0 ? categories : categoryOptions).map((category) => (
            <option key={category} value={category}>
              {category.replace('_', ' ')}
            </option>
          ))}
        </select>
      </div>

      {/* Read Status Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Read Status
        </label>
        <select
          value={
            filters.is_read === undefined ? '' : filters.is_read ? 'read' : 'unread'
          }
          onChange={(e) =>
            onFilterChange(
              'is_read',
              e.target.value === '' ? undefined : e.target.value === 'read'
            )
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        >
          <option value="">All</option>
          <option value="unread">Unread Only</option>
          <option value="read">Read Only</option>
        </select>
      </div>

      {/* Starred Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Starred
        </label>
        <select
          value={
            filters.is_starred === undefined
              ? ''
              : filters.is_starred
              ? 'starred'
              : 'unstarred'
          }
          onChange={(e) =>
            onFilterChange(
              'is_starred',
              e.target.value === '' ? undefined : e.target.value === 'starred'
            )
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        >
          <option value="">All</option>
          <option value="starred">Starred Only</option>
          <option value="unstarred">Not Starred</option>
        </select>
      </div>

      {/* Relevance Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Relevance
        </label>
        <div className="space-y-2">
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={(filters.min_relevance || 0) * 100}
            onChange={(e) =>
              onFilterChange('min_relevance', parseFloat(e.target.value) / 100)
            }
            className="w-full"
          />
          <div className="text-sm text-gray-600 text-center">
            {Math.round((filters.min_relevance || 0) * 100)}%
          </div>
        </div>
      </div>

      {/* Date Range Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Date Range
        </label>
        <div className="space-y-2">
          <input
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => onFilterChange('start_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="Start date"
          />
          <input
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => onFilterChange('end_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="End date"
          />
        </div>
      </div>

      {/* Clear Filters */}
      <button
        onClick={() => {
          onFilterChange('search', '');
          onFilterChange('category', undefined);
          onFilterChange('is_read', undefined);
          onFilterChange('is_starred', undefined);
          onFilterChange('min_relevance', 0);
          onFilterChange('start_date', undefined);
          onFilterChange('end_date', undefined);
        }}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
      >
        Clear All Filters
      </button>
    </div>
  );
}
