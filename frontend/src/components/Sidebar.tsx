import React from 'react';
import {
  LayoutDashboard,
  FileText,
  Tag,
  Folder,
  Settings,
  Circle,
  Plus,
  Sun,
  Moon,
  Monitor,
} from 'lucide-react';
import { cn } from '../utils/helpers';
import { useAppStore } from '../stores/appStore';
import { useLicense } from '../hooks/useApi';
import { UpgradePrompt } from './UpgradePrompt';
import type { TagOutWithCount, CollectionOutWithCount, Page } from '../types';

interface SidebarProps {
  tags: TagOutWithCount[];
  collections: CollectionOutWithCount[];
  onCreateTag: () => void;
  onCreateCollection: () => void;
}

const NAV_ITEMS: { page: Page; label: string; icon: React.ElementType }[] = [
  { page: 'snippets', label: 'Snippets', icon: FileText },
  { page: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { page: 'tags', label: 'Tags', icon: Tag },
  { page: 'collections', label: 'Collections', icon: Folder },
  { page: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  tags,
  collections,
  onCreateTag,
  onCreateCollection,
}) => {
  const page = useAppStore((s) => s.page);
  const setPage = useAppStore((s) => s.setPage);
  const selectedTag = useAppStore((s) => s.selectedTag);
  const setSelectedTag = useAppStore((s) => s.setSelectedTag);
  const selectedCollection = useAppStore((s) => s.selectedCollection);
  const setSelectedCollection = useAppStore((s) => s.setSelectedCollection);
  const backendStatus = useAppStore((s) => s.backendStatus);
  const theme = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);

  const licenseQuery = useLicense();
  const license = licenseQuery.data;
  const showUpgradeCard = license && license.plan === 'trial';

  const statusColor: Record<string, string> = {
    connected: 'text-green-500',
    error: 'text-red-500',
    checking: 'text-yellow-500',
    disconnected: 'text-gray-400',
  };

  return (
    <aside className="w-56 flex flex-col border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 shrink-0 overflow-y-auto">
      {/* App Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
        <span className="text-lg">📌</span>
        <span className="font-bold text-sm text-gray-900 dark:text-gray-100">Pin-Up AI</span>
        <Circle className={cn('ml-auto w-2.5 h-2.5', statusColor[backendStatus])} fill="currentColor" />
      </div>

      {/* Main Nav */}
      <nav className="px-2 py-2 space-y-0.5">
        {NAV_ITEMS.map(({ page: p, label, icon: Icon }) => (
          <button
            key={p}
            onClick={() => {
              setPage(p);
              if (p !== 'snippets') {
                setSelectedTag(null);
                setSelectedCollection(null);
              }
            }}
            className={cn(
              'w-full flex items-center gap-2.5 px-3 py-1.5 text-sm rounded-md transition-colors',
              page === p
                ? 'bg-brand-100 dark:bg-brand-700/20 text-brand-700 dark:text-brand-200 font-medium'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800',
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </nav>

      {/* Quick filters — only on snippets page */}
      {page === 'snippets' && (
        <>
          <div className="px-3 py-2 mt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Collections
              </span>
              <button
                onClick={onCreateCollection}
                className="text-gray-400 hover:text-brand-600"
                aria-label="New collection"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
            <button
              onClick={() => setSelectedCollection(null)}
              className={cn(
                'w-full text-left px-2 py-1 text-sm rounded transition-colors',
                !selectedCollection ? 'bg-brand-100 dark:bg-brand-700/20 text-brand-700 dark:text-brand-200 font-medium' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800',
              )}
            >
              All
            </button>
            {collections.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedCollection(c.name)}
                className={cn(
                  'w-full flex items-center justify-between px-2 py-1 text-sm rounded transition-colors',
                  selectedCollection === c.name
                    ? 'bg-brand-100 dark:bg-brand-700/20 text-brand-700 dark:text-brand-200 font-medium'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800',
                )}
              >
                <span className="flex items-center gap-1.5 truncate">
                  <span className="text-xs">{c.icon ?? '📁'}</span>
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: c.color ?? '#7C5CFC' }}
                  />
                  <span className="truncate">{c.name}</span>
                </span>
                <span className="text-xs text-gray-400">{c.count}</span>
              </button>
            ))}
          </div>

          <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Tags
              </span>
              <button
                onClick={onCreateTag}
                className="text-gray-400 hover:text-brand-600"
                aria-label="New tag"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
            <button
              onClick={() => setSelectedTag(null)}
              className={cn(
                'w-full text-left px-2 py-1 text-sm rounded transition-colors',
                !selectedTag ? 'bg-brand-100 dark:bg-brand-700/20 text-brand-700 dark:text-brand-200 font-medium' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800',
              )}
            >
              All
            </button>
            {tags.slice(0, 15).map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedTag(t.name)}
                className={cn(
                  'w-full flex items-center gap-2 px-2 py-1 text-sm rounded transition-colors',
                  selectedTag === t.name
                    ? 'bg-brand-100 dark:bg-brand-700/20 text-brand-700 dark:text-brand-200 font-medium'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800',
                )}
              >
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: t.color || '#6366f1' }}
                />
                <span className="truncate flex-1">{t.name}</span>
                <span className="text-xs text-gray-400">{t.count}</span>
              </button>
            ))}
          </div>
        </>
      )}

      <div className="flex-1" />

      {/* Upgrade prompt for free-tier users */}
      {showUpgradeCard && (
        <UpgradePrompt
          variant="card"
          reason={license.status === 'trial_expired' ? 'trial_expired' : 'generic'}
          daysLeft={license.days_left}
          onActivate={() => {
            setPage('settings');
          }}
        />
      )}

      {/* Theme toggle */}
      <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-1 rounded-lg bg-gray-200 dark:bg-gray-700 p-0.5">
          {([
            { value: 'light' as const, icon: Sun, label: 'Light' },
            { value: 'system' as const, icon: Monitor, label: 'System' },
            { value: 'dark' as const, icon: Moon, label: 'Dark' },
          ]).map(({ value, icon: Icon, label }) => (
            <button
              key={value}
              onClick={() => setTheme(value)}
              title={label}
              className={cn(
                'flex-1 flex items-center justify-center p-1.5 rounded-md text-xs transition-colors',
                theme === value
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
              )}
            >
              <Icon className="w-3.5 h-3.5" />
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
