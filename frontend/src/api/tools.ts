import axios from 'axios';
import type { Tool, ToolCreate } from '../types';
import type { User } from '../types/auth';

const API_BASE_URL = 'http://10.40.1.65:8889';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const getTools = async (): Promise<Tool[]> => {
  const response = await api.get('/api/tools');
  return response.data;
};

export const getTool = async (id: string): Promise<Tool> => {
  const response = await api.get(`/api/tools/${id}`);
  return response.data;
};

export const createTool = async (tool: ToolCreate): Promise<Tool> => {
  const response = await api.post('/api/tools', tool);
  return response.data;
};

export const updateTool = async (id: string, tool: Partial<ToolCreate>): Promise<Tool> => {
  const response = await api.put(`/api/tools/${id}`, tool);
  return response.data;
};

export const deleteTool = async (id: string): Promise<void> => {
  await api.delete(`/api/tools/${id}`);
};

export const searchTools = async (query?: string, tags?: string): Promise<Tool[]> => {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (tags) params.append('tags', tags);
  
  const response = await api.get(`/api/search?${params.toString()}`);
  return response.data;
};

export const getAllTags = async (): Promise<string[]> => {
  const response = await api.get('/api/tags');
  return response.data;
};

export const getTagStats = async () => {
  const response = await api.get('/api/tags/stats');
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/api/users/me');
  return response.data;
};

export const aiSearch = async (query: string, limit: number = 10): Promise<any> => {
  const response = await api.get('/api/ai-search', {
    params: { q: query, limit }
  });
  return response.data;
};

export const docSearch = async (query: string, limit: number = 10): Promise<any> => {
  const response = await api.get('/api/doc-search', {
    params: { q: query, limit }
  });
  return response.data;
};

export const checkIsAdmin = async (): Promise<boolean> => {
  try {
    const response = await api.get('/api/admins/is-admin');
    return response.data.is_admin;
  } catch (error) {
    console.error('Failed to check admin status:', error);
    return false;
  }
};
