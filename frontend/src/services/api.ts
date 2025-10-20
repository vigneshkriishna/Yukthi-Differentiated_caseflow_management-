// Main API exports
export { httpClient } from './httpClient';
export { authAPI } from './auth';
export { API_CONFIG } from './config';

// Re-export types
export type { ApiResponse, ApiError } from './httpClient';
export type { LoginRequest, LoginResponse } from './auth';

// Cases API service
import { httpClient } from './httpClient';
import { API_CONFIG } from './config';
import type { Case, CaseFilters, CreateCaseRequest, UpdateCaseRequest, User } from '@/types';

export const casesAPI = {
  async getAll(filters?: CaseFilters) {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    const url = queryString ? `${API_CONFIG.ENDPOINTS.cases.list}?${queryString}` : API_CONFIG.ENDPOINTS.cases.list;
    return httpClient.get<Case[]>(url);
  },

  async getById(id: number) {
    return httpClient.get<Case>(API_CONFIG.ENDPOINTS.cases.get(String(id)));
  },

  async create(data: CreateCaseRequest) {
    return httpClient.post<Case>(API_CONFIG.ENDPOINTS.cases.create, data);
  },

  async update(id: number, data: UpdateCaseRequest) {
    return httpClient.put<Case>(API_CONFIG.ENDPOINTS.cases.update(String(id)), data);
  },

  async delete(id: number) {
    return httpClient.delete<void>(API_CONFIG.ENDPOINTS.cases.delete(String(id)));
  },

  async search(query: string) {
    return httpClient.get<Case[]>(`${API_CONFIG.ENDPOINTS.cases.search}?q=${encodeURIComponent(query)}`);
  },
};

// Hearings API service
import type { Hearing, CreateHearingRequest, UpdateHearingRequest } from '@/types';

export const hearingsAPI = {
  async getAll() {
    return httpClient.get<Hearing[]>(API_CONFIG.ENDPOINTS.hearings.list);
  },

  async getById(id: number) {
    return httpClient.get<Hearing>(API_CONFIG.ENDPOINTS.hearings.get(String(id)));
  },

  async create(data: CreateHearingRequest) {
    return httpClient.post<Hearing>(API_CONFIG.ENDPOINTS.hearings.create, data);
  },

  async update(id: number, data: UpdateHearingRequest) {
    return httpClient.put<Hearing>(API_CONFIG.ENDPOINTS.hearings.update(String(id)), data);
  },

  async delete(id: number) {
    return httpClient.delete<void>(API_CONFIG.ENDPOINTS.hearings.delete(String(id)));
  },

  async getUpcoming() {
    return httpClient.get<Hearing[]>(API_CONFIG.ENDPOINTS.hearings.upcoming);
  },
};

// Users API service
export const usersAPI = {
  async getAll() {
    return httpClient.get<User[]>(API_CONFIG.ENDPOINTS.users.list);
  },

  async getById(id: number) {
    return httpClient.get<User>(API_CONFIG.ENDPOINTS.users.get(String(id)));
  },

  async create(data: Partial<User>) {
    return httpClient.post<User>(API_CONFIG.ENDPOINTS.users.create, data);
  },

  async update(id: number, data: Partial<User>) {
    return httpClient.put<User>(API_CONFIG.ENDPOINTS.users.update(String(id)), data);
  },

  async delete(id: number) {
    return httpClient.delete<void>(API_CONFIG.ENDPOINTS.users.delete(String(id)));
  },
};

// Documents API service
export const documentsAPI = {
  async upload(file: File, caseId?: number) {
    const formData = new FormData();
    formData.append('file', file);
    if (caseId) {
      formData.append('case_id', String(caseId));
    }
    return httpClient.upload(API_CONFIG.ENDPOINTS.documents.upload, formData);
  },

  async download(id: number) {
    return httpClient.get(API_CONFIG.ENDPOINTS.documents.download(String(id)));
  },

  async delete(id: number) {
    return httpClient.delete(API_CONFIG.ENDPOINTS.documents.delete(String(id)));
  },
};

// Reports API service
export const reportsAPI = {
  async getDashboard() {
    return httpClient.get(API_CONFIG.ENDPOINTS.reports.dashboard);
  },

  async getMetrics(filters?: { start_date?: string; end_date?: string }) {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    const url = queryString ? `${API_CONFIG.ENDPOINTS.reports.metrics}?${queryString}` : API_CONFIG.ENDPOINTS.reports.metrics;
    return httpClient.get(url);
  },

  async getCaseStatistics(filters?: { case_type?: string; track?: string }) {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    const url = queryString ? `${API_CONFIG.ENDPOINTS.reports.caseStatistics}?${queryString}` : API_CONFIG.ENDPOINTS.reports.caseStatistics;
    return httpClient.get(url);
  },

  async exportCauseList(date: string, format: 'csv' | 'pdf' = 'csv') {
    const params = new URLSearchParams({ date, format });
    return httpClient.get(`${API_CONFIG.ENDPOINTS.reports.exportCauseList}?${params.toString()}`);
  },
};

// BNS NLP API service
export const nlpAPI = {
  async classifyBNS(caseData: {
    title: string;
    description: string;
    case_type?: string;
    severity?: string;
    evidence?: string;
  }) {
    return httpClient.post(API_CONFIG.ENDPOINTS.nlp.classify, caseData);
  },

  async classifyBatch(cases: Array<{
    title: string;
    description: string;
    case_type?: string;
    severity?: string;
    evidence?: string;
  }>) {
    return httpClient.post(API_CONFIG.ENDPOINTS.nlp.batch, { cases });
  },

  async getModelStatus() {
    return httpClient.get(API_CONFIG.ENDPOINTS.nlp.status);
  },

  async getSupportedSections() {
    return httpClient.get(API_CONFIG.ENDPOINTS.nlp.sections);
  },
};
