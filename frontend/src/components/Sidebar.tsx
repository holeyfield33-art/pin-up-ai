import React from 'react';
import { Folder, Tag, Circle } from 'lucide-react';
import type { Collection, Tag as TagType } from '../types';
import clsx from 'clsx';

interface SidebarProps {
  collections: Collection[];
  tags: TagType[];
  onSelectCollection: (id: string | null) => void;
  onSelectTag: (id: string | null) => void;
  backendStatus:  'checking' | 'connected' | 'error' | 'disconnected';
}

export const Sidebar: React.FC<SidebarProps> = ({
  collections,
  tags,
  onSelectCollection,
  onSelectTag,
  backendStatus,
}) => {
  const statusColor = {
    connected: 'bg-green-500',
    error: 'bg-red-500',
    checking: 'bg-yellow-500',
    disconnected: 'bg-gray-500',
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
      {/* Status Indicator */}
      <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-200">
        <Circle className={clsx('w-3 h-3 rounded-full', statusColor[backendStatus])} />
        <span className="text-sm text-gray-600 capitalize">{backendStatus}</span>
      </div>

      {/* Collections */}
      <div className="mb-6">
        <h3 className="flex items-center gap-2 font-semibold text-sm mb-3 text-gray-900">
          <Folder className="w-4 h-4" />
          Collections
        </h3>
        <button
          onClick={() => onSelectCollection(null)}
          className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-200 transition-colors"
        >
          All Snippets
        </button>
        {collections.map((col) => (
          <button
            key={col.id}
            onClick={() => onSelectCollection(col.id)}
            className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-200 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="truncate">{col.name}</span>
              <span className="text-xs bg-gray-300 text-gray-700 px-2 py-1 rounded">
                {col.snippet_count ?? 0}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Tags */}
      <div>
        <h3 className="flex items-center gap-2 font-semibold text-sm mb-3 text-gray-900">
          <Tag className="w-4 h-4" />
          Tags
        </h3>
        <button
          onClick={() => onSelectTag(null)}
          className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-200 transition-colors"
        >
          All Tags
        </button>
        {tags.slice(0, 10).map((tag) => (
          <button
            key={tag.id}
            onClick={() => onSelectTag(tag.id)}
            className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-200 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Circle className="w-2 h-2 rounded-full" style={{ color: tag.color }} />
              <span className="truncate flex-1">{tag.name}</span>
              <span className="text-xs text-gray-500">{tag.snippet_count ?? 0}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
