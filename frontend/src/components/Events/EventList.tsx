/**
 * EventList Component
 * Table view of events with selection and actions
 */

import type { Event } from '../../services/events';

interface EventListProps {
  events: Event[];
  loading: boolean;
  selectedIds: Set<number>;
  onToggleSelection: (eventId: number) => void;
  onToggleAll: () => void;
  onView: (event: Event) => void;
  onEdit: (event: Event) => void;
  onDelete: (event: Event) => void;
}

export default function EventList({
  events,
  loading,
  selectedIds,
  onToggleSelection,
  onToggleAll,
  onView,
  onEdit,
  onDelete,
}: EventListProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">📰</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          No events found
        </h3>
        <p className="text-gray-600">
          Try adjusting your filters or add new events to get started.
        </p>
      </div>
    );
  }

  const allSelected = events.length > 0 && events.every((e) => selectedIds.has(e.id));

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      funding: 'bg-green-100 text-green-800',
      acquisition: 'bg-purple-100 text-purple-800',
      leadership: 'bg-blue-100 text-blue-800',
      leadership_change: 'bg-blue-100 text-blue-800',
      product: 'bg-indigo-100 text-indigo-800',
      product_launch: 'bg-indigo-100 text-indigo-800',
      partnership: 'bg-cyan-100 text-cyan-800',
      financial: 'bg-yellow-100 text-yellow-800',
      financial_results: 'bg-yellow-100 text-yellow-800',
      regulatory: 'bg-red-100 text-red-800',
      award: 'bg-pink-100 text-pink-800',
      news: 'bg-gray-100 text-gray-800',
      other: 'bg-gray-100 text-gray-800',
    };
    return colors[category] || colors.other;
  };

  const getSentimentIcon = (score: number | null) => {
    if (score === null) return '○';
    if (score > 0.3) return '😊';
    if (score < -0.3) return '😟';
    return '😐';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={onToggleAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Event
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Relevance
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {events.map((event) => (
              <tr
                key={event.id}
                className={`hover:bg-gray-50 transition-colors ${
                  !event.is_read ? 'bg-blue-50' : ''
                }`}
              >
                <td className="px-4 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(event.id)}
                    onChange={() => onToggleSelection(event.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-start gap-2">
                    {event.is_starred && <span className="text-yellow-500">⭐</span>}
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {event.title}
                      </div>
                      {event.description && (
                        <div className="text-sm text-gray-500 mt-1 line-clamp-2">
                          {event.description}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getCategoryColor(
                      event.category
                    )}`}
                  >
                    {event.category.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{event.source || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(event.event_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center gap-1">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          event.relevance_score > 0.7
                            ? 'bg-green-600'
                            : event.relevance_score > 0.4
                            ? 'bg-yellow-600'
                            : 'bg-red-600'
                        }`}
                        style={{ width: `${event.relevance_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">
                      {Math.round(event.relevance_score * 100)}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center gap-2">
                    <span title="Sentiment">
                      {getSentimentIcon(event.sentiment_score)}
                    </span>
                    {!event.is_read && (
                      <span
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                        title="Unread"
                      >
                        New
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onView(event)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View
                  </button>
                  <button
                    onClick={() => onEdit(event)}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(event)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
