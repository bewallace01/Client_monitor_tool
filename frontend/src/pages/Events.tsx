/**
 * Events Page
 * Main page for viewing and managing events
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getEvents,
  updateEvent,
  deleteEvent,
  getCategories,
  bulkUpdateEvents,
  bulkDeleteEvents,
} from '../services/events';
import type { Event, EventsFilters } from '../services/events';
import EventList from '../components/Events/EventList';
import EventCard from '../components/Events/EventCard';
import EventDetail from '../components/Events/EventDetail';
import EventFilters from '../components/Events/EventFilters';

type ViewMode = 'table' | 'cards';

export default function Events() {
  const queryClient = useQueryClient();
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [filters, setFilters] = useState<EventsFilters>({
    skip: 0,
    limit: 20,
    sort_by: 'event_date',
    sort_desc: true,
  });
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<Event | null>(null);

  // Fetch events with filters
  const { data, isLoading, error } = useQuery({
    queryKey: ['events', filters],
    queryFn: () => getEvents(filters),
    refetchInterval: 30000,
  });

  // Fetch categories for filter dropdown
  const { data: categories } = useQuery({
    queryKey: ['event-categories'],
    queryFn: getCategories,
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) =>
      updateEvent(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (eventId: string) => deleteEvent(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      setEventToDelete(null);
    },
  });

  // Bulk update mutation
  const bulkUpdateMutation = useMutation({
    mutationFn: bulkUpdateEvents,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      setSelectedIds(new Set());
    },
  });

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: bulkDeleteEvents,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      setSelectedIds(new Set());
    },
  });

  const handleView = (event: Event) => {
    setSelectedEvent(event);
    setIsDetailOpen(true);
  };

  const handleEdit = (event: Event) => {
    // For now, just open detail view - we can add a form modal later
    setSelectedEvent(event);
    setIsDetailOpen(true);
  };

  const handleDelete = (event: Event) => {
    setEventToDelete(event);
  };

  const handleToggleSelection = (eventId: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(eventId)) {
      newSelected.delete(eventId);
    } else {
      newSelected.add(eventId);
    }
    setSelectedIds(newSelected);
  };

  const handleToggleAll = () => {
    if (data && data.items.length > 0) {
      const allIds = data.items.map((e) => e.id);
      const allSelected = allIds.every((id) => selectedIds.has(id));
      if (allSelected) {
        setSelectedIds(new Set());
      } else {
        setSelectedIds(new Set(allIds));
      }
    }
  };

  const handleToggleStar = (event: Event) => {
    updateMutation.mutate({
      id: event.id,
      updates: { is_starred: !event.is_starred },
    });
  };

  const handleToggleRead = (event: Event) => {
    updateMutation.mutate({
      id: event.id,
      updates: { is_read: !event.is_read },
    });
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({
      ...prev,
      skip: (page - 1) * (prev.limit || 20),
    }));
  };

  const handleFilterChange = (filterKey: string, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [filterKey]: value === '' || value === undefined ? undefined : value,
      skip: 0, // Reset to first page
    }));
  };

  const handleBulkMarkRead = () => {
    bulkUpdateMutation.mutate({
      event_ids: Array.from(selectedIds),
      is_read: true,
    });
  };

  const handleBulkMarkUnread = () => {
    bulkUpdateMutation.mutate({
      event_ids: Array.from(selectedIds),
      is_read: false,
    });
  };

  const handleBulkStar = () => {
    bulkUpdateMutation.mutate({
      event_ids: Array.from(selectedIds),
      is_starred: true,
    });
  };

  const handleBulkDelete = () => {
    if (window.confirm(`Delete ${selectedIds.size} selected events?`)) {
      bulkDeleteMutation.mutate(Array.from(selectedIds));
    }
  };

  if (error) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Events</h1>
          <p className="text-gray-600 mt-2">Monitor client-related events and news</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">
            Failed to load events. Please check if the API server is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-6">
      {/* Sidebar Filters */}
      <div className="w-64 flex-shrink-0">
        <EventFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          categories={categories}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Events</h1>
              <p className="text-gray-600 mt-2">
                Monitor client-related events and news
              </p>
            </div>
            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <div className="bg-white rounded-lg shadow p-1 flex gap-1">
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    viewMode === 'table'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Table
                </button>
                <button
                  onClick={() => setViewMode('cards')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    viewMode === 'cards'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Cards
                </button>
              </div>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedIds.size > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between">
              <span className="text-sm font-medium text-blue-900">
                {selectedIds.size} event{selectedIds.size !== 1 ? 's' : ''} selected
              </span>
              <div className="flex gap-2">
                <button
                  onClick={handleBulkMarkRead}
                  disabled={bulkUpdateMutation.isPending}
                  className="px-3 py-1 text-sm bg-white border border-blue-300 text-blue-700 rounded hover:bg-blue-50 transition-colors disabled:opacity-50"
                >
                  Mark Read
                </button>
                <button
                  onClick={handleBulkMarkUnread}
                  disabled={bulkUpdateMutation.isPending}
                  className="px-3 py-1 text-sm bg-white border border-blue-300 text-blue-700 rounded hover:bg-blue-50 transition-colors disabled:opacity-50"
                >
                  Mark Unread
                </button>
                <button
                  onClick={handleBulkStar}
                  disabled={bulkUpdateMutation.isPending}
                  className="px-3 py-1 text-sm bg-white border border-blue-300 text-blue-700 rounded hover:bg-blue-50 transition-colors disabled:opacity-50"
                >
                  Star
                </button>
                <button
                  onClick={handleBulkDelete}
                  disabled={bulkDeleteMutation.isPending}
                  className="px-3 py-1 text-sm bg-white border border-red-300 text-red-700 rounded hover:bg-red-50 transition-colors disabled:opacity-50"
                >
                  Delete
                </button>
                <button
                  onClick={() => setSelectedIds(new Set())}
                  className="px-3 py-1 text-sm bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Event List or Cards */}
        {viewMode === 'table' ? (
          <EventList
            events={data?.items || []}
            loading={isLoading}
            selectedIds={selectedIds}
            onToggleSelection={handleToggleSelection}
            onToggleAll={handleToggleAll}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ) : (
          <div className="space-y-4">
            {isLoading ? (
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-32 bg-gray-200 rounded animate-pulse"></div>
                ))}
              </div>
            ) : data?.items.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-6xl mb-4">📰</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No events found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your filters or add new events to get started.
                </p>
              </div>
            ) : (
              data?.items.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  selected={selectedIds.has(event.id)}
                  onToggleSelection={handleToggleSelection}
                  onView={handleView}
                  onEdit={handleEdit}
                  onToggleStar={handleToggleStar}
                  onToggleRead={handleToggleRead}
                />
              ))
            )}
          </div>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="mt-6 bg-white rounded-lg shadow px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page {Math.floor((filters.skip || 0) / (filters.limit || 20)) + 1} of{' '}
              {data.total_pages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() =>
                  handlePageChange(
                    Math.floor((filters.skip || 0) / (filters.limit || 20))
                  )
                }
                disabled={filters.skip === 0}
                className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() =>
                  handlePageChange(
                    Math.floor((filters.skip || 0) / (filters.limit || 20)) + 2
                  )
                }
                disabled={
                  Math.floor((filters.skip || 0) / (filters.limit || 20)) + 1 >=
                  data.total_pages
                }
                className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Event Detail Modal */}
        {isDetailOpen && selectedEvent && (
          <EventDetail
            event={selectedEvent}
            onClose={() => {
              setIsDetailOpen(false);
              setSelectedEvent(null);
            }}
            onEdit={() => {
              // In the future, open an edit form modal
              setIsDetailOpen(false);
            }}
          />
        )}

        {/* Delete Confirmation Modal */}
        {eventToDelete && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Delete Event
              </h3>
              <p className="text-gray-600 mb-4">
                Are you sure you want to delete this event:{' '}
                <strong>{eventToDelete.title}</strong>? This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setEventToDelete(null)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (eventToDelete) {
                      deleteMutation.mutate(eventToDelete.id);
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
