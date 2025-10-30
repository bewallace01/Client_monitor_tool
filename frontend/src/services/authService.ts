/**
 * Authentication Service - Handles user authentication
 */

import { apiClient } from './api';

export interface User {
  id: number;
  username: string;
  email: string;
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

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export const authService = {
  /**
   * Login user and get access token
   */
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await apiClient.post<AuthToken>('/api/v1/auth/login', credentials);
    return response.data;
  },

  /**
   * Register new user
   */
  async register(userData: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/api/v1/auth/register', userData);
    return response.data;
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  /**
   * Update current user
   */
  async updateCurrentUser(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/api/v1/auth/me', userData);
    return response.data;
  },

  /**
   * Change password
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/api/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } finally {
      // Always remove token from localStorage, even if API call fails
      localStorage.removeItem('auth_token');
    }
  },

  /**
   * Store auth token in localStorage
   */
  setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  },

  /**
   * Get auth token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  /**
   * Remove auth token from localStorage
   */
  removeToken(): void {
    localStorage.removeItem('auth_token');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};

export default authService;
