import React, { useCallback } from 'react';
import { useAppStore } from '../stores/appStore';
import { SearchBar } from '../components/SearchBar';
import { SnippetList } from '../components/SnippetList';
import { SnippetDetail } from '../components/SnippetDetail';
import { useSnippets, useSearch, useCreateSnippet } from '../hooks/useApi';
import { Plus } from 'lucide-react';

interface SnippetsPageProps {
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

export const SnippetsPage: React.FC<SnippetsPageProps> = ({ showToast }) => {
  const searchQuery = useAppStore((s) => s.searchQuery);
  const setSearchQuery = useAppStore((s) => s.setSearchQuery);
  const selectedTag = useAppStore((s) => s.selectedTag);
  const selectedCollection = useAppStore((s) => s.selectedCollection);
  const selectedSnippetId = useAppStore((s) => s.selectedSnippetId);
  const setSelectedSnippetId = useAppStore((s) => s.setSelectedSnippetId);
  const isCreating = useAppStore((s) => s.isCreating);
  const setIsCreating = useAppStore((s) => s.setIsCreating);

  // Use search or list depending on query
  const isSearching = searchQuery.trim().length > 0;
  const searchResult = useSearch(searchQuery, isSearching);

  // Build filter params for snippets list
  // We need tag_id and collection_id but sidebar stores names — we'll pass names
  // as tag/collection and resolve via search DSL or filter by name.
  // For simplicity, use the list endpoint without filter when sidebar names are set,
  // then filter client-side. Or use search DSL: tag:NAME
  const snippetsQuery = useSnippets({
    limit: 200,
    archived: false,
  });

  const createSnippet = useCreateSnippet();

  const handleNewSnippet = useCallback(() => {
    setIsCreating(true);
    setSelectedSnippetId(null);
  }, [setIsCreating, setSelectedSnippetId]);

  const handleCreated = useCallback(
    (id: string) => {
      setIsCreating(false);
      setSelectedSnippetId(id);
      showToast('Snippet created', 'success');
    },
    [setIsCreating, setSelectedSnippetId, showToast],
  );

  // Get items to show
  let items = snippetsQuery.data?.items ?? [];

  // Client-side filter by tag/collection name when sidebar selection is active
  if (selectedTag && !isSearching) {
    items = items.filter((s) => s.tags.some((t) => t.name === selectedTag));
  }
  if (selectedCollection && !isSearching) {
    items = items.filter((s) =>
      s.collections.some((c) => c.name === selectedCollection),
    );
  }

  return (
    <>
      {/* Header bar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 shrink-0">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search snippets… (⌘K)"
        />
        <button
          onClick={handleNewSnippet}
          className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          New
        </button>
      </div>

      {/* Content: list + detail panes */}
      <div className="flex flex-1 overflow-hidden">
        <SnippetList
          items={isSearching ? [] : items}
          searchResults={isSearching ? searchResult.data?.results ?? [] : undefined}
          isLoading={isSearching ? searchResult.isLoading : snippetsQuery.isLoading}
          selectedId={selectedSnippetId}
          onSelect={(id) => {
            setSelectedSnippetId(id);
            setIsCreating(false);
          }}
        />

        <SnippetDetail
          snippetId={selectedSnippetId}
          isCreating={isCreating}
          onCreated={handleCreated}
          onCancelCreate={() => setIsCreating(false)}
          showToast={showToast}
        />
      </div>
    </>
  );
};
