import axios, { AxiosInstance } from 'axios';
import type { Snippet, Tag, Collection, SnippetCreateInput } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const client: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
client.interceptors.request.use((config) => {
  const requestId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  config.headers['X-Request-ID'] = requestId;
  return config;
});

// Response interceptor
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      throw new Error('Rate limited. Please try again later.');
    }
    if (error.response?.status === 401) {
      throw new Error('Unauthorized.');
    }
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
);

export const snippetsAPI = {
  list: async (limit = 50, offset = 0, collectionId?: string) => {
    const { data } = await client.get<{ data: Snippet[] }>('/snippets', {
      params: { limit, offset, collection_id: collectionId },
    });
    return data.data;
  },

  create: async (snippet: SnippetCreateInput) => {
    const { data } = await client.post<Snippet>('/snippets', snippet);
    return data;
  },

  get: async (id: string) => {
    const { data } = await client.get<Snippet>(`/snippets/${id}`);
    return data;
  },

  update: async (id: string, snippet: Partial<SnippetCreateInput>) => {
    const { data } = await client.put<Snippet>(`/snippets/${id}`, snippet);
    return data;
  },

  delete: async (id: string) => {
    await client.delete(`/snippets/${id}`);
  },

  search: async (query: string, limit = 50) => {
    const { data } = await client.get<{ data: Snippet[] }>('/search/query', {
      params: { q: query, limit },
    });
    return data.data;
  },

  export: async (format: 'json' | 'markdown') => {
    const { data } = await client.get(`/snippets/export/${format}`);
    return data;
  },
};

export const tagsAPI = {
  list: async (limit = 100) => {
    const { data } = await client.get<{ data: Tag[] }>('/tags', { params: { limit } });
    return data.data;
  },

  create: async (name: string, color = '#6366F1') => {
    const { data } = await client.post<Tag>('/tags', { name, color });
    return data;
  },

  delete: async (id: string) => {
    await client.delete(`/tags/${id}`);
  },
};

export const collectionsAPI = {
  list: async (limit = 100) => {
    const { data } = await client.get<{ data: Collection[] }>('/collections', { params: { limit } });
    return data.data;
  },

  create: async (name: string, description?: string) => {
    const { data } = await client.post<Collection>('/collections', { name, description });
    return data;
  },

  delete: async (id: string) => {
    await client.delete(`/collections/${id}`);
  },
};

export const healthAPI = {
  check: async () => {
    try {
      const { data } = await client.get('/health');
      return { status: 'connected' as const, data };
    } catch (error) {
      return { status: 'error' as const, error };
    }
  },
};

export default client;
