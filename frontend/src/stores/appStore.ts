import { create } from 'zustand';
import type { Snippet, Tag, Collection, AppState } from '../types';

interface Store extends AppState {
  // Actions
  setSnippets: (snippets: Snippet[]) => void;
  setSelectedSnippet: (snippet: Snippet | null) => void;
  setTags: (tags: Tag[]) => void;
  setCollections: (collections: Collection[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setBackendStatus: (status: AppState['backendStatus']) => void;
  addSnippet: (snippet: Snippet) => void;
  removeSnippet: (id: string) => void;
  updateSnippet: (id: string, snippet: Partial<Snippet>) => void;
}

export const useStore = create<Store>((set) => ({
  // Initial state
  snippets: [],
  selectedSnippet: null,
  tags: [],
  collections: [],
  loading: false,
  error: null,
  backendStatus: 'checking',

  // Actions
  setSnippets: (snippets) => set({ snippets }),
  setSelectedSnippet: (selectedSnippet) => set({ selectedSnippet }),
  setTags: (tags) => set({ tags }),
  setCollections: (collections) => set({ collections }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setBackendStatus: (backendStatus) => set({ backendStatus }),

  addSnippet: (snippet) =>
    set((state) => ({
      snippets: [snippet, ...state.snippets],
    })),

  removeSnippet: (id) =>
    set((state) => ({
      snippets: state.snippets.filter((s) => s.id !== id),
      selectedSnippet: state.selectedSnippet?.id === id ? null : state.selectedSnippet,
    })),

  updateSnippet: (id, updates) =>
    set((state) => ({
      snippets: state.snippets.map((s) => (s.id === id ? { ...s, ...updates } : s)),
      selectedSnippet:
        state.selectedSnippet?.id === id
          ? { ...state.selectedSnippet, ...updates }
          : state.selectedSnippet,
    })),
}));
