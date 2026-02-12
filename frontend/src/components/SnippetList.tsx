import React from 'react';
import { formatDate, truncate } from '../utils/helpers';
import type { Snippet } from '../types';
import clsx from 'clsx';

interface SnippetListProps {
  snippets: Snippet[];
  selectedId: string | null;
  onSelect: (snippet: Snippet) => void;
  loading: boolean;
}

export const SnippetList: React.FC<SnippetListProps> = ({
  snippets,
  selectedId,
  onSelect,
  loading,
}) => {
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-gray-500">Loading snippets...</div>
      </div>
    );
  }

  if (snippets.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">No snippets yet</p>
          <p className="text-sm">Create your first snippet to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 border-r border-gray-200 overflow-y-auto">
      {snippets.map((snippet) => (
        <button
          key={snippet.id}
          onClick={() => onSelect(snippet)}
          className={clsx(
            'w-full p-4 border-b border-gray-100 text-left hover:bg-gray-50 transition-colors',
            selectedId === snippet.id && 'bg-blue-50 border-l-4 border-blue-500'
          )}
        >
          <h3 className="font-semibold text-gray-900 truncate">{snippet.title}</h3>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {truncate(snippet.body, 100)}
          </p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
              {snippet.language}
            </span>
            <span className="text-xs text-gray-500">{formatDate(snippet.created_at)}</span>
          </div>
          {snippet.tags.length > 0 && (
            <div className="flex gap-1 mt-2">
              {snippet.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag.id}
                  className="text-xs px-2 py-1 rounded-full"
                  style={{ backgroundColor: tag.color + '20', color: tag.color }}
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}
        </button>
      ))}
    </div>
  );
};
