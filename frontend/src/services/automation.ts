/**
 * Automation/Scheduler API Service
 * Handles all job management and scheduler-related API calls
 */

import { apiClient } from './api';

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface JobRun {
  id: string; // UUID
  job_id: string;
  job_type: string;
  started_at: string;
  completed_at: string | null;
  status: JobStatus;
  events_found: number;
  events_new: number;
  clients_processed: number;
  error_message: string | null;
  job_metadata: string | null;
  duration_seconds: number | null;
}

export interface JobRunListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: JobRun[];
}

export interface JobRunStats {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  running_runs: number;
  pending_runs: number;
  average_duration_seconds: number | null;
  runs_by_job_type: Record<string, number>;
  recent_runs: JobRun[];
}

export interface JobRunFilters {
  skip?: number;
  limit?: number;
  job_type?: string;
  status?: JobStatus;
  start_date?: string;
  end_date?: string;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface TriggerJobRequest {
  job_type: string;
  override_params?: Record<string, any>;
}

/**
 * Get paginated list of job runs with optional filters
 */
export async function getJobRuns(filters?: JobRunFilters): Promise<JobRunListResponse> {
  const response = await apiClient.get<JobRunListResponse>('/api/v1/scheduler/jobs', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single job run by ID
 */
export async function getJobRun(jobRunId: string): Promise<JobRun> {
  const response = await apiClient.get<JobRun>(`/api/v1/scheduler/jobs/${jobRunId}`);
  return response.data;
}

/**
 * Get job run statistics
 */
export async function getJobRunStats(): Promise<JobRunStats> {
  const response = await apiClient.get<JobRunStats>('/api/v1/scheduler/jobs/stats');
  return response.data;
}

/**
 * Get recent job runs
 */
export async function getRecentJobRuns(limit: number = 10): Promise<JobRun[]> {
  const response = await apiClient.get<JobRun[]>('/api/v1/scheduler/jobs/recent', {
    params: { limit },
  });
  return response.data;
}

/**
 * Get currently active (pending or running) job runs
 */
export async function getActiveJobRuns(): Promise<JobRun[]> {
  const response = await apiClient.get<JobRun[]>('/api/v1/scheduler/jobs/active');
  return response.data;
}

/**
 * Get list of all job types
 */
export async function getJobTypes(): Promise<string[]> {
  const response = await apiClient.get<string[]>('/api/v1/scheduler/jobs/types');
  return response.data;
}

/**
 * Manually trigger a new job run
 */
export async function triggerJob(request: TriggerJobRequest): Promise<JobRun> {
  const response = await apiClient.post<JobRun>('/api/v1/scheduler/jobs/trigger', request);
  return response.data;
}

/**
 * Delete a job run
 */
export async function deleteJobRun(jobRunId: number): Promise<void> {
  await apiClient.delete(`/api/v1/scheduler/jobs/${jobRunId}`);
}

/**
 * Mark a job as running
 */
export async function startJob(jobRunId: number): Promise<JobRun> {
  const response = await apiClient.post<JobRun>(`/api/v1/scheduler/jobs/${jobRunId}/start`);
  return response.data;
}

/**
 * Mark a job as completed
 */
export async function completeJob(
  jobRunId: number,
  eventsFound: number,
  eventsNew: number,
  clientsProcessed: number
): Promise<JobRun> {
  const response = await apiClient.post<JobRun>(
    `/api/v1/scheduler/jobs/${jobRunId}/complete`,
    null,
    {
      params: {
        events_found: eventsFound,
        events_new: eventsNew,
        clients_processed: clientsProcessed,
      },
    }
  );
  return response.data;
}

/**
 * Mark a job as failed
 */
export async function failJob(jobRunId: number, errorMessage: string): Promise<JobRun> {
  const response = await apiClient.post<JobRun>(
    `/api/v1/scheduler/jobs/${jobRunId}/fail`,
    null,
    {
      params: {
        error_message: errorMessage,
      },
    }
  );
  return response.data;
}

// ============================================================================
// AUTOMATION SCHEDULES
// ============================================================================

export type ScheduleType = 'manual' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'custom';

export interface AutomationSchedule {
  id: string; // UUID
  business_id: string;
  name: string;
  description: string | null;
  job_type: string;
  schedule_type: ScheduleType;
  schedule_config: Record<string, any>;
  is_active: boolean;
  client_ids: string[] | null;
  last_run_at: string | null;
  next_run_at: string | null;
  consecutive_failures: number;
  last_error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduleListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: AutomationSchedule[];
}

export interface ScheduleFilters {
  skip?: number;
  limit?: number;
  job_type?: string;
  is_active?: boolean;
  schedule_type?: ScheduleType;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface ScheduleCreate {
  name: string;
  description?: string | null;
  job_type: string;
  schedule_type: ScheduleType;
  schedule_config: Record<string, any>;
  client_ids?: string[] | null;
  is_active?: boolean;
}

export interface ScheduleUpdate {
  name?: string;
  description?: string | null;
  schedule_type?: ScheduleType;
  schedule_config?: Record<string, any>;
  client_ids?: string[] | null;
  is_active?: boolean;
}

/**
 * Get paginated list of automation schedules with optional filters
 */
export async function getSchedules(filters?: ScheduleFilters): Promise<ScheduleListResponse> {
  const response = await apiClient.get<ScheduleListResponse>('/api/v1/automation-schedules/', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single automation schedule by ID
 */
export async function getSchedule(scheduleId: string): Promise<AutomationSchedule> {
  const response = await apiClient.get<AutomationSchedule>(`/api/v1/automation-schedules/${scheduleId}`);
  return response.data;
}

/**
 * Create a new automation schedule
 */
export async function createSchedule(data: ScheduleCreate): Promise<AutomationSchedule> {
  const response = await apiClient.post<AutomationSchedule>('/api/v1/automation-schedules/', data);
  return response.data;
}

/**
 * Update an existing automation schedule
 */
export async function updateSchedule(scheduleId: string, data: ScheduleUpdate): Promise<AutomationSchedule> {
  const response = await apiClient.put<AutomationSchedule>(`/api/v1/automation-schedules/${scheduleId}`, data);
  return response.data;
}

/**
 * Delete an automation schedule
 */
export async function deleteSchedule(scheduleId: string): Promise<void> {
  await apiClient.delete(`/api/v1/automation-schedules/${scheduleId}`);
}

/**
 * Activate an automation schedule
 */
export async function activateSchedule(scheduleId: string): Promise<AutomationSchedule> {
  const response = await apiClient.post<AutomationSchedule>(`/api/v1/automation-schedules/${scheduleId}/activate`);
  return response.data;
}

/**
 * Deactivate an automation schedule
 */
export async function deactivateSchedule(scheduleId: string): Promise<AutomationSchedule> {
  const response = await apiClient.post<AutomationSchedule>(`/api/v1/automation-schedules/${scheduleId}/deactivate`);
  return response.data;
}

/**
 * Manually trigger a scheduled job (runs once immediately)
 */
export async function triggerSchedule(scheduleId: string): Promise<JobRun> {
  const response = await apiClient.post<JobRun>(`/api/v1/automation-schedules/${scheduleId}/trigger`);
  return response.data;
}

/**
 * Bulk activate multiple schedules
 */
export async function bulkActivateSchedules(scheduleIds: string[]): Promise<{ updated: number }> {
  const response = await apiClient.post<{ updated: number }>('/api/v1/automation-schedules/bulk/activate', {
    schedule_ids: scheduleIds,
  });
  return response.data;
}

/**
 * Bulk deactivate multiple schedules
 */
export async function bulkDeactivateSchedules(scheduleIds: string[]): Promise<{ updated: number }> {
  const response = await apiClient.post<{ updated: number }>('/api/v1/automation-schedules/bulk/deactivate', {
    schedule_ids: scheduleIds,
  });
  return response.data;
}

/**
 * Bulk delete multiple schedules
 */
export async function bulkDeleteSchedules(scheduleIds: string[]): Promise<{ deleted: number }> {
  const response = await apiClient.post<{ deleted: number }>('/api/v1/automation-schedules/bulk/delete', {
    schedule_ids: scheduleIds,
  });
  return response.data;
}

// Manual Event Search (Monitoring Jobs)

export interface ManualEventSearchRequest {
  client_ids?: string[] | null;
  days_back?: number;
  max_results_per_source?: number;
  force_mock?: boolean;
}

export interface ManualEventSearchResponse {
  success: boolean;
  job_run_id: string;
  clients_processed: number;
  events_found: number;
  events_new: number;
  notifications_sent: number;
  duration_seconds: number;
  error?: string;
}

/**
 * Trigger a manual event search job
 * This searches configured APIs for client events within the specified time range
 */
export async function triggerManualEventSearch(request: ManualEventSearchRequest): Promise<ManualEventSearchResponse> {
  const response = await apiClient.post<ManualEventSearchResponse>('/api/v1/monitoring-jobs/execute', request);
  return response.data;
}
