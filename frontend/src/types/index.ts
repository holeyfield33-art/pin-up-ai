// ─────────────────────────────────────────────────────────────────────────────
// Types matching backend schemas exactly.
// Timestamps are epoch milliseconds (number).
// ─────────────────────────────────────────────────────────────────────────────

export interface TagOut {
  id: string;
  name: string;
  color: string | null;
  created_at: number;
}

export interface TagOutWithCount extends TagOut {
  count: number;
}

export interface CollectionOut {
  id: string;
  name: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  created_at: number;
  updated_at: number;
}

export interface CollectionOutWithCount extends CollectionOut {
  count: number;
}

export interface SnippetOut {
  id: string;
  title: string;
  body: string;
  language: string | null;
  source: string | null;
  source_url: string | null;
  pinned: number;       // 0 | 1
  archived: number;     // 0 | 1
  created_at: number;
  updated_at: number;
  tags: TagOut[];
  collections: CollectionOut[];
}

export interface SnippetListResponse {
  items: SnippetOut[];
  total: number;
}

export interface SnippetCreateInput {
  body: string;
  title?: string;
  language?: string;
  source?: string;
  source_url?: string;
  tags?: string[];
  collections?: string[];
  pinned?: boolean;
}

export interface SnippetPatchInput {
  title?: string;
  body?: string;
  language?: string;
  source?: string;
  source_url?: string;
  tags?: string[];
  collections?: string[];
  pinned?: boolean;
  archived?: boolean;
}

/** Flat search result item — not a full SnippetOut */
export interface SearchResultItem {
  id: string;
  title: string;
  preview: string;
  tags: string[];
  collections: string[];
  source: string | null;
  language: string | null;
  created_at: number;
  updated_at: number;
}

export interface SearchResponse {
  results: SearchResultItem[];
  total: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  db_path: string;
  uptime_ms: number;
}

export interface StatsResponse {
  totals: {
    snippets: number;
    tags: number;
    collections: number;
    pinned: number;
    archived: number;
  };
  top_tags: { name: string; count: number }[];
  top_collections: { name: string; count: number }[];
  created_counts: Record<string, number>;
  recent_activity: Record<string, any>[];
  vault: {
    db_size_bytes: number;
    fts_entries: number;
  };
}

export interface SettingsOut {
  dedupe_enabled: boolean;
  backup_enabled: boolean;
  backup_schedule: string;
}

export interface LicenseStatus {
  status: string;    // trial_active | trial_expired | licensed_active | grace_period
  days_left: number;
  entitled: boolean;
  plan: string;      // trial | pro | pro_plus
}

export interface BackupInfo {
  name: string;
  created_at: number;
  db_size_bytes: number;
  app_version: string;
}

export interface ImportResponse {
  ok: boolean;
  imported: Record<string, number>;
  merged: Record<string, number>;
}

export interface ExportData {
  version: number;
  exported_at: number;
  snippets: SnippetOut[];
  tags: TagOut[];
  collections: CollectionOut[];
}

export interface OkResponse {
  ok: boolean;
}

export interface ErrorEnvelope {
  code: string;
  message: string;
  details?: any;
}

export type BackendStatus = 'checking' | 'connected' | 'error' | 'disconnected';
export type Page = 'snippets' | 'dashboard' | 'tags' | 'collections' | 'settings';
