import axios from 'axios';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: any) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

export const competitorsAPI = {
  list: () => api.get('/competitors'),
  get: (id: string) => api.get(`/competitors/${id}`),
  create: (data: any) => api.post('/competitors', data),
  update: (id: string, data: any) => api.put(`/competitors/${id}`, data),
  delete: (id: string) => api.delete(`/competitors/${id}`),
};

export const marketAPI = {
  trends: () => api.get('/market/trends'),
  forecast: () => api.get('/market/forecast'),
  insights: () => api.get('/market/insights'),
};

export const newsAPI = {
  list: () => api.get('/news'),
  get: (id: string) => api.get(`/news/${id}`),
  search: (query: string) => api.get(`/news/search?q=${query}`),
};

export const alertsAPI = {
  list: () => api.get('/alerts'),
  create: (data: any) => api.post('/alerts', data),
  update: (id: string, data: any) => api.put(`/alerts/${id}`, data),
  delete: (id: string) => api.delete(`/alerts/${id}`),
  markRead: (id: string) => api.put(`/alerts/${id}/read`),
};

export const reportsAPI = {
  list: () => api.get('/reports'),
  generate: (data: any) => api.post('/reports/generate', data),
  download: (id: string) => api.get(`/reports/${id}/download`, { responseType: 'blob' }),
};

export const analyticsAPI = {
  competitorAnalysis: (competitorId: string) =>
    api.get(`/analytics/competitor/${competitorId}`),
  marketAnalysis: () => api.get('/analytics/market'),
  predictions: () => api.get('/analytics/predictions'),
  insights: () => api.get('/analytics/insights'),
};

export default api;