/**
 * Dashboard API Service
 * Handles all dashboard and analytics API calls
 */

import { apiClient } from './api';

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
}

export interface DashboardSummary {
  // Client metrics
  total_clients: number;
  active_clients: number;
  clients_by_tier: Record<string, number>;
  clients_by_industry: Record<string, number>;

  // Event metrics
  total_events: number;
  unread_events: number;
  starred_events: number;
  recent_events: number;

  // Activity metrics
  events_by_category: Record<string, number>;
  sentiment_distribution: SentimentDistribution;

  // Time-based metrics
  events_this_week: number;
  events_this_month: number;
  events_today: number;

  // Quality metrics
  avg_relevance_score: number;
  high_relevance_events: number;
}

export interface TimelineDataPoint {
  date: string;
  value: number;
}

export interface EventTimelineResponse {
  timeline: TimelineDataPoint[];
  total_events: number;
  period_start: string;
  period_end: string;
}

export interface CategoryDataPoint {
  category: string;
  count: number;
  percentage: number;
}

export interface CategoryAnalytics {
  distribution: CategoryDataPoint[];
  total_events: number;
  unique_categories: number;
}

export interface SentimentDataPoint {
  name: string;
  value: number;
  percentage: number;
}

export interface SentimentAnalytics {
  distribution: SentimentDistribution;
  total_events: number;
  avg_sentiment_score: number;
}

export interface ClientActivityMetrics {
  client_id: string; // UUID
  client_name: string;
  event_count: number;
  last_event_date: string | null;
}

export interface TopClientsResponse {
  clients: ClientActivityMetrics[];
  period_days: number;
}

export interface GrowthMetrics {
  event_growth: {
    current_period: number;
    previous_period: number;
    change_percentage: number;
    trend: 'up' | 'down' | 'stable';
  };
  client_growth: {
    current_period: number;
    previous_period: number;
    change_percentage: number;
    trend: 'up' | 'down' | 'stable';
  };
  period_days: number;
}

/**
 * Get complete dashboard summary
 */
export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await apiClient.get<DashboardSummary>('/api/v1/analytics/dashboard');
  return response.data;
}

/**
 * Get event timeline data
 */
export async function getEventTimeline(
  days: number = 30,
  groupBy: 'day' | 'week' = 'day'
): Promise<EventTimelineResponse> {
  const response = await apiClient.get<EventTimelineResponse>('/api/v1/analytics/events/timeline', {
    params: { days, group_by: groupBy },
  });
  return response.data;
}

/**
 * Get category analytics
 */
export async function getCategoryAnalytics(): Promise<CategoryAnalytics> {
  const response = await apiClient.get<CategoryAnalytics>('/api/v1/analytics/events/categories');
  return response.data;
}

/**
 * Get sentiment analytics
 */
export async function getSentimentAnalytics(): Promise<SentimentAnalytics> {
  const response = await apiClient.get<SentimentAnalytics>('/api/v1/analytics/events/sentiment');
  return response.data;
}

/**
 * Get top clients by activity
 */
export async function getTopClients(
  limit: number = 10,
  days: number = 30
): Promise<TopClientsResponse> {
  const response = await apiClient.get<TopClientsResponse>('/api/v1/analytics/clients/top-activity', {
    params: { limit, days },
  });
  return response.data;
}

/**
 * Get growth metrics
 */
export async function getGrowthMetrics(periodDays: number = 7): Promise<GrowthMetrics> {
  const response = await apiClient.get<GrowthMetrics>('/api/v1/analytics/growth', {
    params: { period_days: periodDays },
  });
  return response.data;
}
