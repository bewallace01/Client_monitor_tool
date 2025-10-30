/**
 * Dashboard Page
 * Main overview and analytics dashboard
 */

import { useQuery } from '@tanstack/react-query';
import StatsCard from '../components/Dashboard/StatsCard';
import EventsChart from '../components/Dashboard/EventsChart';
import SentimentChart from '../components/Dashboard/SentimentChart';
import CategoryChart from '../components/Dashboard/CategoryChart';
import {
  getDashboardSummary,
  getEventTimeline,
  getCategoryAnalytics,
  getSentimentAnalytics,
} from '../services/dashboard';

export default function Dashboard() {
  // Fetch dashboard summary
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: getDashboardSummary,
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch event timeline
  const { data: timeline, isLoading: timelineLoading } = useQuery({
    queryKey: ['event-timeline', 30],
    queryFn: () => getEventTimeline(30, 'day'),
    refetchInterval: 60000,
  });

  // Fetch category analytics
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['category-analytics'],
    queryFn: getCategoryAnalytics,
    refetchInterval: 60000,
  });

  // Fetch sentiment analytics
  const { data: sentiment, isLoading: sentimentLoading } = useQuery({
    queryKey: ['sentiment-analytics'],
    queryFn: getSentimentAnalytics,
    refetchInterval: 60000,
  });

  // Show error state
  if (summaryError) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Overview of client monitoring and intelligence activities
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">
            Failed to load dashboard data. Please check if the API server is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of client monitoring and intelligence activities
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatsCard
          label="Total Clients"
          value={summary?.total_clients ?? '--'}
          icon="👥"
          loading={summaryLoading}
        />
        <StatsCard
          label="Total Events"
          value={summary?.total_events ?? '--'}
          icon="📰"
          loading={summaryLoading}
        />
        <StatsCard
          label="Unread Events"
          value={summary?.unread_events ?? '--'}
          icon="📬"
          loading={summaryLoading}
        />
        <StatsCard
          label="This Week"
          value={summary?.events_this_week ?? '--'}
          icon="📊"
          loading={summaryLoading}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <EventsChart
          data={timeline?.timeline || []}
          loading={timelineLoading}
        />
        <CategoryChart
          data={categories?.distribution || []}
          loading={categoriesLoading}
        />
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SentimentChart
          data={sentiment?.distribution ? [
            { name: 'Positive', value: sentiment.distribution.positive, percentage: sentiment.distribution.positive_percentage },
            { name: 'Neutral', value: sentiment.distribution.neutral, percentage: sentiment.distribution.neutral_percentage },
            { name: 'Negative', value: sentiment.distribution.negative, percentage: sentiment.distribution.negative_percentage },
          ] : []}
          loading={sentimentLoading}
        />

        {/* Quick Stats Panel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
          {summaryLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-4 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Clients</span>
                <span className="text-lg font-semibold text-gray-900">
                  {summary?.active_clients || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Starred Events</span>
                <span className="text-lg font-semibold text-gray-900">
                  {summary?.starred_events || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Today's Events</span>
                <span className="text-lg font-semibold text-gray-900">
                  {summary?.events_today || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">This Month</span>
                <span className="text-lg font-semibold text-gray-900">
                  {summary?.events_this_month || 0}
                </span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                <span className="text-sm text-gray-600">Avg Relevance</span>
                <span className={`text-lg font-semibold ${
                  (summary?.avg_relevance_score || 0) >= 0.7
                    ? 'text-green-600'
                    : (summary?.avg_relevance_score || 0) >= 0.4
                    ? 'text-yellow-600'
                    : 'text-red-600'
                }`}>
                  {(summary?.avg_relevance_score || 0).toFixed(2)}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
