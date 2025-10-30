/**
 * Clients API Service
 * Handles all client-related API calls
 */

import { apiClient } from './api';

export interface Client {
  id: string; // UUID
  business_id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  description: string | null;
  company_size: string | null;
  revenue_range: string | null;
  headquarters_location: string | null;
  founded_year: number | null;
  search_keywords: string | null;
  monitoring_frequency: string;
  is_active: boolean;
  assigned_to_user_id: number | null;
  created_by_user_id: number | null;
  tier: string | null;
  health_score: number | null;
  notes: string | null;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  last_checked_at: string | null;
  deleted_at: string | null;
}

export interface ClientCreate {
  name: string;
  domain?: string | null;
  industry?: string | null;
  description?: string | null;
  company_size?: string | null;
  revenue_range?: string | null;
  headquarters_location?: string | null;
  founded_year?: number | null;
  search_keywords?: string | null;
  monitoring_frequency?: string;
  is_active?: boolean;
  assigned_to_user_id?: number | null;
  tier?: string | null;
  health_score?: number | null;
  notes?: string | null;
}

export interface ClientUpdate {
  name?: string;
  domain?: string | null;
  industry?: string | null;
  description?: string | null;
  search_keywords?: string | null;
  is_active?: boolean;
  account_owner?: string | null;
  tier?: string | null;
  notes?: string | null;
}

export interface ClientListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Client[];
}

export interface ClientsFilters {
  skip?: number;
  limit?: number;
  search?: string;
  industry?: string;
  is_active?: boolean;
  tier?: string;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface ClientStats {
  total_clients: number;
  active_clients: number;
  inactive_clients: number;
  clients_by_tier: Record<string, number>;
  clients_by_industry: Record<string, number>;
}

/**
 * Get paginated list of clients with optional filters
 */
export async function getClients(filters?: ClientsFilters): Promise<ClientListResponse> {
  const response = await apiClient.get<ClientListResponse>('/api/v1/clients', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single client by ID
 */
export async function getClient(clientId: string): Promise<Client> {
  const response = await apiClient.get<Client>(`/api/v1/clients/${clientId}`);
  return response.data;
}

/**
 * Create a new client
 */
export async function createClient(client: ClientCreate): Promise<Client> {
  const response = await apiClient.post<Client>('/api/v1/clients', client);
  return response.data;
}

/**
 * Update an existing client
 */
export async function updateClient(clientId: string, updates: ClientUpdate): Promise<Client> {
  const response = await apiClient.put<Client>(`/api/v1/clients/${clientId}`, updates);
  return response.data;
}

/**
 * Delete a client
 */
export async function deleteClient(clientId: string): Promise<void> {
  await apiClient.delete(`/api/v1/clients/${clientId}`);
}

/**
 * Get client statistics
 */
export async function getClientStats(): Promise<ClientStats> {
  const response = await apiClient.get<ClientStats>('/api/v1/clients/stats');
  return response.data;
}

/**
 * Get list of all industries
 */
export async function getIndustries(): Promise<string[]> {
  const response = await apiClient.get<string[]>('/api/v1/clients/industries');
  return response.data;
}

/**
 * Get list of all tiers
 */
export async function getTiers(): Promise<string[]> {
  const response = await apiClient.get<string[]>('/api/v1/clients/tiers');
  return response.data;
}
