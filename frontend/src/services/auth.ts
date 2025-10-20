import { httpClient, ApiResponse } from './httpClient';
import { API_CONFIG } from './config';
import { User, UserRole } from '@/types';

// Login request interface
export interface LoginRequest {
  username: string;
  password: string;
}

// Login response interface
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  refresh_token?: string;  // Make optional since backend may not provide it
}

// Auth API service
export const authAPI = {
  // Login user
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    try {
      console.log('Attempting login with:', { username: credentials.username });
      
      console.log('Sending request to:', `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.auth.login}`);
      
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.auth.login}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password
        }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
        console.error('Login error response:', errorData);
        throw new Error(errorData.detail || errorData.message || 'Login failed');
      }

      const data = await response.json();
      console.log('Login success:', { user: data.user_info, hasToken: !!data.access_token });
      
      // Store tokens in localStorage
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token || '');
        localStorage.setItem('user', JSON.stringify(data.user_info));
      }
      
      return {
        data: {
          ...data,
          user: data.user_info  // Map user_info to user for frontend compatibility
        },
        success: true,
        status: response.status,
        message: 'Login successful'
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Logout user
  async logout(): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.post<void>(API_CONFIG.ENDPOINTS.auth.logout);
      
      // Clear tokens from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      return response;
    } catch (error) {
      // Clear tokens even if logout fails on server
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      throw error;
    }
  },

  // Refresh token
  async refreshToken(): Promise<ApiResponse<{ access_token: string; expires_in: number }>> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await httpClient.post<{ access_token: string; expires_in: number }>(
        API_CONFIG.ENDPOINTS.auth.refresh,
        { refresh_token: refreshToken }
      );

      // Update access token
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }

      return response;
    } catch (error) {
      // Clear tokens if refresh fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      throw error;
    }
  },

  // Get current user
  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      return await httpClient.get<User>(API_CONFIG.ENDPOINTS.auth.me);
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    return !!(token && user);
  },

  // Get stored user data
  getStoredUser(): User | null {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Error parsing stored user:', error);
      return null;
    }
  },

  // Demo login function for development
  async demoLogin(role: UserRole = UserRole.ADMIN): Promise<ApiResponse<LoginResponse>> {
    // Real demo credentials that exist in backend
    const demoCredentials: Record<UserRole, LoginRequest> = {
      [UserRole.ADMIN]: { username: 'admin', password: 'admin123' },
      [UserRole.JUDGE]: { username: 'judge1', password: 'demo123' },
      [UserRole.CLERK]: { username: 'clerk1', password: 'demo123' },
      [UserRole.LAWYER]: { username: 'lawyer1', password: 'demo123' },
      [UserRole.PUBLIC]: { username: 'lawyer1', password: 'demo123' }, // Using lawyer1 as fallback
    };

    // Use actual login instead of mock data
    return await this.login(demoCredentials[role]);
  },
};
