/**
 * API Configuration Service
 * Handles API configuration management for businesses
 */

import { apiClient } from './api';

export interface APIProvider {
  provider: string;
  display_name: string;
  description: string;
  requires_secret: boolean;
  requires_oauth: boolean;
  documentation_url?: string;
}

export interface APIConfig {
  id: string;
  business_id: string;
  provider: string;
  provider_name: string;
  max_tokens_per_month?: number;
  tokens_used_current_month: number;
  rate_limit_per_hour?: number;
  requests_this_hour: number;
  cost_per_1k_tokens?: number;
  estimated_monthly_cost?: number;
  is_active: boolean;
  last_tested_at?: string;
  last_test_status?: string;
  last_test_message?: string;
  api_key_masked?: string;
  has_secret: boolean;
  has_access_token: boolean;
  has_refresh_token: boolean;
  created_at: string;
  updated_at: string;
}

export interface APIConfigCreate {
  business_id: string;
  provider: string;
  provider_name: string;
  api_key?: string;
  api_secret?: string;
  access_token?: string;
  refresh_token?: string;
  max_tokens_per_month?: number;
  rate_limit_per_hour?: number;
  cost_per_1k_tokens?: number;
  is_active?: boolean;
  config_data?: string;
}

export interface APIConfigUpdate {
  provider_name?: string;
  api_key?: string;
  api_secret?: string;
  access_token?: string;
  refresh_token?: string;
  max_tokens_per_month?: number;
  rate_limit_per_hour?: number;
  cost_per_1k_tokens?: number;
  is_active?: boolean;
  config_data?: string;
}

export interface APITestResult {
  success: boolean;
  status: string;
  message: string;
  response_time_ms?: number;
  tested_at: string;
}

export interface APIUsageStats {
  config_id: string;
  provider: string;
  tokens_used_current_month: number;
  max_tokens_per_month?: number;
  requests_this_hour: number;
  rate_limit_per_hour?: number;
  estimated_monthly_cost?: number;
  usage_percentage?: number;
}

/**
 * Get list of available API providers
 */
export const getAvailableProviders = async (): Promise<APIProvider[]> => {
  const response = await apiClient.get('/api/v1/api-configs/providers');
  return response.data;
};

/**
 * Get all API configurations for a business
 */
export const getAPIConfigs = async (
  businessId: string,
  provider?: string,
  isActive?: boolean
): Promise<APIConfig[]> => {
  const params: any = { business_id: businessId };
  if (provider) params.provider = provider;
  if (isActive !== undefined) params.is_active = isActive;

  const response = await apiClient.get('/api/v1/api-configs', { params });
  return response.data;
};

/**
 * Get a specific API configuration
 */
export const getAPIConfig = async (
  configId: string,
  businessId: string
): Promise<APIConfig> => {
  const response = await apiClient.get(`/api/v1/api-configs/${configId}`, {
    params: { business_id: businessId }
  });
  return response.data;
};

/**
 * Create a new API configuration
 */
export const createAPIConfig = async (
  config: APIConfigCreate
): Promise<APIConfig> => {
  const response = await apiClient.post('/api/v1/api-configs', config);
  return response.data;
};

/**
 * Update an existing API configuration
 */
export const updateAPIConfig = async (
  configId: string,
  businessId: string,
  update: APIConfigUpdate
): Promise<APIConfig> => {
  const response = await apiClient.put(`/api/v1/api-configs/${configId}`, update, {
    params: { business_id: businessId }
  });
  return response.data;
};

/**
 * Delete an API configuration
 */
export const deleteAPIConfig = async (
  configId: string,
  businessId: string
): Promise<void> => {
  await apiClient.delete(`/api/v1/api-configs/${configId}`, {
    params: { business_id: businessId }
  });
};

/**
 * Test API connection
 */
export const testAPIConnection = async (
  configId: string,
  businessId: string
): Promise<APITestResult> => {
  const response = await apiClient.post(`/api/v1/api-configs/${configId}/test`, null, {
    params: { business_id: businessId }
  });
  return response.data;
};

/**
 * Get usage statistics for all API configurations
 */
export const getUsageStats = async (
  businessId: string
): Promise<APIUsageStats[]> => {
  const response = await apiClient.get('/api/v1/api-configs/usage/stats', {
    params: { business_id: businessId }
  });
  return response.data;
};

/**
 * Record API usage (internal)
 */
export const recordAPIUsage = async (
  configId: string,
  businessId: string,
  tokensUsed: number = 1
): Promise<void> => {
  await apiClient.post(`/api/v1/api-configs/${configId}/usage`, null, {
    params: { business_id: businessId, tokens_used: tokensUsed }
  });
};

/**
 * Reset monthly usage counters
 */
export const resetMonthlyUsage = async (
  businessId: string
): Promise<{ message: string }> => {
  const response = await apiClient.post('/api/v1/api-configs/usage/reset/monthly', null, {
    params: { business_id: businessId }
  });
  return response.data;
};

/**
 * Reset hourly usage counters
 */
export const resetHourlyUsage = async (
  businessId: string
): Promise<{ message: string }> => {
  const response = await apiClient.post('/api/v1/api-configs/usage/reset/hourly', null, {
    params: { business_id: businessId }
  });
  return response.data;
};
