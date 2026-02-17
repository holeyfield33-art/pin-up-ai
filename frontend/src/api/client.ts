// ─────────────────────────────────────────────────────────────────────────────
// API client — thin wrapper around fetch with bearer token injection
// ─────────────────────────────────────────────────────────────────────────────
import type {
  SnippetOut,
  SnippetListResponse,
  SnippetCreateInput,
  SnippetPatchInput,
  SearchResponse,
  TagOut,
  TagOutWithCount,
  CollectionOut,
  CollectionOutWithCount,
  HealthResponse,
  StatsResponse,
  SettingsOut,
  LicenseStatus,
  BackupInfo,
  ImportResponse,
  OkResponse,
} from '../types';

// Bootstrap config — set by Tauri or dev defaults
let BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
let AUTH_TOKEN = import.meta.env.VITE_API_TOKEN || '';

export function setBootstrap(baseUrl: string, token: string) {
  BASE_URL = baseUrl.replace(/\/+$/, '');
  AUTH_TOKEN = token;
}

export function getBaseUrl() {
  return BASE_URL;
}

export function getToken() {
  return AUTH_TOKEN;
}

// ─── Core request helper ────────────────────────────────────────────────────
async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string> || {}),
  };
  // Don't set Content-Type for FormData
  if (!(init.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  headers['X-Request-ID'] = `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;

  const res = await fetch(url, { ...init, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ message: res.statusText }));
    throw new ApiError(res.status, body.message || body.code || res.statusText);
  }

  // 204 No Content
  if (res.status === 204) return undefined as unknown as T;

  return res.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

function qs(params: Record<string, string | number | boolean | undefined>): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined);
  if (!entries.length) return '';
  return '?' + new URLSearchParams(
    entries.map(([k, v]) => [k, String(v)]),
  ).toString();
}

// ─── Snippets ───────────────────────────────────────────────────────────────
export const snippetsAPI = {
  list: (opts: {
    limit?: number;
    offset?: number;
    tag_id?: string;
    collection_id?: string;
    pinned?: boolean;
    archived?: boolean;
    sort?: string;
  } = {}) =>
    request<SnippetListResponse>(
      `/snippets${qs({ ...opts })}`,
    ),

  get: (id: string) => request<SnippetOut>(`/snippets/${id}`),

  create: (data: SnippetCreateInput) =>
    request<SnippetOut>('/snippets', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: string, data: SnippetPatchInput) =>
    request<SnippetOut>(`/snippets/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  delete: (id: string) => request<OkResponse>(`/snippets/${id}`, { method: 'DELETE' }),

  pin: (id: string) => request<SnippetOut>(`/snippets/${id}/pin`, { method: 'POST' }),
  unpin: (id: string) => request<SnippetOut>(`/snippets/${id}/unpin`, { method: 'POST' }),
  archive: (id: string) => request<SnippetOut>(`/snippets/${id}/archive`, { method: 'POST' }),
  unarchive: (id: string) => request<SnippetOut>(`/snippets/${id}/unarchive`, { method: 'POST' }),
};

// ─── Search ─────────────────────────────────────────────────────────────────
export const searchAPI = {
  search: (q: string, limit = 50, offset = 0, sort?: string) =>
    request<SearchResponse>(`/search${qs({ q, limit, offset, sort })}`),
};

// ─── Tags ───────────────────────────────────────────────────────────────────
export const tagsAPI = {
  list: () =>
    request<{ items: TagOutWithCount[]; total: number }>('/tags'),

  create: (name: string, color?: string) =>
    request<TagOut>('/tags', { method: 'POST', body: JSON.stringify({ name, color }) }),

  update: (id: string, data: { name?: string; color?: string }) =>
    request<TagOut>(`/tags/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  delete: (id: string) => request<OkResponse>(`/tags/${id}`, { method: 'DELETE' }),
};

// ─── Collections ────────────────────────────────────────────────────────────
export const collectionsAPI = {
  list: () =>
    request<{ items: CollectionOutWithCount[]; total: number }>('/collections'),

  create: (name: string, description?: string, icon?: string, color?: string) =>
    request<CollectionOut>('/collections', {
      method: 'POST',
      body: JSON.stringify({ name, description, icon, color }),
    }),

  update: (id: string, data: { name?: string; description?: string; icon?: string; color?: string }) =>
    request<CollectionOut>(`/collections/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: string) => request<OkResponse>(`/collections/${id}`, { method: 'DELETE' }),
};

// ─── Health ─────────────────────────────────────────────────────────────────
export const healthAPI = {
  check: () => request<HealthResponse>('/health'),
};

// ─── Stats ──────────────────────────────────────────────────────────────────
export const statsAPI = {
  get: () => request<StatsResponse>('/stats'),
};

// ─── Settings ───────────────────────────────────────────────────────────────
export const settingsAPI = {
  get: () => request<SettingsOut>('/settings'),
  update: (data: Partial<SettingsOut>) =>
    request<SettingsOut>('/settings', { method: 'PATCH', body: JSON.stringify(data) }),
  rotateToken: () =>
    request<{ token: string }>('/settings/rotate-token', { method: 'POST' }),
};

// ─── License ────────────────────────────────────────────────────────────────
export const licenseAPI = {
  status: () => request<LicenseStatus>('/license/status'),
  activate: (key: string) =>
    request<LicenseStatus>('/license/activate', {
      method: 'POST',
      body: JSON.stringify({ license_key: key }),
    }),
  deactivate: () => request<OkResponse>('/license/deactivate', { method: 'POST' }),
};

// ─── Backup ─────────────────────────────────────────────────────────────────
export const backupAPI = {
  list: () => request<{ items: BackupInfo[] }>('/backup/list'),
  run: () => request<BackupInfo>('/backup/run', { method: 'POST' }),
  restore: (name: string) =>
    request<OkResponse>(`/backup/restore/${encodeURIComponent(name)}`, { method: 'POST' }),
};

// ─── Export / Import ────────────────────────────────────────────────────────
export const exportAPI = {
  json: (scope = 'all', ids?: string[]) =>
    request<any>('/export', {
      method: 'POST',
      body: JSON.stringify({ format: 'json', scope, ids: ids || [] }),
    }),

  bundle: (scope = 'all', ids?: string[]) =>
    request<Blob>('/export', {
      method: 'POST',
      body: JSON.stringify({ format: 'bundle', scope, ids: ids || [] }),
    }),

  /** Import accepts a File (zip bundle) uploaded as multipart/form-data */
  importFile: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<ImportResponse>('/import', { method: 'POST', body: form });
  },
};
