import React, { useState, useRef } from 'react';
import {
  Settings as SettingsIcon,
  Shield,
  Database,
  Download,
  Upload,
  Key,
  RefreshCw,
  Save,
  Check,
  AlertTriangle,
  Trash2,
  HardDrive,
  Clock,
} from 'lucide-react';
import {
  useSettings,
  useUpdateSettings,
  useLicense,
  useActivateLicense,
  useDeactivateLicense,
  useBackups,
  useRunBackup,
  useRestoreBackup,
  useExportJson,
  useImportFile,
} from '../hooks/useApi';
import { settingsAPI } from '../api/client';
import { setBootstrap, getBaseUrl, getToken } from '../api/client';
import { cn, formatDate, formatBytes } from '../utils/helpers';

/* -------------------------------------------------------------------------- */
/*  Props                                                                     */
/* -------------------------------------------------------------------------- */
interface SettingsPageProps {
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

/* -------------------------------------------------------------------------- */
/*  Section wrapper                                                           */
/* -------------------------------------------------------------------------- */
const Section: React.FC<{
  title: string;
  icon: React.ElementType;
  iconColor?: string;
  children: React.ReactNode;
}> = ({ title, icon: Icon, iconColor = 'text-brand-500', children }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-4">
    <h2 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
      <Icon className={cn('w-4 h-4', iconColor)} />
      {title}
    </h2>
    {children}
  </div>
);

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */
export const SettingsPage: React.FC<SettingsPageProps> = ({ showToast }) => {
  /* ── Data ────────────────────────────────────────────────────────────── */
  const settingsQuery = useSettings();
  const updateSettings = useUpdateSettings();
  const licenseQuery = useLicense();
  const activateLicense = useActivateLicense();
  const deactivateLicense = useDeactivateLicense();
  const backupsQuery = useBackups();
  const runBackup = useRunBackup();
  const restoreBackup = useRestoreBackup();
  const exportJson = useExportJson();
  const importFile = useImportFile();

  const settings = settingsQuery.data;
  const license = licenseQuery.data;
  const backups = backupsQuery.data?.items ?? [];

  /* ── Local state ─────────────────────────────────────────────────────── */
  const [licenseKey, setLicenseKey] = useState('');
  const [confirmRestore, setConfirmRestore] = useState<string | null>(null);
  const [rotatingToken, setRotatingToken] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /* ── Handlers ────────────────────────────────────────────────────────── */
  const handleToggleDedupe = () => {
    if (!settings) return;
    updateSettings.mutate(
      { dedupe_enabled: !settings.dedupe_enabled },
      {
        onSuccess: () => showToast('Settings saved', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      },
    );
  };

  const handleToggleBackup = () => {
    if (!settings) return;
    updateSettings.mutate(
      { backup_enabled: !settings.backup_enabled },
      {
        onSuccess: () => showToast('Settings saved', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      },
    );
  };

  const handleActivateLicense = () => {
    if (!licenseKey.trim()) return;
    activateLicense.mutate(licenseKey.trim(), {
      onSuccess: () => {
        showToast('License activated!', 'success');
        setLicenseKey('');
      },
      onError: (e) => showToast(e.message, 'error'),
    });
  };

  const handleDeactivateLicense = () => {
    deactivateLicense.mutate(undefined, {
      onSuccess: () => showToast('License deactivated', 'info'),
      onError: (e) => showToast(e.message, 'error'),
    });
  };

  const handleRunBackup = () => {
    runBackup.mutate(undefined, {
      onSuccess: () => showToast('Backup created', 'success'),
      onError: (e) => showToast(e.message, 'error'),
    });
  };

  const handleRestore = (name: string) => {
    restoreBackup.mutate(name, {
      onSuccess: () => {
        showToast('Backup restored — data reloaded', 'success');
        setConfirmRestore(null);
      },
      onError: (e) => showToast(e.message, 'error'),
    });
  };

  const handleExportJson = () => {
    exportJson.mutate(
      {},
      {
        onSuccess: (data) => {
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `pinup-export-${Date.now()}.json`;
          a.click();
          URL.revokeObjectURL(url);
          showToast('Export downloaded', 'success');
        },
        onError: (e) => showToast(e.message, 'error'),
      },
    );
  };

  const handleImportFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    importFile.mutate(file, {
      onSuccess: (result) => {
        const counts = result.imported;
        const total = Object.values(counts).reduce((a, b) => a + (b as number), 0);
        showToast(`Imported ${total} items`, 'success');
      },
      onError: (err) => showToast(err.message, 'error'),
    });
    // Reset input
    e.target.value = '';
  };

  const handleRotateToken = async () => {
    setRotatingToken(true);
    try {
      const result = await settingsAPI.rotateToken();
      // Update the client with the new token
      setBootstrap(getBaseUrl(), result.token);
      showToast('API token rotated. New token applied.', 'success');
    } catch (e: any) {
      showToast(e.message || 'Failed to rotate token', 'error');
    } finally {
      setRotatingToken(false);
    }
  };

  /* ── Loading ─────────────────────────────────────────────────────────── */
  if (settingsQuery.isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400" role="status">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="ml-2 text-sm">Loading settings…</span>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
        <SettingsIcon className="w-5 h-5 text-brand-500" />
        Settings
      </h1>

      {/* ── General Settings ───────────────────────────────────────────── */}
      <Section title="General" icon={SettingsIcon}>
        {/* Dedupe */}
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm text-gray-700 font-medium">Deduplicate on import</p>
            <p className="text-xs text-gray-500">Skip snippets with identical content hash</p>
          </div>
          <button
            role="switch"
            aria-checked={settings?.dedupe_enabled ?? false}
            onClick={handleToggleDedupe}
            className={cn(
              'relative w-10 h-6 rounded-full transition-colors',
              settings?.dedupe_enabled ? 'bg-brand-600' : 'bg-gray-300',
            )}
          >
            <span
              className={cn(
                'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                settings?.dedupe_enabled && 'translate-x-4',
              )}
            />
          </button>
        </label>

        {/* Auto-backup */}
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm text-gray-700 font-medium">Auto-backup</p>
            <p className="text-xs text-gray-500">
              Schedule: {settings?.backup_schedule || 'daily'}
            </p>
          </div>
          <button
            role="switch"
            aria-checked={settings?.backup_enabled ?? false}
            onClick={handleToggleBackup}
            className={cn(
              'relative w-10 h-6 rounded-full transition-colors',
              settings?.backup_enabled ? 'bg-brand-600' : 'bg-gray-300',
            )}
          >
            <span
              className={cn(
                'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                settings?.backup_enabled && 'translate-x-4',
              )}
            />
          </button>
        </label>
      </Section>

      {/* ── License ────────────────────────────────────────────────────── */}
      <Section title="License" icon={Shield} iconColor="text-indigo-600">
        {license && (
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <span className="text-gray-500">Status:</span>
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
              <span className="text-gray-400 text-xs ml-auto">
                {license.days_left} day{license.days_left !== 1 ? 's' : ''} left
              </span>
            </div>

            {license.status !== 'licensed_active' && (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={licenseKey}
                  onChange={(e) => setLicenseKey(e.target.value)}
                  placeholder="Enter license key"
                  className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleActivateLicense()}
                />
                <button
                  onClick={handleActivateLicense}
                  disabled={!licenseKey.trim() || activateLicense.isPending}
                  className="px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
                >
                  {activateLicense.isPending ? 'Activating…' : 'Activate'}
                </button>
              </div>
            )}

            {license.status === 'licensed_active' && (
              <button
                onClick={handleDeactivateLicense}
                disabled={deactivateLicense.isPending}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                Deactivate license
              </button>
            )}
          </div>
        )}
      </Section>

      {/* ── Export / Import ─────────────────────────────────────────────── */}
      <Section title="Export & Import" icon={Download} iconColor="text-green-600">
        <p className="text-xs text-gray-500">
          Export always works regardless of license status.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleExportJson}
            disabled={exportJson.isPending}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            {exportJson.isPending ? 'Exporting…' : 'Export JSON'}
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={importFile.isPending}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <Upload className="w-4 h-4" />
            {importFile.isPending ? 'Importing…' : 'Import'}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.zip"
            onChange={handleImportFile}
            className="hidden"
            aria-label="Choose file to import"
          />
        </div>
      </Section>

      {/* ── Backup & Restore ───────────────────────────────────────────── */}
      <Section title="Backup & Restore" icon={Database} iconColor="text-blue-600">
        <div className="flex items-center gap-3 mb-3">
          <button
            onClick={handleRunBackup}
            disabled={runBackup.isPending}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
          >
            <HardDrive className="w-4 h-4" />
            {runBackup.isPending ? 'Creating…' : 'Create Backup'}
          </button>
        </div>

        {backups.length === 0 ? (
          <p className="text-xs text-gray-400">No backups yet</p>
        ) : (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-3 py-2 font-medium text-gray-600">Name</th>
                  <th className="text-left px-3 py-2 font-medium text-gray-600">Created</th>
                  <th className="text-right px-3 py-2 font-medium text-gray-600">Size</th>
                  <th className="text-right px-3 py-2 font-medium text-gray-600 w-24">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {backups.map((b) => (
                  <tr key={b.name}>
                    <td className="px-3 py-2 text-gray-700 font-mono text-xs">{b.name}</td>
                    <td className="px-3 py-2 text-gray-500 text-xs flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(b.created_at)}
                    </td>
                    <td className="px-3 py-2 text-gray-500 text-xs text-right">
                      {formatBytes(b.db_size_bytes)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {confirmRestore === b.name ? (
                        <div className="flex items-center justify-end gap-1">
                          <span className="text-[11px] text-red-600">Restore?</span>
                          <button
                            onClick={() => handleRestore(b.name)}
                            disabled={restoreBackup.isPending}
                            className="px-2 py-0.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                          >
                            Yes
                          </button>
                          <button
                            onClick={() => setConfirmRestore(null)}
                            className="px-2 py-0.5 text-xs text-gray-600"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmRestore(b.name)}
                          className="text-xs text-brand-600 hover:text-brand-800 underline"
                        >
                          Restore
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>

      {/* ── Security ───────────────────────────────────────────────────── */}
      <Section title="Security" icon={Key} iconColor="text-amber-600">
        <p className="text-xs text-gray-500 mb-2">
          Rotate the API bearer token. The current token will be replaced immediately.
        </p>
        <button
          onClick={handleRotateToken}
          disabled={rotatingToken}
          className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border border-amber-300 text-amber-700 rounded-lg hover:bg-amber-50 disabled:opacity-50"
        >
          <RefreshCw className={cn('w-4 h-4', rotatingToken && 'animate-spin')} />
          {rotatingToken ? 'Rotating…' : 'Rotate API Token'}
        </button>
      </Section>
    </div>
  );
};
