/**
 * EventCard Component
 * Card view of a single event
 */

import type { Event } from '../../services/events';

interface EventCardProps {
  event: Event;
  selected: boolean;
  onToggleSelection: (eventId: number) => void;
  onView: (event: Event) => void;
  onEdit: (event: Event) => void;
  onToggleStar: (event: Event) => void;
  onToggleRead: (event: Event) => void;
}

export default function EventCard({
  event,
  selected,
  onToggleSelection,
  onView,
  onEdit,
  onToggleStar,
  onToggleRead,
}: EventCardProps) {
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      funding: 'bg-green-100 text-green-800 border-green-200',
      acquisition: 'bg-purple-100 text-purple-800 border-purple-200',
      leadership: 'bg-blue-100 text-blue-800 border-blue-200',
      leadership_change: 'bg-blue-100 text-blue-800 border-blue-200',
      product: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      product_launch: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      partnership: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      financial: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      financial_results: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      regulatory: 'bg-red-100 text-red-800 border-red-200',
      award: 'bg-pink-100 text-pink-800 border-pink-200',
      news: 'bg-gray-100 text-gray-800 border-gray-200',
      other: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[category] || colors.other;
  };

  const getSentimentIcon = (score: number | null) => {
    if (score === null) return { icon: '○', label: 'Unknown' };
    if (score > 0.3) return { icon: '😊', label: 'Positive' };
    if (score < -0.3) return { icon: '😟', label: 'Negative' };
    return { icon: '😐', label: 'Neutral' };
  };

  const sentiment = getSentimentIcon(event.sentiment_score);

  return (
    <div
      className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow p-4 border-2 ${
        selected ? 'border-blue-500' : 'border-transparent'
      } ${!event.is_read ? 'bg-blue-50' : ''}`}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onToggleSelection(event.id)}
          className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h3
              className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-blue-600"
              onClick={() => onView(event)}
            >
              {event.title}
            </h3>
            <button
              onClick={() => onToggleStar(event)}
              className="text-xl hover:scale-110 transition-transform flex-shrink-0"
            >
              {event.is_starred ? '⭐' : '☆'}
            </button>
          </div>

          {/* Category and Status */}
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span
              className={`px-2 py-1 text-xs font-semibold rounded border ${getCategoryColor(
                event.category
              )}`}
            >
              {event.category.replace('_', ' ')}
            </span>
            {!event.is_read && (
              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded border border-blue-200">
                New
              </span>
            )}
            <span className="text-sm" title={sentiment.label}>
              {sentiment.icon}
            </span>
          </div>

          {/* Description */}
          {event.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-3">
              {event.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 mb-3">
            {event.source && (
              <div className="flex items-center gap-1">
                <span className="font-medium">Source:</span>
                <span>{event.source}</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <span className="font-medium">Date:</span>
              <span>{new Date(event.event_date).toLocaleDateString()}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-medium">Relevance:</span>
              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    event.relevance_score > 0.7
                      ? 'bg-green-600'
                      : event.relevance_score > 0.4
                      ? 'bg-yellow-600'
                      : 'bg-red-600'
                  }`}
                  style={{ width: `${event.relevance_score * 100}%` }}
                ></div>
              </div>
              <span>{Math.round(event.relevance_score * 100)}%</span>
            </div>
          </div>

          {/* User Notes */}
          {event.user_notes && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-2 mb-3">
              <p className="text-xs text-gray-700">{event.user_notes}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 pt-3 border-t border-gray-200">
            {event.url && (
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                View Source →
              </a>
            )}
            <button
              onClick={() => onView(event)}
              className="text-xs text-gray-600 hover:text-gray-800 font-medium"
            >
              Details
            </button>
            <button
              onClick={() => onEdit(event)}
              className="text-xs text-gray-600 hover:text-gray-800 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => onToggleRead(event)}
              className="text-xs text-gray-600 hover:text-gray-800 font-medium ml-auto"
            >
              Mark as {event.is_read ? 'Unread' : 'Read'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
