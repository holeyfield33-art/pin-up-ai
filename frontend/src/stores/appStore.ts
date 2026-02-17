// ─────────────────────────────────────────────────────────────────────────────
// Zustand store — global app state
// ─────────────────────────────────────────────────────────────────────────────
import { create } from 'zustand';
import type {
  SnippetOut,
  TagOutWithCount,
  CollectionOutWithCount,
  BackendStatus,
  Page,
} from '../types';

type Theme = 'light' | 'dark' | 'system';

interface AppStore {
  // Theme
  theme: Theme;
  setTheme: (t: Theme) => void;

  // Navigation
  page: Page;
  setPage: (p: Page) => void;

  // Backend status
  backendStatus: BackendStatus;
  setBackendStatus: (s: BackendStatus) => void;

  // Sidebar filter state
  selectedTag: string | null;       // tag name
  selectedCollection: string | null; // collection name
  setSelectedTag: (t: string | null) => void;
  setSelectedCollection: (c: string | null) => void;

  // Snippet list cache
  snippets: SnippetOut[];
  snippetsTotal: number;
  setSnippets: (items: SnippetOut[], total: number) => void;

  // Selected snippet
  selectedSnippetId: string | null;
  setSelectedSnippetId: (id: string | null) => void;

  // Tags/collections cache
  tags: TagOutWithCount[];
  setTags: (t: TagOutWithCount[]) => void;
  collections: CollectionOutWithCount[];
  setCollections: (c: CollectionOutWithCount[]) => void;

  // Search
  searchQuery: string;
  setSearchQuery: (q: string) => void;

  // Editing
  isEditing: boolean;
  setIsEditing: (e: boolean) => void;
  isCreating: boolean;
  setIsCreating: (c: boolean) => void;

  // Loading / error
  loading: boolean;
  setLoading: (l: boolean) => void;
  error: string | null;
  setError: (e: string | null) => void;
}

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('pinup_theme');
  if (stored === 'light' || stored === 'dark' || stored === 'system') return stored;
  return 'system';
}

function applyTheme(theme: Theme) {
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', isDark);
}

export const useAppStore = create<AppStore>((set) => ({
  theme: getInitialTheme(),
  setTheme: (theme) => {
    localStorage.setItem('pinup_theme', theme);
    applyTheme(theme);
    set({ theme });
  },

  page: 'snippets',
  setPage: (page) => set({ page }),

  backendStatus: 'checking',
  setBackendStatus: (backendStatus) => set({ backendStatus }),

  selectedTag: null,
  selectedCollection: null,
  setSelectedTag: (selectedTag) => set({ selectedTag, selectedCollection: null }),
  setSelectedCollection: (selectedCollection) => set({ selectedCollection, selectedTag: null }),

  snippets: [],
  snippetsTotal: 0,
  setSnippets: (items, total) => set({ snippets: items, snippetsTotal: total }),

  selectedSnippetId: null,
  setSelectedSnippetId: (selectedSnippetId) => set({ selectedSnippetId }),

  tags: [],
  setTags: (tags) => set({ tags }),
  collections: [],
  setCollections: (collections) => set({ collections }),

  searchQuery: '',
  setSearchQuery: (searchQuery) => set({ searchQuery }),

  isEditing: false,
  setIsEditing: (isEditing) => set({ isEditing }),
  isCreating: false,
  setIsCreating: (isCreating) => set({ isCreating }),

  loading: false,
  setLoading: (loading) => set({ loading }),
  error: null,
  setError: (error) => set({ error }),
}));
