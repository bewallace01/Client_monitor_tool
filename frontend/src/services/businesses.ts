/**
 * Businesses API Service
 * Handles all business-related API calls
 */

import { apiClient } from './api';

export interface Business {
  id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  size: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  address: string | null;
  is_active: boolean;
  subscription_tier: string | null;
  subscription_status: string | null;
  trial_ends_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BusinessCreate {
  name: string;
  domain?: string | null;
  industry?: string | null;
  size?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  is_active?: boolean;
  subscription_tier?: string | null;
  subscription_status?: string | null;
}

export interface BusinessUpdate {
  name?: string;
  domain?: string | null;
  industry?: string | null;
  size?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  is_active?: boolean;
  subscription_tier?: string | null;
  subscription_status?: string | null;
}

export interface BusinessListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Business[];
}

export interface BusinessFilters {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  industry?: string;
  subscription_tier?: string;
  search?: string;
}

/**
 * Get paginated list of businesses with optional filters
 */
export async function getBusinesses(filters?: BusinessFilters): Promise<BusinessListResponse> {
  const response = await apiClient.get<BusinessListResponse>('/api/v1/businesses', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single business by ID
 */
export async function getBusiness(businessId: string): Promise<Business> {
  const response = await apiClient.get<Business>(`/api/v1/businesses/${businessId}`);
  return response.data;
}

/**
 * Create a new business
 */
export async function createBusiness(business: BusinessCreate): Promise<Business> {
  const response = await apiClient.post<Business>('/api/v1/businesses', business);
  return response.data;
}

/**
 * Update an existing business
 */
export async function updateBusiness(businessId: string, updates: BusinessUpdate): Promise<Business> {
  const response = await apiClient.put<Business>(`/api/v1/businesses/${businessId}`, updates);
  return response.data;
}

/**
 * Delete a business
 */
export async function deleteBusiness(businessId: string): Promise<void> {
  await apiClient.delete(`/api/v1/businesses/${businessId}`);
}

/**
 * Deactivate a business
 */
export async function deactivateBusiness(businessId: string): Promise<Business> {
  const response = await apiClient.post<Business>(`/api/v1/businesses/${businessId}/deactivate`);
  return response.data;
}

/**
 * Activate a business
 */
export async function activateBusiness(businessId: string): Promise<Business> {
  const response = await apiClient.post<Business>(`/api/v1/businesses/${businessId}/activate`);
  return response.data;
}
