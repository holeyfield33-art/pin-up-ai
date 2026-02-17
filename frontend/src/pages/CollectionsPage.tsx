import React, { useState } from 'react';
import {
  Folder,
  Plus,
  Pencil,
  Trash2,
  Check,
  X,
  FileText,
} from 'lucide-react';
import { useCollections, useCreateCollection, useUpdateCollection, useDeleteCollection } from '../hooks/useApi';
import { cn, formatDate } from '../utils/helpers';
import type { CollectionOutWithCount } from '../types';

/* -------------------------------------------------------------------------- */
/*  Presets                                                                   */
/* -------------------------------------------------------------------------- */
const ICONS = ['📁', '📂', '🗂️', '📦', '🔖', '⭐', '💡', '🚀', '🔧', '🎨', '📝', '🧩', '🐛', '🛡️', '📊', '🌐'];
const COLORS = [
  '#7C5CFC', '#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#ef4444',
  '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6',
];

/* -------------------------------------------------------------------------- */
/*  Props                                                                     */
/* -------------------------------------------------------------------------- */
interface CollectionsPageProps {
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

/* -------------------------------------------------------------------------- */
/*  Edit row                                                                  */
/* -------------------------------------------------------------------------- */
interface EditRowState {
  collectionId: string | null; // null = creating new
  name: string;
  description: string;
  icon: string;
  color: string;
}

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */
export const CollectionsPage: React.FC<CollectionsPageProps> = ({ showToast }) => {
  const collectionsQuery = useCollections();
  const createMut = useCreateCollection();
  const updateMut = useUpdateCollection();
  const deleteMut = useDeleteCollection();

  const [editRow, setEditRow] = useState<EditRowState | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const collections: CollectionOutWithCount[] = collectionsQuery.data?.items ?? [];

  /* ── Start create ────────────────────────────────────────────────────── */
  const startCreate = () => {
    setEditRow({ collectionId: null, name: '', description: '', icon: ICONS[0], color: COLORS[0] });
    setConfirmDeleteId(null);
  };

  /* ── Start edit ──────────────────────────────────────────────────────── */
  const startEdit = (c: CollectionOutWithCount) => {
    setEditRow({
      collectionId: c.id,
      name: c.name,
      description: c.description ?? '',
      icon: c.icon ?? ICONS[0],
      color: c.color ?? COLORS[0],
    });
    setConfirmDeleteId(null);
  };

  /* ── Cancel ──────────────────────────────────────────────────────────── */
  const cancel = () => setEditRow(null);

  /* ── Save ────────────────────────────────────────────────────────────── */
  const save = async () => {
    if (!editRow || !editRow.name.trim()) return;
    try {
      if (editRow.collectionId) {
        await updateMut.mutateAsync({
          id: editRow.collectionId,
          data: {
            name: editRow.name.trim(),
            description: editRow.description.trim() || undefined,
            icon: editRow.icon,
            color: editRow.color,
          },
        });
        showToast('Collection updated', 'success');
      } else {
        await createMut.mutateAsync({
          name: editRow.name.trim(),
          description: editRow.description.trim() || undefined,
          icon: editRow.icon,
          color: editRow.color,
        });
        showToast('Collection created', 'success');
      }
      setEditRow(null);
    } catch (e: any) {
      showToast(e.message || 'Failed', 'error');
    }
  };

  /* ── Delete ──────────────────────────────────────────────────────────── */
  const handleDelete = async (id: string) => {
    try {
      await deleteMut.mutateAsync(id);
      showToast('Collection deleted', 'success');
      setConfirmDeleteId(null);
    } catch (e: any) {
      showToast(e.message || 'Failed to delete', 'error');
    }
  };

  /* ── Loading ─────────────────────────────────────────────────────────── */
  if (collectionsQuery.isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400" role="status">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="ml-2 text-sm">Loading collections…</span>
      </div>
    );
  }

