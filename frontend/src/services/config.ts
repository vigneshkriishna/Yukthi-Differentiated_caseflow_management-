// API Configuration for DCM System
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    auth: {
      login: '/auth/login',
      logout: '/auth/logout',
      refresh: '/auth/refresh',
      me: '/auth/me',
    },
    cases: {
      list: '/api/cases',
      create: '/api/cases',
      get: (id: string) => `/api/cases/${id}`,
      update: (id: string) => `/api/cases/${id}`,
      delete: (id: string) => `/api/cases/${id}`,
      search: '/api/cases/search',
    },
    hearings: {
      list: '/api/hearings',
      create: '/api/hearings',
      get: (id: string) => `/api/hearings/${id}`,
      update: (id: string) => `/api/hearings/${id}`,
      delete: (id: string) => `/api/hearings/${id}`,
      upcoming: '/api/hearings/upcoming',
    },
    users: {
      list: '/api/users',
      create: '/api/users',
      get: (id: string) => `/api/users/${id}`,
      update: (id: string) => `/api/users/${id}`,
      delete: (id: string) => `/api/users/${id}`,
    },
    documents: {
      list: '/api/documents',
      upload: '/api/documents/upload',
      download: (id: string) => `/api/documents/${id}/download`,
      delete: (id: string) => `/api/documents/${id}`,
    },
    reports: {
      dashboard: '/reports/dashboard',
      metrics: '/reports/metrics',
      caseStatistics: '/reports/case-statistics',
      exportCauseList: '/reports/export/cause-list',
    },
    nlp: {
      classify: '/nlp/classify-bns',
      batch: '/nlp/classify-batch',
      status: '/nlp/model-status',
      sections: '/nlp/supported-sections',
    },
  },
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
} as const;

export type ApiEndpoint = typeof API_CONFIG.ENDPOINTS;
