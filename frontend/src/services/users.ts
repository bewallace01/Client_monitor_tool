/**
 * Users API Service
 * Handles all user-related API calls
 */

import { apiClient } from './api';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: 'system_admin' | 'business_admin' | 'base_user';
  business_id: string | null;
  is_active: boolean;
  is_superuser: boolean;
  sso_enabled: boolean;
  sso_provider: string | null;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string | null;
  role?: 'system_admin' | 'business_admin' | 'base_user';
  business_id?: string | null;
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string | null;
  password?: string;
  role?: 'system_admin' | 'business_admin' | 'base_user';
  business_id?: string | null;
  is_active?: boolean;
}

export interface UserListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: User[];
}

export interface UsersFilters {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  role?: 'system_admin' | 'business_admin' | 'base_user';
  business_id?: string;
}

/**
 * Get paginated list of users with optional filters
 */
export async function getUsers(filters?: UsersFilters): Promise<UserListResponse> {
  const response = await apiClient.get<UserListResponse>('/api/v1/users', {
    params: filters,
  });
  return response.data;
}

/**
 * Get a single user by ID
 */
export async function getUser(userId: number): Promise<User> {
  const response = await apiClient.get<User>(`/api/v1/users/${userId}`);
  return response.data;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/api/v1/users/me');
  return response.data;
}

/**
 * Create a new user
 */
export async function createUser(user: UserCreate): Promise<User> {
  const response = await apiClient.post<User>('/api/v1/users', user);
  return response.data;
}

/**
 * Update an existing user
 */
export async function updateUser(userId: number, updates: UserUpdate): Promise<User> {
  const response = await apiClient.put<User>(`/api/v1/users/${userId}`, updates);
  return response.data;
}

/**
 * Delete a user
 */
export async function deleteUser(userId: number): Promise<void> {
  await apiClient.delete(`/api/v1/users/${userId}`);
}

/**
 * Deactivate a user
 */
export async function deactivateUser(userId: number): Promise<User> {
  const response = await apiClient.post<User>(`/api/v1/users/${userId}/deactivate`);
  return response.data;
}

/**
 * Activate a user
 */
export async function activateUser(userId: number): Promise<User> {
  const response = await apiClient.post<User>(`/api/v1/users/${userId}/activate`);
  return response.data;
}

/**
 * Update user role
 */
export async function updateUserRole(userId: number, role: string): Promise<User> {
  const response = await apiClient.put<User>(`/api/v1/users/${userId}/role`, { role });
  return response.data;
}

/**
 * Update user business
 */
export async function updateUserBusiness(userId: number, businessId: string | null): Promise<User> {
  const response = await apiClient.put<User>(`/api/v1/users/${userId}/business`, { business_id: businessId });
  return response.data;
}
