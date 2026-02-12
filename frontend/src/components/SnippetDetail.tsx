import React, { useEffect } from 'react';
import { Copy, Trash2, ExternalLink } from 'lucide-react';
import { formatDate } from '../utils/helpers';
import type { Snippet } from '../types';

interface SnippetDetailProps {
  snippet: Snippet | null;
  onDelete: (id: string) => Promise<void>;
  loading?: boolean;
}

export const SnippetDetail: React.FC<SnippetDetailProps> = ({
  snippet,
  onDelete,
  loading = false,
}) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    if (snippet) {
      navigator.clipboard.writeText(snippet.body);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDelete = async () => {
    if (!snippet || !window.confirm('Delete this snippet?')) return;
    await onDelete(snippet.id);
  };

  if (!snippet) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">No snippet selected</p>
          <p className="text-sm">Select a snippet to view details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{snippet.title}</h1>
            <p className="text-sm text-gray-600 mt-1">
              {snippet.source && (
                <>
                  <strong>Source:</strong> {snippet.source} •{' '}
                </>
              )}
              <strong>Language:</strong> {snippet.language}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Copy to clipboard"
            >
              <Copy className={`w-5 h-5 ${copied ? 'text-green-600' : 'text-gray-600'}`} />
            </button>
            <button
              onClick={handleDelete}
              disabled={loading}
              className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              title="Delete snippet"
            >
              <Trash2 className="w-5 h-5 text-red-600" />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Created: {formatDate(snippet.created_at)}</span>
          {snippet.updated_at && <span>Updated: {formatDate(snippet.updated_at)}</span>}
        </div>
      </div>

      {/* Tags and Collections */}
      {(snippet.tags.length > 0 || snippet.collections.length > 0) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {snippet.tags.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-semibold text-gray-700 mb-2">Tags</p>
              <div className="flex flex-wrap gap-2">
                {snippet.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="px-3 py-1 rounded-full text-sm"
                    style={{ backgroundColor: tag.color + '20', color: tag.color }}
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            </div>
          )}
          {snippet.collections.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Collections</p>
              <div className="flex flex-wrap gap-2">
                {snippet.collections.map((col) => (
                  <span key={col.id} className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">
                    {col.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Body */}
      <div className="flex-1 p-6 overflow-auto">
        <pre className="bg-gray-50 p-4 rounded-lg border border-gray-200 overflow-x-auto text-sm font-mono text-gray-900 whitespace-pre-wrap break-words">
          {snippet.body}
        </pre>
      </div>
    </div>
  );
};
