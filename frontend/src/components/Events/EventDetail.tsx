/**
 * EventDetail Component
 * Modal displaying full event details
 */

import type { Event } from '../../services/events';

interface EventDetailProps {
  event: Event;
  onClose: () => void;
  onEdit: () => void;
}

export default function EventDetail({ event, onClose, onEdit }: EventDetailProps) {
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

  const getSentimentLabel = (score: number | null) => {
    if (score === null) return { label: 'Unknown', color: 'text-gray-600', icon: '○' };
    if (score > 0.3) return { label: 'Positive', color: 'text-green-600', icon: '😊' };
    if (score < -0.3) return { label: 'Negative', color: 'text-red-600', icon: '😟' };
    return { label: 'Neutral', color: 'text-gray-600', icon: '😐' };
  };

  const sentiment = getSentimentLabel(event.sentiment_score);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900">{event.title}</h2>
            {event.is_starred && <span className="text-2xl">⭐</span>}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Status Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${getCategoryColor(
                event.category
              )}`}
            >
              {event.category.replace('_', ' ')}
            </span>
            {!event.is_read && (
              <span className="px-3 py-1 inline-flex text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
                Unread
              </span>
            )}
            <span className={`text-2xl ${sentiment.color}`} title={sentiment.label}>
              {sentiment.icon}
            </span>
          </div>

          {/* Description */}
          {event.description && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Description
              </label>
              <p className="text-gray-900 whitespace-pre-wrap">{event.description}</p>
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Relevance Score
              </label>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      event.relevance_score > 0.7
                        ? 'bg-green-600'
                        : event.relevance_score > 0.4
                        ? 'bg-yellow-600'
                        : 'bg-red-600'
                    }`}
                    style={{ width: `${event.relevance_score * 100}%` }}
                  ></div>
                </div>
                <span className="text-lg font-semibold text-gray-900">
                  {Math.round(event.relevance_score * 100)}%
                </span>
              </div>
            </div>

            {event.sentiment_score !== null && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Sentiment Score
                </label>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        event.sentiment_score > 0
                          ? 'bg-green-600'
                          : event.sentiment_score < 0
                          ? 'bg-red-600'
                          : 'bg-gray-600'
                      }`}
                      style={{
                        width: `${Math.abs(event.sentiment_score) * 50 + 50}%`,
                        marginLeft: event.sentiment_score < 0 ? '0' : '50%',
                      }}
                    ></div>
                  </div>
                  <span className={`text-lg font-semibold ${sentiment.color}`}>
                    {sentiment.label}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Source Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {event.source && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Source
                </label>
                <p className="text-gray-900">{event.source}</p>
              </div>
            )}

            {event.url && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">URL</label>
                <a
                  href={event.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline break-all"
                >
                  {event.url}
                </a>
              </div>
            )}
          </div>

          {/* User Notes */}
          {event.user_notes && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                User Notes
              </label>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <p className="text-gray-900 whitespace-pre-wrap">{event.user_notes}</p>
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Event Date
              </label>
              <p className="text-sm text-gray-900">
                {new Date(event.event_date).toLocaleString()}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Discovered At
              </label>
              <p className="text-sm text-gray-900">
                {new Date(event.discovered_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            {event.url && (
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                View Source
              </a>
            )}
            <button
              onClick={onEdit}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Edit Event
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
