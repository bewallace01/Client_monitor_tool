/**
 * Automation Page
 * Manage scheduled automation jobs and view execution history
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  // Schedule functions
  getSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  activateSchedule,
  deactivateSchedule,
  triggerSchedule,
  // Job run functions
  getJobRuns,
  getJobRunStats,
  deleteJobRun,
  // Manual event search
  triggerManualEventSearch,
} from '../services/automation';
import type {
  AutomationSchedule,
  ScheduleFilters,
  ScheduleCreate,
  JobRunFilters,
  ScheduleType,
  ManualEventSearchRequest,
} from '../services/automation';
import { getClients } from '../services/clients';

type TabType = 'schedules' | 'history';

export default function Automation() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('schedules');

  // Schedule state
  const [scheduleFilters, setScheduleFilters] = useState<ScheduleFilters>({
    skip: 0,
    limit: 20,
    sort_by: 'created_at',
    sort_desc: true,
  });
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<AutomationSchedule | null>(null);

  // Job history state
  const [historyFilters, setHistoryFilters] = useState<JobRunFilters>({
    skip: 0,
    limit: 20,
    sort_by: 'started_at',
    sort_desc: true,
  });
  // Manual event search state
  const [selectedClientIds, setSelectedClientIds] = useState<string[]>([]);
  const [daysBack, setDaysBack] = useState<number>(21); // 3 weeks default
  const [maxResults, setMaxResults] = useState<number>(10);

  // Fetch schedules
  const { data: schedules, isLoading: schedulesLoading, error: schedulesError } = useQuery({
    queryKey: ['automation-schedules', scheduleFilters],
    queryFn: () => getSchedules(scheduleFilters),
    refetchInterval: 30000,
  });

  // Fetch job runs
  const { data: jobRuns, isLoading: historyLoading, error: historyError } = useQuery({
    queryKey: ['job-runs', historyFilters],
    queryFn: () => getJobRuns(historyFilters),
    refetchInterval: 30000,
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['job-run-stats'],
    queryFn: getJobRunStats,
    refetchInterval: 30000,
  });

  // Fetch clients for dropdown
  const { data: clients } = useQuery({
    queryKey: ['clients'],
    queryFn: () => getClients({ skip: 0, limit: 100 }),
  });

  // Schedule mutations
  const createScheduleMutation = useMutation({
    mutationFn: (data: ScheduleCreate) => createSchedule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-schedules'] });
      setShowScheduleModal(false);
      setEditingSchedule(null);
    },
  });

  const updateScheduleMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AutomationSchedule> }) =>
      updateSchedule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-schedules'] });
      setShowScheduleModal(false);
      setEditingSchedule(null);
    },
  });

  const deleteScheduleMutation = useMutation({
    mutationFn: (scheduleId: string) => deleteSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-schedules'] });
    },
  });

  const activateScheduleMutation = useMutation({
    mutationFn: (scheduleId: string) => activateSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-schedules'] });
    },
  });

  const deactivateScheduleMutation = useMutation({
    mutationFn: (scheduleId: string) => deactivateSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-schedules'] });
    },
  });

  const triggerScheduleMutation = useMutation({
    mutationFn: (scheduleId: string) => triggerSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-runs'] });
      queryClient.invalidateQueries({ queryKey: ['job-run-stats'] });
    },
  });

  // Manual event search mutation
  const triggerEventSearchMutation = useMutation({
    mutationFn: (request: ManualEventSearchRequest) => triggerManualEventSearch(request),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['job-runs'] });
      queryClient.invalidateQueries({ queryKey: ['job-run-stats'] });
      // Reset form
      setSelectedClientIds([]);
      setDaysBack(21);
      setMaxResults(10);
      // Show success message (you can add a toast notification here)
      alert(`Event search completed!\n\nClients processed: ${response.clients_processed}\nEvents found: ${response.events_found}\nNew events: ${response.events_new}`);
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    },
  });

  const deleteJobMutation = useMutation({
    mutationFn: (jobRunId: number) => deleteJobRun(jobRunId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-runs'] });
      queryClient.invalidateQueries({ queryKey: ['job-run-stats'] });
    },
  });

  const handleToggleActive = (schedule: AutomationSchedule) => {
    if (schedule.is_active) {
      deactivateScheduleMutation.mutate(schedule.id);
    } else {
      activateScheduleMutation.mutate(schedule.id);
    }
  };

  const handleTriggerEventSearch = () => {
    const request: ManualEventSearchRequest = {
      client_ids: selectedClientIds.length > 0 ? selectedClientIds : null,
      days_back: daysBack,
      max_results_per_source: maxResults,
      force_mock: false,
    };
    triggerEventSearchMutation.mutate(request);
  };

  const handleSchedulePageChange = (page: number) => {
    setScheduleFilters((prev) => ({
      ...prev,
      skip: (page - 1) * (prev.limit || 20),
    }));
  };

  const handleHistoryPageChange = (page: number) => {
    setHistoryFilters((prev) => ({
      ...prev,
      skip: (page - 1) * (prev.limit || 20),
    }));
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  const formatScheduleType = (type: ScheduleType) => {
    const labels: Record<ScheduleType, string> = {
      manual: 'Manual',
      hourly: 'Hourly',
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      custom: 'Custom Cron',
    };
    return labels[type] || type;
  };

  const formatNextRun = (nextRunAt: string | null) => {
    if (!nextRunAt) return 'Not scheduled';
    const date = new Date(nextRunAt);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 0) return 'Overdue';
    if (diffMins < 60) return `in ${diffMins}m`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `in ${diffHours}h`;
    const diffDays = Math.floor(diffHours / 24);
    return `in ${diffDays}d`;
  };

  if (schedulesError || historyError) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-lg bg-red-50 p-4">
            <p className="text-red-800">
              Error loading automation data: {(schedulesError || historyError)?.toString()}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Automation</h1>
          <p className="mt-2 text-gray-600">
            Manage scheduled monitoring jobs and view execution history
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg bg-white p-6 shadow">
              <p className="text-sm font-medium text-gray-600">Total Runs</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.total_runs}</p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="mt-2 text-3xl font-bold text-green-600">{stats.completed_runs}</p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="mt-2 text-3xl font-bold text-red-600">{stats.failed_runs}</p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow">
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="mt-2 text-3xl font-bold text-blue-600">{stats.running_runs}</p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('schedules')}
              className={`border-b-2 px-1 pb-4 text-sm font-medium ${
                activeTab === 'schedules'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              Schedules ({schedules?.total || 0})
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`border-b-2 px-1 pb-4 text-sm font-medium ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              Job History ({jobRuns?.total || 0})
            </button>
          </nav>
        </div>

        {/* Schedules Tab */}
        {activeTab === 'schedules' && (
          <div>
            {/* Create Schedule Button */}
            <div className="mb-6 flex justify-between items-center">
              <div className="flex gap-4">
                <select
                  value={scheduleFilters.is_active?.toString() || ''}
                  onChange={(e) =>
                    setScheduleFilters((prev) => ({
                      ...prev,
                      is_active: e.target.value === '' ? undefined : e.target.value === 'true',
                    }))
                  }
                  className="rounded-lg border border-gray-300 px-4 py-2"
                >
                  <option value="">All Statuses</option>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
                <select
                  value={scheduleFilters.schedule_type || ''}
                  onChange={(e) =>
                    setScheduleFilters((prev) => ({
                      ...prev,
                      schedule_type: e.target.value as ScheduleType || undefined,
                    }))
                  }
                  className="rounded-lg border border-gray-300 px-4 py-2"
                >
                  <option value="">All Types</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="custom">Custom Cron</option>
                </select>
              </div>
              <button
                onClick={() => setShowScheduleModal(true)}
                className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Create Schedule
              </button>
            </div>

            {/* Schedules Table */}
            <div className="rounded-lg bg-white shadow">
              {schedulesLoading ? (
                <div className="p-8 text-center">
                  <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                  <p className="mt-2 text-gray-600">Loading schedules...</p>
                </div>
              ) : schedules && schedules.items.length > 0 ? (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Name
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Schedule
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Next Run
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Last Run
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {schedules.items.map((schedule) => (
                          <tr key={schedule.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4">
                              <div className="text-sm font-medium text-gray-900">{schedule.name}</div>
                              {schedule.description && (
                                <div className="text-sm text-gray-500">{schedule.description}</div>
                              )}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">{schedule.job_type}</td>
                            <td className="px-6 py-4">
                              <span className="inline-flex rounded-full bg-gray-100 px-2 py-1 text-xs font-semibold text-gray-800">
                                {formatScheduleType(schedule.schedule_type)}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                                  schedule.is_active
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {schedule.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {formatNextRun(schedule.next_run_at)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {schedule.last_run_at
                                ? new Date(schedule.last_run_at).toLocaleString()
                                : 'Never'}
                            </td>
                            <td className="px-6 py-4 text-right text-sm font-medium">
                              <div className="flex justify-end gap-2">
                                <button
                                  onClick={() => triggerScheduleMutation.mutate(schedule.id)}
                                  className="text-blue-600 hover:text-blue-900"
                                  title="Run now"
                                >
                                  ▶
                                </button>
                                <button
                                  onClick={() => handleToggleActive(schedule)}
                                  className={`${
                                    schedule.is_active
                                      ? 'text-yellow-600 hover:text-yellow-900'
                                      : 'text-green-600 hover:text-green-900'
                                  }`}
                                  title={schedule.is_active ? 'Deactivate' : 'Activate'}
                                >
                                  {schedule.is_active ? '⏸' : '▶'}
                                </button>
                                <button
                                  onClick={() => {
                                    setEditingSchedule(schedule);
                                    setShowScheduleModal(true);
                                  }}
                                  className="text-gray-600 hover:text-gray-900"
                                  title="Edit"
                                >
                                  ✎
                                </button>
                                <button
                                  onClick={() => {
                                    if (confirm('Delete this schedule?')) {
                                      deleteScheduleMutation.mutate(schedule.id);
                                    }
                                  }}
                                  className="text-red-600 hover:text-red-900"
                                  title="Delete"
                                >
                                  ×
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  {schedules.total_pages > 1 && (
                    <div className="border-t border-gray-200 px-6 py-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-700">
                          Showing {schedules.items.length} of {schedules.total} schedules
                        </p>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSchedulePageChange(schedules.page - 1)}
                            disabled={schedules.page === 1}
                            className="rounded-lg border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
                          >
                            Previous
                          </button>
                          <span className="px-3 py-1 text-sm">
                            Page {schedules.page} of {schedules.total_pages}
                          </span>
                          <button
                            onClick={() => handleSchedulePageChange(schedules.page + 1)}
                            disabled={schedules.page === schedules.total_pages}
                            className="rounded-lg border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-8 text-center">
                  <p className="text-gray-500">No schedules found. Create one to get started!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Job History Tab */}
        {activeTab === 'history' && (
          <div>
            {/* Manual Event Search Section */}
            <div className="mb-6 rounded-lg bg-white p-6 shadow">
              <h2 className="mb-4 text-lg font-semibold">Manual Event Search</h2>
              <p className="mb-4 text-sm text-gray-600">
                Search configured APIs for client events. Select specific clients or leave empty to search all active clients.
              </p>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Clients (optional)
                  </label>
                  <select
                    multiple
                    value={selectedClientIds}
                    onChange={(e) => {
                      const options = Array.from(e.target.selectedOptions);
                      setSelectedClientIds(options.map(opt => opt.value));
                    }}
                    className="h-32 w-full rounded-lg border border-gray-300 px-3 py-2"
                    disabled={triggerEventSearchMutation.isPending}
                  >
                    <option value="">All Active Clients</option>
                    {clients?.items?.map((client: any) => (
                      <option key={client.id} value={client.id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">Hold Ctrl/Cmd to select multiple</p>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Time Period (days back)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={daysBack}
                    onChange={(e) => setDaysBack(parseInt(e.target.value))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    disabled={triggerEventSearchMutation.isPending}
                  />
                  <p className="mt-1 text-xs text-gray-500">1-90 days (default: 21)</p>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Max Results Per API
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    disabled={triggerEventSearchMutation.isPending}
                  />
                  <p className="mt-1 text-xs text-gray-500">1-100 results (default: 10)</p>
                </div>
                <div className="flex items-end">
                  <button
                    onClick={handleTriggerEventSearch}
                    disabled={triggerEventSearchMutation.isPending}
                    className="w-full rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {triggerEventSearchMutation.isPending ? 'Searching...' : 'Search for Events'}
                  </button>
                </div>
              </div>
            </div>

            {/* Job History Table */}
            <div className="rounded-lg bg-white shadow">
              {historyLoading ? (
                <div className="p-8 text-center">
                  <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                  <p className="mt-2 text-gray-600">Loading job history...</p>
                </div>
              ) : jobRuns && jobRuns.items.length > 0 ? (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Job Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Started
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Duration
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Events
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                            Clients
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {jobRuns.items.map((job) => (
                          <tr key={job.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">
                              {job.job_type}
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(
                                  job.status
                                )}`}
                              >
                                {job.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {new Date(job.started_at).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {formatDuration(job.duration_seconds)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {job.events_found} ({job.events_new} new)
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {job.clients_processed}
                            </td>
                            <td className="px-6 py-4 text-right text-sm font-medium">
                              <button
                                onClick={() => {
                                  if (confirm('Delete this job run?')) {
                                    deleteJobMutation.mutate(parseInt(job.id));
                                  }
                                }}
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

                  {/* Pagination */}
                  {jobRuns.total_pages > 1 && (
                    <div className="border-t border-gray-200 px-6 py-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-700">
                          Showing {jobRuns.items.length} of {jobRuns.total} jobs
                        </p>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleHistoryPageChange(jobRuns.page - 1)}
                            disabled={jobRuns.page === 1}
                            className="rounded-lg border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
                          >
                            Previous
                          </button>
                          <span className="px-3 py-1 text-sm">
                            Page {jobRuns.page} of {jobRuns.total_pages}
                          </span>
                          <button
                            onClick={() => handleHistoryPageChange(jobRuns.page + 1)}
                            disabled={jobRuns.page === jobRuns.total_pages}
                            className="rounded-lg border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-8 text-center">
                  <p className="text-gray-500">No job history found.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Schedule Modal */}
        {showScheduleModal && (
          <ScheduleModal
            schedule={editingSchedule}
            jobTypes={[]}
            onClose={() => {
              setShowScheduleModal(false);
              setEditingSchedule(null);
            }}
            onSave={(data) => {
              if (editingSchedule) {
                updateScheduleMutation.mutate({ id: editingSchedule.id, data });
              } else {
                createScheduleMutation.mutate(data);
              }
            }}
          />
        )}
      </div>
    </div>
  );
}

// Schedule Modal Component
interface ScheduleModalProps {
  schedule: AutomationSchedule | null;
  jobTypes: string[];
  onClose: () => void;
  onSave: (data: ScheduleCreate) => void;
}

function ScheduleModal({ schedule, jobTypes, onClose, onSave }: ScheduleModalProps) {
  const [formData, setFormData] = useState<ScheduleCreate>({
    name: schedule?.name || '',
    description: schedule?.description || '',
    job_type: schedule?.job_type || 'client_monitoring',
    schedule_type: schedule?.schedule_type || 'daily',
    schedule_config: schedule?.schedule_config || { hour_of_day: 9 },
    client_ids: schedule?.client_ids || null,
    is_active: schedule?.is_active ?? true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6">
        <h2 className="mb-4 text-2xl font-bold">
          {schedule ? 'Edit Schedule' : 'Create Schedule'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Job Type</label>
            <select
              value={formData.job_type}
              onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
              className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              required
            >
              {jobTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Schedule Type</label>
            <select
              value={formData.schedule_type}
              onChange={(e) =>
                setFormData({ ...formData, schedule_type: e.target.value as ScheduleType })
              }
              className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              required
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="custom">Custom Cron</option>
            </select>
          </div>

          {/* Schedule Config based on type */}
          {formData.schedule_type === 'hourly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Minute of Hour (0-59)
              </label>
              <input
                type="number"
                min="0"
                max="59"
                value={formData.schedule_config.minute_of_hour || 0}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    schedule_config: { minute_of_hour: parseInt(e.target.value) },
                  })
                }
                className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              />
            </div>
          )}

          {formData.schedule_type === 'daily' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Hour of Day (0-23)</label>
              <input
                type="number"
                min="0"
                max="23"
                value={formData.schedule_config.hour_of_day || 9}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    schedule_config: { hour_of_day: parseInt(e.target.value) },
                  })
                }
                className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
              />
            </div>
          )}

          {formData.schedule_type === 'weekly' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Day of Week (0=Monday, 6=Sunday)
                </label>
                <input
                  type="number"
                  min="0"
                  max="6"
                  value={formData.schedule_config.day_of_week || 0}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      schedule_config: {
                        ...formData.schedule_config,
                        day_of_week: parseInt(e.target.value),
                      },
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Hour of Day (0-23)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={formData.schedule_config.hour_of_day || 9}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      schedule_config: {
                        ...formData.schedule_config,
                        hour_of_day: parseInt(e.target.value),
                      },
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>
            </>
          )}

          {formData.schedule_type === 'monthly' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Day of Month (1-31)
                </label>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={formData.schedule_config.day_of_month || 1}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      schedule_config: {
                        ...formData.schedule_config,
                        day_of_month: parseInt(e.target.value),
                      },
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Hour of Day (0-23)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={formData.schedule_config.hour_of_day || 9}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      schedule_config: {
                        ...formData.schedule_config,
                        hour_of_day: parseInt(e.target.value),
                      },
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>
            </>
          )}

          {formData.schedule_type === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Cron Expression
              </label>
              <input
                type="text"
                value={formData.schedule_config.cron_expression || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    schedule_config: { cron_expression: e.target.value },
                  })
                }
                className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2"
                placeholder="0 9 * * *"
              />
              <p className="mt-1 text-xs text-gray-500">
                Format: minute hour day month day_of_week
              </p>
            </div>
          )}

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700">Active</span>
            </label>
          </div>

          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              {schedule ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