  /* ── Error ───────────────────────────────────────────────────────────── */
  if (collectionsQuery.isError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-500 gap-2 p-8">
        <p className="text-sm font-medium">Failed to load collections</p>
        <button
          onClick={() => collectionsQuery.refetch()}
          className="mt-2 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700"
        >
          Retry
        </button>
      </div>
    );
  }

  /* ── Shared form (used for both create and inline edit) ──────────────── */
  const renderForm = (isInline: boolean) => {
    if (!editRow) return null;
    const isPending = editRow.collectionId ? updateMut.isPending : createMut.isPending;
    const actionLabel = editRow.collectionId ? 'Save' : 'Create';

    return (
      <div className={cn(
        'bg-white dark:bg-gray-800 border-2 rounded-lg p-4 space-y-3',
        'border-brand-300 dark:border-brand-600',
      )}>
        <input
          autoFocus
          type="text"
          value={editRow.name}
          onChange={(e) => setEditRow({ ...editRow, name: e.target.value })}
          onKeyDown={(e) => {
            if (e.key === 'Enter') save();
            if (e.key === 'Escape') cancel();
          }}
          placeholder="Collection name"
          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none bg-white dark:bg-gray-900 dark:text-gray-100"
        />
        <textarea
          value={editRow.description}
          onChange={(e) => setEditRow({ ...editRow, description: e.target.value })}
          placeholder="Description (optional)"
          rows={2}
          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none resize-none bg-white dark:bg-gray-900 dark:text-gray-100"
        />

        {/* Icon picker */}
        <div>
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Icon</span>
          <div className="flex gap-1 flex-wrap mt-1">
            {ICONS.map((ic) => (
              <button
                key={ic}
                onClick={() => setEditRow({ ...editRow, icon: ic })}
                className={cn(
                  'w-7 h-7 rounded text-base flex items-center justify-center border-2 transition-transform',
                  editRow.icon === ic
                    ? 'border-brand-500 scale-110 bg-brand-100 dark:bg-brand-900/30'
                    : 'border-transparent hover:bg-gray-100 dark:hover:bg-gray-700',
                )}
              >
                {ic}
              </button>
            ))}
          </div>
        </div>

        {/* Color picker */}
        <div>
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Color</span>
          <div className="flex gap-1 flex-wrap mt-1">
            {COLORS.map((clr) => (
              <button
                key={clr}
                onClick={() => setEditRow({ ...editRow, color: clr })}
                className={cn(
                  'w-5 h-5 rounded-full border-2 transition-transform',
                  editRow.color === clr
                    ? 'border-gray-900 dark:border-white scale-110'
                    : 'border-transparent',
                )}
                style={{ backgroundColor: clr }}
                aria-label={`Color ${clr}`}
              />
            ))}
          </div>
        </div>

        <div className="flex gap-2 justify-end">
          <button
            onClick={save}
            disabled={!editRow.name.trim() || isPending}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
          >
            <Check className="w-3.5 h-3.5" />
            {actionLabel}
          </button>
          <button
            onClick={cancel}
            className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  };

  /* ── Render ──────────────────────────────────────────────────────────── */
  return (
    <div className="flex-1 overflow-y-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100">Collections</h1>
        <button
          onClick={startCreate}
          disabled={!!editRow}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          New Collection
        </button>
      </div>

      {/* Grid */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {/* New collection form */}
        {editRow && !editRow.collectionId && renderForm(false)}

        {/* Collection cards */}
        {collections.map((c) => {
          const isEditingThis = editRow?.collectionId === c.id;
          const isDeletingThis = confirmDeleteId === c.id;

          return (
            <div
              key={c.id}
              className={cn(
                'bg-white dark:bg-gray-800 border rounded-lg p-4 space-y-2 transition-shadow hover:shadow-sm',
                isEditingThis
                  ? 'border-brand-300 bg-brand-50 dark:bg-gray-800'
                  : 'border-gray-200 dark:border-gray-700',
              )}
              style={{ borderLeftWidth: 3, borderLeftColor: c.color ?? '#7C5CFC' }}
            >
              {isEditingThis ? (
                renderForm(true)
              ) : (
                <>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-6 h-6 rounded flex items-center justify-center text-sm shrink-0"
                        style={{ backgroundColor: (c.color ?? '#7C5CFC') + '20' }}
                      >
                        {c.icon ?? '📁'}
                      </span>
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{c.name}</h3>
                    </div>
                    <div className="flex items-center gap-0.5 shrink-0">
                      <button
                        onClick={() => startEdit(c)}
                        className="p-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                        aria-label="Edit collection"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setConfirmDeleteId(c.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        aria-label="Delete collection"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {c.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{c.description}</p>
                  )}

                  <div className="flex items-center gap-3 text-xs text-gray-400 pt-1">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {c.count} snippet{c.count !== 1 ? 's' : ''}
                    </span>
                    <span>Created {formatDate(c.created_at)}</span>
                  </div>

                  {/* Delete confirmation */}
                  {isDeletingThis && (
                    <div className="flex items-center gap-2 pt-1 border-t border-gray-100 dark:border-gray-700 mt-2">
                      <span className="text-xs text-red-600">Delete this collection?</span>
                      <button
                        onClick={() => handleDelete(c.id)}
                        disabled={deleteMut.isPending}
                        className="px-2 py-0.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setConfirmDeleteId(null)}
                        className="px-2 py-0.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                      >
                        No
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}

        {/* Empty */}
        {collections.length === 0 && !editRow && (
          <div className="col-span-full flex flex-col items-center justify-center py-12 text-gray-400">
            <Folder className="w-8 h-8 mb-2" />
            <p className="text-sm">No collections yet</p>
            <p className="text-xs mt-1">
              Click <strong>+ New Collection</strong> to organize your snippets
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
