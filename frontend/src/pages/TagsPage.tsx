import React, { useState } from 'react';
import {
  Tag as TagIcon,
  Plus,
  Pencil,
  Trash2,
  Check,
  X,
  Palette,
} from 'lucide-react';
import { useTags, useCreateTag, useUpdateTag, useDeleteTag } from '../hooks/useApi';
import { cn } from '../utils/helpers';
import type { TagOutWithCount } from '../types';

/* -------------------------------------------------------------------------- */
/*  Props                                                                     */
/* -------------------------------------------------------------------------- */
interface TagsPageProps {
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

/* -------------------------------------------------------------------------- */
/*  Preset colors                                                             */
/* -------------------------------------------------------------------------- */
const COLORS = [
  '#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#ef4444',
  '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4',
  '#3b82f6', '#64748b',
];

/* -------------------------------------------------------------------------- */
/*  Inline edit row                                                           */
/* -------------------------------------------------------------------------- */
interface EditRowState {
  tagId: string | null; // null = creating new
  name: string;
  color: string;
}

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */
export const TagsPage: React.FC<TagsPageProps> = ({ showToast }) => {
  const tagsQuery = useTags();
  const createTag = useCreateTag();
  const updateTag = useUpdateTag();
  const deleteTag = useDeleteTag();

  const [editRow, setEditRow] = useState<EditRowState | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const tags: TagOutWithCount[] = tagsQuery.data?.items ?? [];

  /* ── Start create ────────────────────────────────────────────────────── */
  const startCreate = () => {
    setEditRow({ tagId: null, name: '', color: COLORS[0] });
    setConfirmDeleteId(null);
  };

  /* ── Start edit ──────────────────────────────────────────────────────── */
  const startEdit = (t: TagOutWithCount) => {
    setEditRow({ tagId: t.id, name: t.name, color: t.color ?? COLORS[0] });
    setConfirmDeleteId(null);
  };

  /* ── Cancel ──────────────────────────────────────────────────────────── */
  const cancel = () => setEditRow(null);

  /* ── Save (create or update) ─────────────────────────────────────────── */
  const save = async () => {
    if (!editRow || !editRow.name.trim()) return;
    try {
      if (editRow.tagId) {
        await updateTag.mutateAsync({
          id: editRow.tagId,
          data: { name: editRow.name.trim(), color: editRow.color },
        });
        showToast('Tag updated', 'success');
      } else {
        await createTag.mutateAsync({ name: editRow.name.trim(), color: editRow.color });
        showToast('Tag created', 'success');
      }
      setEditRow(null);
    } catch (e: any) {
      showToast(e.message || 'Failed', 'error');
    }
  };

  /* ── Delete ──────────────────────────────────────────────────────────── */
  const handleDelete = async (id: string) => {
    try {
      await deleteTag.mutateAsync(id);
      showToast('Tag deleted', 'success');
      setConfirmDeleteId(null);
    } catch (e: any) {
      showToast(e.message || 'Failed to delete', 'error');
    }
  };

  /* ── Loading ─────────────────────────────────────────────────────────── */
  if (tagsQuery.isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400" role="status">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="ml-2 text-sm">Loading tags…</span>
      </div>
    );
  }

