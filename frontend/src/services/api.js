import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';
const AUTH_API_BASE_URL = import.meta.env.VITE_AUTH_API_BASE_URL || 'http://localhost:8001';
const AI_API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8004';

// Axios instance for backend
export const backendAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios instance for auth
export const authAPI = axios.create({
  baseURL: AUTH_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios instance for AI
export const aiAPI = axios.create({
  baseURL: AI_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
backendAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

authAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

aiAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authService = {
  login: (username, password) => authAPI.post('/api/auth/login', { username, password }),
  register: (data) => authAPI.post('/api/auth/register', data),
  me: () => authAPI.get('/api/auth/me'),
  logout: () => authAPI.post('/api/auth/logout'),
};

// Drops API
export const dropsService = {
  getAll: (params) => backendAPI.get('/api/drops/', { params }),
  getActive: () => backendAPI.get('/api/drops/active'),
  getById: (id) => backendAPI.get(`/api/drops/${id}`),
  create: (data) => backendAPI.post('/api/admin/drops', data),
  update: (id, data) => backendAPI.put(`/api/admin/drops/${id}`, data),
  delete: (id) => backendAPI.delete(`/api/admin/drops/${id}`),
};

// Waitlist API - Case formatına uygun endpoint'ler
export const waitlistService = {
  join: (dropId) => backendAPI.post(`/api/drops/${dropId}/join`), // Case formatı: POST /drops/:id/join
  leave: (dropId) => backendAPI.post(`/api/drops/${dropId}/leave`), // Case formatı: POST /drops/:id/leave
  getMyWaitlist: () => backendAPI.get('/api/waitlist/my-waitlist'),
  getPosition: (dropId) => backendAPI.get(`/api/waitlist/${dropId}/my-position`),
  getCount: (dropId) => backendAPI.get(`/api/waitlist/${dropId}/waitlist-count`),
};

// Claims API - Case formatına uygun endpoint
export const claimsService = {
  create: (dropId, data) => backendAPI.post(`/api/drops/${dropId}/claim`, data), // Case formatı: POST /drops/:id/claim
  getMyClaims: () => backendAPI.get('/api/claims/my-claims'),
};

// Admin API
export const adminService = {
  getStats: () => backendAPI.get('/api/admin/stats'),
  getClaims: (status) => backendAPI.get('/api/admin/claims', { params: { status_filter: status } }),
  approveClaim: (id) => backendAPI.put(`/api/admin/claims/${id}/approve`),
  rejectClaim: (id) => backendAPI.put(`/api/admin/claims/${id}/reject`),
};

// Super Admin API
export const superAdminService = {
  getUsers: () => backendAPI.get('/api/superadmin/users'),
  getUser: (id) => backendAPI.get(`/api/superadmin/users/${id}`),
  assignRole: (userId, roleId) => backendAPI.post(`/api/superadmin/users/${userId}/roles`, { role_id: roleId }),
  removeRole: (userId, roleId) => backendAPI.delete(`/api/superadmin/users/${userId}/roles/${roleId}`),
  deleteUser: (userId) => backendAPI.delete(`/api/superadmin/users/${userId}`),
  getRoles: () => backendAPI.get('/api/superadmin/roles'),
  createRole: (roleData) => backendAPI.post('/api/superadmin/roles', roleData),
  deleteRole: (roleId) => backendAPI.delete(`/api/superadmin/roles/${roleId}`),
  getStats: () => backendAPI.get('/api/superadmin/stats'),
};

// AI Chat API
export const chatService = {
  ask: (message, chatHistory = [], includeContext = true) => 
    aiAPI.post('/api/chat/ask', { message, chat_history: chatHistory, include_context: includeContext }),
};
