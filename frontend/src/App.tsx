import React, { useEffect, useCallback } from 'react';
import { snippetsAPI, tagsAPI, collectionsAPI, healthAPI } from './api/client';
import { useStore } from './stores/appStore';
import { useToast } from './hooks/useToast';
import { SearchBar } from './components/SearchBar';
import { Sidebar } from './components/Sidebar';
import { SnippetList } from './components/SnippetList';
import { SnippetDetail } from './components/SnippetDetail';
import { Toast } from './components/Toast';
import type { Snippet } from './types';

function App() {
  const store = useStore();
  const { toasts, addToast, removeToast } = useToast();

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      store.setBackendStatus('checking');
      try {
        const healthResult = await healthAPI.check();
        
        if (healthResult.status === 'connected') {
          store.setBackendStatus('connected');
        } else {
          store.setBackendStatus('error');
          addToast('Backend connection failed', 'error');
          return;
        }

        store.setLoading(true);
        const [snippets, tags, collections] = await Promise.all([
          snippetsAPI.list(100),
          tagsAPI.list(100),
          collectionsAPI.list(100),
        ]);

        store.setSnippets(snippets);
        store.setTags(tags);
        store.setCollections(collections);
        addToast('Data loaded successfully', 'success', 1000);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load data';
        store.setError(message);
        store.setBackendStatus('error');
        addToast(message, 'error');
      } finally {
        store.setLoading(false);
      }
    };

    loadData();
  }, [store, addToast]);

  const handleSearch = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        try {
          const snippets = await snippetsAPI.list(100);
          store.setSnippets(snippets);
        } catch (err) {
          addToast('Search failed', 'error');
        }
        return;
      }

      try {
        store.setLoading(true);
        const results = await snippetsAPI.search(query, 100);
        store.setSnippets(results);
        addToast(`Found ${results.length} snippet(s)`, 'info', 1000);
      } catch (err) {
        addToast('Search failed', 'error');
      } finally {
        store.setLoading(false);
      }
    },
    [store, addToast]
  );

  const handleCreateNew = useCallback(() => {
    addToast('New snippet form coming soon', 'info', 1000);
  }, [addToast]);

  const handleSelectCollection = useCallback(
    async (collectionId: string | null) => {
      try {
        store.setLoading(true);
        const snippets = await snippetsAPI.list(100, 0, collectionId || undefined);
        store.setSnippets(snippets);
      } catch (err) {
        addToast('Failed to load collection', 'error');
      } finally {
        store.setLoading(false);
      }
    },
    [store, addToast]
  );

  const handleSelectTag = useCallback(
    (_tagId: string | null) => {
      addToast('Tag filtering coming soon', 'info', 1000);
    },
    [addToast]
  );

  const handleSelectSnippet = (snippet: Snippet) => {
    store.setSelectedSnippet(snippet);
  };

  const handleDeleteSnippet = useCallback(
    async (id: string) => {
      try {
        await snippetsAPI.delete(id);
        store.removeSnippet(id);
        addToast('Snippet deleted', 'success', 1000);
      } catch (err) {
        addToast('Failed to delete snippet', 'error');
      }
    },
    [store, addToast]
  );

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 p-4 shadow-sm">
        <div className="max-w-full">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">📌 Pin-Up AI</h1>
          <SearchBar onSearch={handleSearch} onCreateNew={handleCreateNew} />
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          collections={store.collections}
          tags={store.tags}
          onSelectCollection={handleSelectCollection}
          onSelectTag={handleSelectTag}
          backendStatus={store.backendStatus}
        />
        <SnippetList
          snippets={store.snippets}
          selectedId={store.selectedSnippet?.id || null}
          onSelect={handleSelectSnippet}
          loading={store.loading}
        />
        <SnippetDetail
          snippet={store.selectedSnippet}
          onDelete={handleDeleteSnippet}
          loading={store.loading}
        />
      </div>

      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>

      {/* Error Banner */}
      {store.error && (
        <div className="bg-red-50 border-t border-red-200 p-4 text-sm text-red-900">
          {store.error}
        </div>
      )}
    </div>
  );
}

export default App;