  /* ── Error ───────────────────────────────────────────────────────────── */
  if (tagsQuery.isError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-500 gap-2 p-8">
        <p className="text-sm font-medium">Failed to load tags</p>
        <button
          onClick={() => tagsQuery.refetch()}
          className="mt-2 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <TagIcon className="w-5 h-5 text-brand-500" />
          Tags
          <span className="text-sm font-normal text-gray-400">({tags.length})</span>
        </h1>
        <button
          onClick={startCreate}
          disabled={editRow?.tagId === null}
          className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          New Tag
        </button>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium text-gray-600 dark:text-gray-300">Color</th>
              <th className="text-left px-4 py-2.5 font-medium text-gray-600 dark:text-gray-300">Name</th>
              <th className="text-right px-4 py-2.5 font-medium text-gray-600 dark:text-gray-300">Snippets</th>
              <th className="text-right px-4 py-2.5 font-medium text-gray-600 dark:text-gray-300 w-32">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {/* Create row */}
            {editRow && editRow.tagId === null && (
              <tr className="bg-brand-50">
                <td className="px-4 py-2">
                  <div className="flex gap-1 flex-wrap">
                    {COLORS.map((c) => (
                      <button
                        key={c}
                        onClick={() => setEditRow({ ...editRow, color: c })}
                        className={cn(
                          'w-5 h-5 rounded-full border-2 transition-transform',
                          editRow.color === c ? 'border-gray-900 scale-110' : 'border-transparent',
                        )}
                        style={{ backgroundColor: c }}
                        aria-label={`Color ${c}`}
                      />
                    ))}
                  </div>
                </td>
                <td className="px-4 py-2">
                  <input
                    autoFocus
                    type="text"
                    value={editRow.name}
                    onChange={(e) => setEditRow({ ...editRow, name: e.target.value })}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') save();
                      if (e.key === 'Escape') cancel();
                    }}
                    placeholder="Tag name"
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-brand-500 outline-none"
                  />
                </td>
                <td />
                <td className="px-4 py-2 text-right">
                  <button
                    onClick={save}
                    disabled={!editRow.name.trim() || createTag.isPending}
                    className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
                    aria-label="Save"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button onClick={cancel} className="p-1 text-gray-400 hover:text-gray-600" aria-label="Cancel">
                    <X className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            )}

            {/* Tag rows */}
            {tags.map((t) => {
              const isEditingThis = editRow?.tagId === t.id;
              const isDeletingThis = confirmDeleteId === t.id;

              return (
                <tr key={t.id} className={cn(isEditingThis && 'bg-brand-50')}>
                  {/* Color */}
                  <td className="px-4 py-2.5">
                    {isEditingThis ? (
                      <div className="flex gap-1 flex-wrap">
                        {COLORS.map((c) => (
                          <button
                            key={c}
                            onClick={() => setEditRow({ ...editRow!, color: c })}
                            className={cn(
                              'w-5 h-5 rounded-full border-2 transition-transform',
                              editRow!.color === c ? 'border-gray-900 scale-110' : 'border-transparent',
                            )}
                            style={{ backgroundColor: c }}
                            aria-label={`Color ${c}`}
                          />
                        ))}
                      </div>
                    ) : (
                      <span
                        className="inline-block w-4 h-4 rounded-full"
                        style={{ backgroundColor: t.color || COLORS[0] }}
                      />
                    )}
                  </td>

                  {/* Name */}
                  <td className="px-4 py-2.5">
                    {isEditingThis ? (
                      <input
                        autoFocus
                        type="text"
                        value={editRow!.name}
                        onChange={(e) => setEditRow({ ...editRow!, name: e.target.value })}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') save();
                          if (e.key === 'Escape') cancel();
                        }}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-brand-500 outline-none"
                      />
                    ) : (
                      <span className="text-gray-900 dark:text-gray-100">{t.name}</span>
                    )}
                  </td>

                  {/* Count */}
                  <td className="px-4 py-2.5 text-right text-gray-500 dark:text-gray-400">{t.count}</td>

                  {/* Actions */}
                  <td className="px-4 py-2.5 text-right">
                    {isEditingThis ? (
                      <>
                        <button
                          onClick={save}
                          disabled={!editRow!.name.trim() || updateTag.isPending}
                          className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
                          aria-label="Save"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button onClick={cancel} className="p-1 text-gray-400 hover:text-gray-600" aria-label="Cancel">
                          <X className="w-4 h-4" />
                        </button>
                      </>
                    ) : isDeletingThis ? (
                      <div className="flex items-center justify-end gap-1">
                        <span className="text-xs text-red-600">Delete?</span>
                        <button
                          onClick={() => handleDelete(t.id)}
                          disabled={deleteTag.isPending}
                          className="px-2 py-0.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                        >
                          Yes
                        </button>
                        <button
                          onClick={() => setConfirmDeleteId(null)}
                          className="px-2 py-0.5 text-xs text-gray-600 hover:text-gray-900"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => startEdit(t)}
                          className="p-1 text-gray-400 hover:text-gray-700"
                          aria-label="Edit tag"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setConfirmDeleteId(t.id)}
                          className="p-1 text-gray-400 hover:text-red-600"
                          aria-label="Delete tag"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}

            {/* Empty */}
            {tags.length === 0 && !editRow && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-400 text-sm">
                  No tags yet. Click <strong>+ New Tag</strong> to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
