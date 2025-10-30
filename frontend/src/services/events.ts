/**
 * Events API Service
 * Handles all event-related API calls
 */

import { apiClient } from './api';

export type EventCategory =
  | 'funding'
  | 'acquisition'
  | 'leadership'
  | 'leadership_change'
  | 'product'
  | 'product_launch'
  | 'partnership'
  | 'financial'
  | 'financial_results'
  | 'regulatory'
  | 'award'
  | 'news'
  | 'other';

export interface Event {
  id: string; // UUID
  client_id: string; // UUID
  title: string;
  description: string | null;
  url: string | null;
  source: string | null;
  category: EventCategory;
  relevance_score: number;
  sentiment_score: number | null;
  event_date: string;
  discovered_at: string;
  content_hash: string | null;
  is_read: boolean;
  is_starred: boolean;
  user_notes: string | null;
}

export interface EventWithClient extends Event {
  client_name: string;
  client_domain: string | null;
}

export interface EventCreate {
  client_id: string; // UUID
  title: string;
  description?: string | null;
  url?: string | null;
  source?: string | null;
  category?: EventCategory;
  relevance_score?: number;
  sentiment_score?: number | null;
  event_date: string;
  content_hash?: string | null;
}

export interface EventUpdate {
  title?: string;
  description?: string | null;
  url?: string | null;
  source?: string | null;
  category?: EventCategory;
  relevance_score?: number;
  sentiment_score?: number | null;
  event_date?: string;
  is_read?: boolean;
  is_starred?: boolean;
  user_notes?: string | null;
}

export interface EventListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Event[];
}

export interface EventsFilters {
  skip?: number;
  limit?: number;
  client_id?: string; // UUID
  category?: EventCategory;
  is_read?: boolean;
  is_starred?: boolean;
  min_relevance?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface EventStats {
  total_events: number;
  unread_events: number;
  starred_events: number;
  events_by_category: Record<string, number>;
  events_by_sentiment: Record<string, number>;
  recent_events_count: number;
}

export interface BulkEventUpdate {
  event_ids: string[]; // UUIDs
  is_read?: boolean;
  is_starred?: boolean;
}

/**
 * Get paginated list of events with optional filters
 */
export async function getEvents(filters?: EventsFilters): Promise<EventListResponse> {
  const response = await apiClient.get<EventListResponse>('/api/v1/events', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single event by ID
 */
export async function getEvent(eventId: string): Promise<Event> {
  const response = await apiClient.get<Event>(`/api/v1/events/${eventId}`);
  return response.data;
}

/**
 * Create a new event
 */
export async function createEvent(event: EventCreate): Promise<Event> {
  const response = await apiClient.post<Event>('/api/v1/events', event);
  return response.data;
}

/**
 * Update an existing event
 */
export async function updateEvent(eventId: string, updates: EventUpdate): Promise<Event> {
  const response = await apiClient.put<Event>(`/api/v1/events/${eventId}`, updates);
  return response.data;
}

/**
 * Delete an event
 */
export async function deleteEvent(eventId: string): Promise<void> {
  await apiClient.delete(`/api/v1/events/${eventId}`);
}

/**
 * Get event statistics
 */
export async function getEventStats(): Promise<EventStats> {
  const response = await apiClient.get<EventStats>('/api/v1/events/stats');
  return response.data;
}

/**
 * Get list of all event categories
 */
export async function getCategories(): Promise<string[]> {
  const response = await apiClient.get<string[]>('/api/v1/events/categories');
  return response.data;
}

/**
 * Bulk update multiple events
 */
export async function bulkUpdateEvents(update: BulkEventUpdate): Promise<void> {
  await apiClient.post('/api/v1/events/bulk-update', update);
}

/**
 * Bulk delete multiple events
 */
export async function bulkDeleteEvents(eventIds: string[]): Promise<void> {
  await apiClient.post('/api/v1/events/bulk-delete', eventIds);
}
