// ─────────────────────────────────────────────────────────────────────────────
// TanStack Query hooks for all API endpoints
// ─────────────────────────────────────────────────────────────────────────────
import {
  useQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';
import {
  snippetsAPI,
  searchAPI,
  tagsAPI,
  collectionsAPI,
  healthAPI,
  statsAPI,
  settingsAPI,
  licenseAPI,
  backupAPI,
  exportAPI,
} from '../api/client';
import type {
  SnippetOut,
  SnippetListResponse,
  SnippetCreateInput,
  SnippetPatchInput,
  SearchResponse,
  TagOutWithCount,
  CollectionOutWithCount,
  HealthResponse,
  StatsResponse,
  SettingsOut,
  LicenseStatus,
  BackupInfo,
  ImportResponse,
} from '../types';

// ─── Query keys ─────────────────────────────────────────────────────────────
export const qk = {
  health: ['health'] as const,
  snippets: (filters?: Record<string, any>) => ['snippets', filters] as const,
  snippet: (id: string) => ['snippet', id] as const,
  search: (q: string) => ['search', q] as const,
  tags: ['tags'] as const,
  collections: ['collections'] as const,
  stats: ['stats'] as const,
  settings: ['settings'] as const,
  license: ['license'] as const,
  backups: ['backups'] as const,
};

// ─── Health ─────────────────────────────────────────────────────────────────
export function useHealth() {
  return useQuery<HealthResponse>({
    queryKey: qk.health,
    queryFn: () => healthAPI.check(),
    retry: 2,
    refetchInterval: 30_000,
  });
}

// ─── Snippets ───────────────────────────────────────────────────────────────
export function useSnippets(opts: {
  limit?: number;
  offset?: number;
  tag_id?: string;
  collection_id?: string;
  pinned?: boolean;
  archived?: boolean;
  sort?: string;
} = {}) {
  return useQuery<SnippetListResponse>({
    queryKey: qk.snippets(opts),
    queryFn: () => snippetsAPI.list(opts),
  });
}

export function useSnippet(id: string | null) {
  return useQuery<SnippetOut>({
    queryKey: qk.snippet(id!),
    queryFn: () => snippetsAPI.get(id!),
    enabled: !!id,
  });
}

export function useCreateSnippet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SnippetCreateInput) => snippetsAPI.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snippets'] });
      qc.invalidateQueries({ queryKey: ['tags'] });
      qc.invalidateQueries({ queryKey: ['collections'] });
      qc.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useUpdateSnippet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SnippetPatchInput }) =>
      snippetsAPI.update(id, data),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: ['snippets'] });
      qc.invalidateQueries({ queryKey: qk.snippet(id) });
      qc.invalidateQueries({ queryKey: ['tags'] });
      qc.invalidateQueries({ queryKey: ['collections'] });
    },
  });
}

export function useDeleteSnippet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => snippetsAPI.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snippets'] });
      qc.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function usePinSnippet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, pinned }: { id: string; pinned: boolean }) =>
      pinned ? snippetsAPI.pin(id) : snippetsAPI.unpin(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snippets'] });
      qc.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useArchiveSnippet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, archived }: { id: string; archived: boolean }) =>
      archived ? snippetsAPI.archive(id) : snippetsAPI.unarchive(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snippets'] });
      qc.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

// ─── Search ─────────────────────────────────────────────────────────────────
export function useSearch(query: string, enabled = true) {
  return useQuery<SearchResponse>({
    queryKey: qk.search(query),
    queryFn: () => searchAPI.search(query),
    enabled: enabled && query.trim().length > 0,
    staleTime: 10_000,
  });
}

// ─── Tags ───────────────────────────────────────────────────────────────────
export function useTags() {
  return useQuery<{ items: TagOutWithCount[]; total: number }>({
    queryKey: qk.tags,
    queryFn: () => tagsAPI.list(),
  });
}

export function useCreateTag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ name, color }: { name: string; color?: string }) =>
      tagsAPI.create(name, color),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.tags }),
  });
}

export function useUpdateTag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { name?: string; color?: string } }) =>
      tagsAPI.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.tags }),
  });
}

export function useDeleteTag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => tagsAPI.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.tags });
      qc.invalidateQueries({ queryKey: ['snippets'] });
    },
  });
}

// ─── Collections ────────────────────────────────────────────────────────────
export function useCollections() {
  return useQuery<{ items: CollectionOutWithCount[]; total: number }>({
    queryKey: qk.collections,
    queryFn: () => collectionsAPI.list(),
  });
}

export function useCreateCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ name, description, icon, color }: { name: string; description?: string; icon?: string; color?: string }) =>
      collectionsAPI.create(name, description, icon, color),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.collections }),
  });
}

export function useUpdateCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { name?: string; description?: string; icon?: string; color?: string };
    }) => collectionsAPI.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.collections }),
  });
}

export function useDeleteCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => collectionsAPI.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.collections });
      qc.invalidateQueries({ queryKey: ['snippets'] });
    },
  });
}

// ─── Stats ──────────────────────────────────────────────────────────────────
export function useStats() {
  return useQuery<StatsResponse>({
    queryKey: qk.stats,
    queryFn: () => statsAPI.get(),
    staleTime: 30_000,
  });
}

// ─── Settings ───────────────────────────────────────────────────────────────
export function useSettings() {
  return useQuery<SettingsOut>({
    queryKey: qk.settings,
    queryFn: () => settingsAPI.get(),
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<SettingsOut>) => settingsAPI.update(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.settings }),
  });
}

// ─── License ────────────────────────────────────────────────────────────────
export function useLicense() {
  return useQuery<LicenseStatus>({
    queryKey: qk.license,
    queryFn: () => licenseAPI.status(),
  });
}

export function useActivateLicense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (key: string) => licenseAPI.activate(key),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.license }),
  });
}

export function useDeactivateLicense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => licenseAPI.deactivate(),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.license }),
  });
}

// ─── Backup ─────────────────────────────────────────────────────────────────
export function useBackups() {
  return useQuery<{ items: BackupInfo[] }>({
    queryKey: qk.backups,
    queryFn: () => backupAPI.list(),
  });
}

export function useRunBackup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => backupAPI.run(),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.backups }),
  });
}

export function useRestoreBackup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => backupAPI.restore(name),
    onSuccess: () => {
      qc.invalidateQueries();
    },
  });
}

// ─── Export / Import ────────────────────────────────────────────────────────
export function useExportJson() {
  return useMutation({
    mutationFn: ({ scope, ids }: { scope?: string; ids?: string[] } = {}) =>
      exportAPI.json(scope, ids),
  });
}

export function useImportFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => exportAPI.importFile(file),
    onSuccess: () => qc.invalidateQueries(),
  });
}
