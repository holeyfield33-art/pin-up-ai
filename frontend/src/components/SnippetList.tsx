import React, { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Pin, Archive, Clock, FileCode, Search as SearchIcon, Inbox } from 'lucide-react';
import { cn, formatDate, truncate } from '../utils/helpers';
import { SnippetListSkeleton } from './Skeleton';
import type { SnippetOut, SearchResultItem } from '../types';

/* -------------------------------------------------------------------------- */
/*  Props                                                                     */
/* -------------------------------------------------------------------------- */
interface SnippetListProps {
  /** Regular snippet items (when not searching) */
  items: SnippetOut[];
  /** Search result items (when searching) */
  searchResults?: SearchResultItem[];
  isLoading: boolean;
  selectedId: string | null;
  onSelect: (id: string) => void;
}

/* -------------------------------------------------------------------------- */
/*  Normalised row — works for both snippet & search result                  */
/* -------------------------------------------------------------------------- */
interface Row {
  id: string;
  title: string;
  preview: string;
  language: string | null;
  tags: string[];
  pinned: boolean;
  archived: boolean;
  updatedAt: number;
}

function snippetToRow(s: SnippetOut): Row {
  return {
    id: s.id,
    title: s.title,
    preview: truncate(s.body.replace(/\n/g, ' '), 100),
    language: s.language,
    tags: s.tags.map((t) => t.name),
    pinned: s.pinned === 1,
    archived: s.archived === 1,
    updatedAt: s.updated_at,
  };
}

function searchToRow(r: SearchResultItem): Row {
  return {
    id: r.id,
    title: r.title,
    preview: r.preview,
    language: r.language,
    tags: r.tags,
    pinned: false,
    archived: false,
    updatedAt: r.updated_at,
  };
}

/* -------------------------------------------------------------------------- */
/*  Row height (estimated)                                                    */
/* -------------------------------------------------------------------------- */
const ROW_HEIGHT = 76;

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */
export const SnippetList: React.FC<SnippetListProps> = ({
  items,
  searchResults,
  isLoading,
  selectedId,
  onSelect,
}) => {
  const parentRef = useRef<HTMLDivElement>(null);
  const isSearch = !!searchResults;
  const rows: Row[] = isSearch
    ? searchResults!.map(searchToRow)
    : items.map(snippetToRow);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ROW_HEIGHT,
    overscan: 8,
  });

  /* ── Loading state ────────────────────────────────────────────────────── */
  if (isLoading) {
    return (
      <div className="w-72 border-r border-gray-200 dark:border-gray-700" role="status">
        <SnippetListSkeleton count={6} />
      </div>
    );
  }

  /* ── Empty state ──────────────────────────────────────────────────────── */
  if (rows.length === 0) {
    return (
      <div className="w-72 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center text-gray-400 gap-3 p-6">
        {isSearch ? (
          <>
            <SearchIcon className="w-8 h-8" />
            <p className="text-sm text-center">No results found</p>
          </>
        ) : (
          <>
            <Inbox className="w-8 h-8" />
            <p className="text-sm text-center">No snippets yet</p>
            <p className="text-xs text-center">Click <strong>+ New</strong> to create one</p>
          </>
        )}
      </div>
    );
  }

  /* ── Virtualised list ─────────────────────────────────────────────────── */
  return (
    <div
      ref={parentRef}
      className="w-72 border-r border-gray-200 dark:border-gray-700 overflow-y-auto"
      role="listbox"
      aria-label={isSearch ? 'Search results' : 'Snippet list'}
    >
      <div
        style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
      >
        {virtualizer.getVirtualItems().map((vItem) => {
          const row = rows[vItem.index];
          const isSelected = row.id === selectedId;

          return (
            <button
              key={row.id}
              role="option"
              aria-selected={isSelected}
              onClick={() => onSelect(row.id)}
              tabIndex={0}
              className={cn(
                'absolute top-0 left-0 w-full px-3 py-2.5 text-left border-b border-gray-100 dark:border-gray-700 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-inset',
                isSelected
                  ? 'bg-brand-50 dark:bg-brand-900/30 border-l-2 border-l-brand-600'
                  : 'bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800',
              )}
              style={{
                height: `${vItem.size}px`,
                transform: `translateY(${vItem.start}px)`,
              }}
            >
              {/* Title row */}
              <div className="flex items-center gap-1.5 mb-0.5">
                {row.pinned && <Pin className="w-3 h-3 text-amber-500 shrink-0" aria-label="Pinned" />}
                {row.archived && <Archive className="w-3 h-3 text-gray-400 shrink-0" aria-label="Archived" />}
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate flex-1">
                  {row.title || 'Untitled'}
                </span>
              </div>

              {/* Preview */}
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate mb-1">{row.preview || '\u00A0'}</p>

              {/* Meta row */}
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                {row.language && (
                  <span className="flex items-center gap-0.5">
                    <FileCode className="w-3 h-3" />
                    {row.language}
                  </span>
                )}
                <span className="flex items-center gap-0.5 ml-auto">
                  <Clock className="w-3 h-3" />
                  {formatDate(row.updatedAt)}
                </span>
              </div>

              {/* Tags (show first 3) */}
              {row.tags.length > 0 && (
                <div className="flex gap-1 mt-1 flex-wrap">
                  {row.tags.slice(0, 3).map((t) => (
                    <span
                      key={t}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-brand-100 text-brand-700"
                    >
                      {t}
                    </span>
                  ))}
                  {row.tags.length > 3 && (
                    <span className="text-[10px] text-gray-400">+{row.tags.length - 3}</span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
