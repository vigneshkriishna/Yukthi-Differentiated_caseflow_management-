import { API_CONFIG } from './config';

// Response wrapper type
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
  status: number;
}

// Error response type
export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// HTTP client class with authentication support
class HttpClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    const headers = { ...this.defaultHeaders, ...customHeaders };
    const token = this.getAuthToken();
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const isJson = response.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const error: ApiError = {
        message: data.message || data.detail || 'An error occurred',
        status: response.status,
        details: data,
      };
      throw error;
    }

    return {
      data,
      success: true,
      status: response.status,
      message: data.message,
    };
  }

  async get<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'GET',
      headers: this.getHeaders(),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(url: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async put<T>(url: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async patch<T>(url: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  // File upload method
  async upload<T>(url: string, formData: FormData, options?: RequestInit): Promise<ApiResponse<T>> {
    const headers = this.getHeaders();
    // Remove Content-Type for FormData (browser will set it with boundary)
    delete headers['Content-Type'];

    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers,
      body: formData,
      ...options,
    });

    return this.handleResponse<T>(response);
  }
}

export const httpClient = new HttpClient();
