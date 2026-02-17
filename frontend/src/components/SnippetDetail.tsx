import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import {
  Pin,
  PinOff,
  Archive,
  ArchiveRestore,
  Trash2,
  Copy,
  Pencil,
  Save,
  X,
  ExternalLink,
  FileCode,
  Tag,
  Folder,
  Plus,
  Check,
} from 'lucide-react';
import { cn, formatDate, formatBytes } from '../utils/helpers';
import {
  useSnippet,
  useCreateSnippet,
  useUpdateSnippet,
  useDeleteSnippet,
  usePinSnippet,
  useArchiveSnippet,
} from '../hooks/useApi';
import type { SnippetCreateInput, SnippetPatchInput, SnippetOut } from '../types';

/* -------------------------------------------------------------------------- */
/*  Props                                                                     */
/* -------------------------------------------------------------------------- */
interface SnippetDetailProps {
  snippetId: string | null;
  isCreating: boolean;
  onCreated: (id: string) => void;
  onCancelCreate: () => void;
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

/* -------------------------------------------------------------------------- */
/*  Blank create state                                                        */
/* -------------------------------------------------------------------------- */
const BLANK: SnippetCreateInput = {
  body: '',
  title: '',
  language: '',
  source: '',
  source_url: '',
  tags: [],
  collections: [],
  pinned: false,
};

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */
export const SnippetDetail: React.FC<SnippetDetailProps> = ({
  snippetId,
  isCreating,
  onCreated,
  onCancelCreate,
  showToast,
}) => {
  /* ── Queries / mutations ─────────────────────────────────────────────── */
  const snippetQuery = useSnippet(snippetId);
  const snippet = snippetQuery.data ?? null;

  const createMut = useCreateSnippet();
  const updateMut = useUpdateSnippet();
  const deleteMut = useDeleteSnippet();
  const pinMut = usePinSnippet();
  const archiveMut = useArchiveSnippet();

  /* ── Local edit/create state ─────────────────────────────────────────── */
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState<SnippetPatchInput & { tags_text: string; collections_text: string }>({
    title: '',
    body: '',
    language: '',
    source: '',
    source_url: '',
    tags: [],
    collections: [],
    tags_text: '',
    collections_text: '',
  });

  const [confirmDelete, setConfirmDelete] = useState(false);
  const [copied, setCopied] = useState(false);
  const codeRef = useRef<HTMLElement>(null);
  const bodyRef = useRef<HTMLTextAreaElement>(null);

  /* ── Populate form from snippet or blank ─────────────────────────────── */
  const populateForm = useCallback((s: SnippetOut | null) => {
    if (!s) {
      setForm({
        ...BLANK,
        tags_text: '',
        collections_text: '',
      });
      return;
    }
    setForm({
      title: s.title,
      body: s.body,
      language: s.language ?? '',
      source: s.source ?? '',
      source_url: s.source_url ?? '',
      tags: s.tags.map((t) => t.name),
      collections: s.collections.map((c) => c.name),
      tags_text: s.tags.map((t) => t.name).join(', '),
      collections_text: s.collections.map((c) => c.name).join(', '),
    });
  }, []);

  useEffect(() => {
    if (isCreating) {
      populateForm(null);
      setIsEditing(false);
    }
  }, [isCreating, populateForm]);

  useEffect(() => {
    if (snippet && !isCreating) {
      populateForm(snippet);
      setIsEditing(false);
    }
  }, [snippet, isCreating, populateForm]);

  /* ── Highlight code on snippet change (lazy-loaded) ───────────────── */
  useEffect(() => {
    if (codeRef.current && snippet && !isEditing && !isCreating) {
      (async () => {
        const [hljs] = await Promise.all([
          import('highlight.js').then((m) => m.default),
          import('highlight.js/styles/github.css'),
        ]);
        codeRef.current!.removeAttribute('data-highlighted');
        hljs.highlightElement(codeRef.current!);
      })();
    }
  }, [snippet, isEditing, isCreating]);

  /* ── Handlers ────────────────────────────────────────────────────────── */
  const handleFieldChange = (field: string, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const parseTags = (text: string): string[] =>
    text
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

  const handleSave = async () => {
    const tags = parseTags(form.tags_text);
    const collections = parseTags(form.collections_text);

    if (isCreating) {
      const payload: SnippetCreateInput = {
        body: form.body || '',
        title: form.title || undefined,
        language: form.language || undefined,
        source: form.source || undefined,
        source_url: form.source_url || undefined,
        tags,
        collections,
        pinned: false,
      };
      try {
        const created = await createMut.mutateAsync(payload);
        onCreated(created.id);
      } catch (e: any) {
        showToast(e.message || 'Failed to create snippet', 'error');
      }
    } else if (snippetId) {
      const payload: SnippetPatchInput = {
        title: form.title,
        body: form.body,
        language: form.language || undefined,
        source: form.source || undefined,
        source_url: form.source_url || undefined,
        tags,
        collections,
      };
      try {
        await updateMut.mutateAsync({ id: snippetId, data: payload });
        setIsEditing(false);
        showToast('Snippet updated', 'success');
      } catch (e: any) {
        showToast(e.message || 'Failed to update snippet', 'error');
      }
    }
  };

  const handleDelete = async () => {
    if (!snippetId) return;
    try {
      await deleteMut.mutateAsync(snippetId);
      showToast('Snippet deleted', 'success');
      setConfirmDelete(false);
    } catch (e: any) {
      showToast(e.message || 'Failed to delete', 'error');
    }
  };

  const handlePin = () => {
    if (!snippet) return;
    pinMut.mutate(
      { id: snippet.id, pinned: snippet.pinned !== 1 },
      {
        onSuccess: () => showToast(snippet.pinned === 1 ? 'Unpinned' : 'Pinned', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      },
    );
  };

  const handleArchive = () => {
    if (!snippet) return;
    archiveMut.mutate(
      { id: snippet.id, archived: snippet.archived !== 1 },
      {
        onSuccess: () =>
          showToast(snippet.archived === 1 ? 'Unarchived' : 'Archived', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      },
    );
  };

  const handleCopy = async () => {
    if (!snippet) return;
    try {
      await navigator.clipboard.writeText(snippet.body);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      showToast('Copy failed', 'error');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
    if (e.key === 'Escape') {
      if (isCreating) onCancelCreate();
      else setIsEditing(false);
    }
  };

  /* ── Derived ─────────────────────────────────────────────────────────── */
  const isSaving = createMut.isPending || updateMut.isPending;
  const isFormMode = isCreating || isEditing;

  /* ── Empty state — nothing selected ──────────────────────────────────── */
  if (!isCreating && !snippetId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-3 p-8">
        <FileCode className="w-12 h-12" />
        <p className="text-sm">Select a snippet to view it here</p>
        <p className="text-xs">or press <kbd className="px-1.5 py-0.5 rounded bg-gray-200 text-gray-600 text-[11px]">⌘N</kbd> to create one</p>
      </div>
    );
  }

  /* ── Loading state ───────────────────────────────────────────────────── */
  if (snippetId && snippetQuery.isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400" role="status">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  /* ── Error state ─────────────────────────────────────────────────────── */
  if (snippetId && snippetQuery.isError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-500 gap-2 p-8">
        <p className="text-sm font-medium">Failed to load snippet</p>
        <p className="text-xs text-gray-500">{(snippetQuery.error as Error)?.message}</p>
        <button
          onClick={() => snippetQuery.refetch()}
          className="mt-2 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700"
        >
          Retry
        </button>
      </div>
    );
  }

  /* ── Form mode (create / edit) ───────────────────────────────────────── */
  if (isFormMode) {
    return (
      <div
        className="flex-1 flex flex-col overflow-hidden"
        onKeyDown={handleKeyDown}
      >
        {/* Toolbar */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-200 shrink-0 bg-gray-50">
          <h2 className="text-sm font-semibold text-gray-700 flex-1">
            {isCreating ? 'New Snippet' : 'Edit Snippet'}
          </h2>
          <button
            onClick={handleSave}
            disabled={isSaving || !form.body?.trim()}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-3.5 h-3.5" />
            {isSaving ? 'Saving…' : 'Save'}
          </button>
          <button
            onClick={() => (isCreating ? onCancelCreate() : setIsEditing(false))}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900"
          >
            Cancel
          </button>
        </div>

        {/* Form fields */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Title */}
          <div>
            <label htmlFor="snippet-title" className="block text-xs font-medium text-gray-600 mb-1">
              Title <span className="text-gray-400">(auto-inferred if blank)</span>
            </label>
            <input
              id="snippet-title"
              type="text"
              value={form.title ?? ''}
              onChange={(e) => handleFieldChange('title', e.target.value)}
              placeholder="Untitled snippet"
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
            />
          </div>

          {/* Body */}
          <div>
            <label htmlFor="snippet-body" className="block text-xs font-medium text-gray-600 mb-1">
              Body <span className="text-red-500">*</span>
            </label>
            <textarea
              id="snippet-body"
              ref={bodyRef}
              value={form.body ?? ''}
              onChange={(e) => handleFieldChange('body', e.target.value)}
              placeholder="Paste or type your snippet…"
              rows={14}
              className="w-full px-3 py-2 text-sm font-mono border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none resize-y"
            />
          </div>

          {/* Language + Source row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="snippet-language" className="block text-xs font-medium text-gray-600 mb-1">Language</label>
              <input
                id="snippet-language"
                type="text"
                value={form.language ?? ''}
                onChange={(e) => handleFieldChange('language', e.target.value)}
                placeholder="e.g. python, javascript"
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
              />
            </div>
            <div>
              <label htmlFor="snippet-source" className="block text-xs font-medium text-gray-600 mb-1">Source</label>
              <input
                id="snippet-source"
                type="text"
                value={form.source ?? ''}
                onChange={(e) => handleFieldChange('source', e.target.value)}
                placeholder="e.g. clipboard, manual"
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
              />
            </div>
          </div>

          {/* Source URL */}
          <div>
            <label htmlFor="snippet-url" className="block text-xs font-medium text-gray-600 mb-1">Source URL</label>
            <input
              id="snippet-url"
              type="url"
              value={form.source_url ?? ''}
              onChange={(e) => handleFieldChange('source_url', e.target.value)}
              placeholder="https://…"
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
            />
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="snippet-tags" className="block text-xs font-medium text-gray-600 mb-1">
              Tags <span className="text-gray-400">(comma-separated, auto-created)</span>
            </label>
            <input
              id="snippet-tags"
              type="text"
              value={form.tags_text}
              onChange={(e) => handleFieldChange('tags_text', e.target.value)}
              placeholder="react, hooks, patterns"
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
            />
          </div>

          {/* Collections */}
          <div>
            <label htmlFor="snippet-collections" className="block text-xs font-medium text-gray-600 mb-1">
              Collections <span className="text-gray-400">(comma-separated, auto-created)</span>
            </label>
            <input
              id="snippet-collections"
              type="text"
              value={form.collections_text}
              onChange={(e) => handleFieldChange('collections_text', e.target.value)}
              placeholder="My Project, Tutorials"
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
            />
          </div>
        </div>
      </div>
    );
  }

  /* ── Read view ───────────────────────────────────────────────────────── */
  if (!snippet) return null;

  const langClass = snippet.language ? `language-${snippet.language}` : '';

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center gap-1.5 px-4 py-2 border-b border-gray-200 shrink-0 bg-gray-50">
        <h2 className="text-sm font-semibold text-gray-900 flex-1 truncate">
          {snippet.title || 'Untitled'}
        </h2>

        <button
          onClick={() => {
            populateForm(snippet);
            setIsEditing(true);
          }}
          className="p-1.5 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
          aria-label="Edit snippet"
          title="Edit (⌘E)"
        >
          <Pencil className="w-4 h-4" />
        </button>
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
          aria-label="Copy body"
          title="Copy to clipboard"
        >
          {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
        </button>
        <button
          onClick={handlePin}
          className={cn(
            'p-1.5 rounded-md hover:bg-gray-200',
            snippet.pinned === 1 ? 'text-amber-500' : 'text-gray-500 hover:text-gray-700',
          )}
          aria-label={snippet.pinned === 1 ? 'Unpin' : 'Pin'}
          title={snippet.pinned === 1 ? 'Unpin' : 'Pin'}
        >
          {snippet.pinned === 1 ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
        </button>
        <button
          onClick={handleArchive}
          className="p-1.5 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
          aria-label={snippet.archived === 1 ? 'Unarchive' : 'Archive'}
          title={snippet.archived === 1 ? 'Unarchive' : 'Archive'}
        >
          {snippet.archived === 1 ? (
            <ArchiveRestore className="w-4 h-4" />
          ) : (
            <Archive className="w-4 h-4" />
          )}
        </button>

        {/* Delete with confirmation */}
        {confirmDelete ? (
          <div className="flex items-center gap-1 ml-1">
            <span className="text-xs text-red-600">Delete?</span>
            <button
              onClick={handleDelete}
              className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
              disabled={deleteMut.isPending}
            >
              {deleteMut.isPending ? '…' : 'Yes'}
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="px-2 py-1 text-xs text-gray-600 hover:text-gray-900"
            >
              No
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="p-1.5 rounded-md text-gray-500 hover:bg-red-100 hover:text-red-600"
            aria-label="Delete snippet"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Meta */}
        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
          {snippet.language && (
            <span className="flex items-center gap-1">
              <FileCode className="w-3.5 h-3.5" />
              {snippet.language}
            </span>
          )}
          {snippet.source && (
            <span>Source: {snippet.source}</span>
          )}
          {snippet.source_url && (
            <a
              href={snippet.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-brand-600 hover:underline"
            >
              <ExternalLink className="w-3 h-3" />
              link
            </a>
          )}
          <span>Created {formatDate(snippet.created_at)}</span>
          <span>Updated {formatDate(snippet.updated_at)}</span>
        </div>

        {/* Tags */}
        {snippet.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            <Tag className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
            {snippet.tags.map((t) => (
              <span
                key={t.id}
                className="text-xs px-2 py-0.5 rounded-full bg-brand-100 text-brand-700"
              >
                {t.name}
              </span>
            ))}
          </div>
        )}

        {/* Collections */}
        {snippet.collections.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {snippet.collections.map((c) => (
              <span
                key={c.id}
                className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: (c.color ?? '#7C5CFC') + '18',
                  color: c.color ?? '#7C5CFC',
                }}
              >
                <span className="text-[10px]">{c.icon ?? '📁'}</span>
                {c.name}
              </span>
            ))}
          </div>
        )}

        {/* Code body */}
        <div className="relative group">
          <pre className="rounded-lg bg-gray-900 p-4 overflow-x-auto text-sm">
            <code ref={codeRef} className={cn('text-sm', langClass)}>
              {snippet.body}
            </code>
          </pre>
          <button
            onClick={handleCopy}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded bg-gray-700 text-gray-300 hover:text-white"
            aria-label="Copy code"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Pinned / Archived badges */}
        <div className="flex gap-2">
          {snippet.pinned === 1 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 flex items-center gap-1">
              <Pin className="w-3 h-3" /> Pinned
            </span>
          )}
          {snippet.archived === 1 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-600 flex items-center gap-1">
              <Archive className="w-3 h-3" /> Archived
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
