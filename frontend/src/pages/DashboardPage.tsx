import React from 'react';
import {
  FileText,
  Tag,
  Folder,
  Pin,
  Archive,
  HardDrive,
  TrendingUp,
  Activity,
  Plus,
  Download,
  Upload,
  Database,
  Shield,
} from 'lucide-react';
import { useStats, useLicense } from '../hooks/useApi';
import { useAppStore } from '../stores/appStore';
import { formatBytes, formatDate } from '../utils/helpers';
import { cn } from '../utils/helpers';

/* -------------------------------------------------------------------------- */
/*  Stat Card                                                                 */
/* -------------------------------------------------------------------------- */
interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon: Icon, color = 'text-brand-600' }) => (
  <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-3">
    <div className={cn('p-2 rounded-lg bg-gray-50', color)}>
      <Icon className="w-5 h-5" />
    </div>
    <div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  </div>
);

/* -------------------------------------------------------------------------- */
/*  Page                                                                      */
/* -------------------------------------------------------------------------- */
export const DashboardPage: React.FC = () => {
  const statsQuery = useStats();
  const licenseQuery = useLicense();
  const setPage = useAppStore((s) => s.setPage);

  const stats = statsQuery.data;
  const license = licenseQuery.data;

  /* ── Loading ─────────────────────────────────────────────────────────── */
  if (statsQuery.isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400" role="status">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="ml-2 text-sm">Loading dashboard…</span>
      </div>
    );
  }

  /* ── Error ───────────────────────────────────────────────────────────── */
  if (statsQuery.isError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-500 gap-2 p-8">
        <p className="text-sm font-medium">Failed to load stats</p>
        <button
          onClick={() => statsQuery.refetch()}
          className="mt-2 px-3 py-1.5 text-xs font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const totals = stats?.totals ?? { snippets: 0, tags: 0, collections: 0, pinned: 0, archived: 0 };
  const topTags = stats?.top_tags ?? [];
  const topCollections = stats?.top_collections ?? [];
  const vault = stats?.vault ?? { db_size_bytes: 0, fts_entries: 0 };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>

      {/* ── Totals grid ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard label="Snippets" value={totals.snippets} icon={FileText} />
        <StatCard label="Tags" value={totals.tags} icon={Tag} color="text-purple-600" />
        <StatCard label="Collections" value={totals.collections} icon={Folder} color="text-blue-600" />
        <StatCard label="Pinned" value={totals.pinned} icon={Pin} color="text-amber-500" />
        <StatCard label="Archived" value={totals.archived} icon={Archive} color="text-gray-500" />
      </div>

      {/* ── Two-column: top tags + top collections ─────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Tags */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-brand-500" />
            Top Tags
          </h2>
          {topTags.length === 0 ? (
            <p className="text-xs text-gray-400">No tags yet</p>
          ) : (
            <div className="space-y-2">
              {topTags.slice(0, 10).map((t) => (
                <div key={t.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{t.name}</span>
                  <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                    {t.count}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Collections */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            Top Collections
          </h2>
          {topCollections.length === 0 ? (
            <p className="text-xs text-gray-400">No collections yet</p>
          ) : (
            <div className="space-y-2">
              {topCollections.slice(0, 10).map((c) => (
                <div key={c.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{c.name}</span>
                  <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                    {c.count}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Vault health + License ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Vault Health */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-green-600" />
            Vault Health
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Database size</span>
              <span className="font-medium text-gray-700">{formatBytes(vault.db_size_bytes)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">FTS entries</span>
              <span className="font-medium text-gray-700">{vault.fts_entries}</span>
            </div>
          </div>
        </div>

        {/* License Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-600" />
            License
          </h2>
          {license ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Status</span>
                <span
                  className={cn(
                    'font-medium px-2 py-0.5 rounded-full text-xs',
                    license.status === 'licensed_active'
                      ? 'bg-green-100 text-green-700'
                      : license.status === 'trial_active'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-red-100 text-red-700',
                  )}
                >
                  {license.status.replace(/_/g, ' ')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Days left</span>
                <span className="font-medium text-gray-700">{license.days_left}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Plan</span>
                <span className="font-medium text-gray-700">{license.plan}</span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-gray-400">Loading…</p>
          )}
        </div>
      </div>

      {/* ── Quick Actions ──────────────────────────────────────────────── */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-500" />
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setPage('snippets')}
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700"
          >
            <Plus className="w-4 h-4" />
            New Snippet
          </button>
          <button
            onClick={() => setPage('settings')}
            className="flex items-center gap-1.5 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => setPage('settings')}
            className="flex items-center gap-1.5 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <Upload className="w-4 h-4" />
            Import
          </button>
          <button
            onClick={() => setPage('settings')}
            className="flex items-center gap-1.5 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <Database className="w-4 h-4" />
            Backup
          </button>
        </div>
      </div>
    </div>
  );
};
