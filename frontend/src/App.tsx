import React, { useEffect, useCallback, useState } from 'react';
import { useAppStore } from './stores/appStore';
import { useHealth, useTags, useCollections, useCreateTag, useCreateCollection, useLicense } from './hooks/useApi';
import { useToast } from './hooks/useToast';

import { Sidebar } from './components/Sidebar';
import { Toast } from './components/Toast';
import { WelcomeWizard } from './components/WelcomeWizard';
import { ShortcutHelp } from './components/ShortcutHelp';
import { UpgradePrompt } from './components/UpgradePrompt';
import { ErrorBoundary } from './components/ErrorBoundary';
import { SnippetsPage } from './pages/SnippetsPage';
import { DashboardPage } from './pages/DashboardPage';
import { TagsPage } from './pages/TagsPage';
import { CollectionsPage } from './pages/CollectionsPage';
import { SettingsPage } from './pages/SettingsPage';

export default function App() {
  const page = useAppStore((s) => s.page);
  const setPage = useAppStore((s) => s.setPage);
  const setBackendStatus = useAppStore((s) => s.setBackendStatus);
  const setIsCreating = useAppStore((s) => s.setIsCreating);
  const { toast, showToast, hideToast } = useToast();

  // Onboarding state
  const [showWizard, setShowWizard] = React.useState(() => {
    return localStorage.getItem('pinup_onboarding_complete') !== 'true';
  });

  // Shortcut help modal
  const [showShortcuts, setShowShortcuts] = useState(false);

  // License & upgrade prompts
  const licenseQuery = useLicense();
  const license = licenseQuery.data;
  const [upgradeDismissed, setUpgradeDismissed] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const needsUpgrade = license && !license.entitled && license.status === 'trial_expired';
  const showUpgradeBanner = license && !license.entitled && !upgradeDismissed;
  const isGracePeriod = license?.status === 'grace_period';

  const goToLicenseSettings = useCallback(() => {
    setShowUpgradeModal(false);
    setPage('settings');
  }, [setPage]);

  const handleWizardComplete = useCallback(() => {
    localStorage.setItem('pinup_onboarding_complete', 'true');
    setShowWizard(false);
  }, []);

  // Global keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      if (!meta) return;

      switch (e.key.toLowerCase()) {
        case 'n':
          e.preventDefault();
          setPage('snippets');
          setIsCreating(true);
          break;
        case ',':
          e.preventDefault();
          setPage('settings');
          break;
        case 'e':
          e.preventDefault();
          setPage('settings'); // Export is in settings
          break;
      }
      // ⌘? or ⌘/ for shortcut help
      if (e.key === '?' || e.key === '/') {
        e.preventDefault();
        setShowShortcuts((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [setPage, setIsCreating]);

  // Health polling
  const healthQuery = useHealth();
  useEffect(() => {
    if (healthQuery.isSuccess) setBackendStatus('connected');
    else if (healthQuery.isError) setBackendStatus('error');
    else if (healthQuery.isLoading) setBackendStatus('checking');
  }, [healthQuery.status, setBackendStatus]);

  // Tags & collections for sidebar
  const tagsQuery = useTags();
  const collectionsQuery = useCollections();

  const createTag = useCreateTag();
  const createCollection = useCreateCollection();

  const handleCreateTag = () => {
    const name = prompt('Tag name:');
    if (name?.trim()) {
      createTag.mutate({ name: name.trim() }, {
        onSuccess: () => showToast('Tag created', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      });
    }
  };

  const handleCreateCollection = () => {
    const name = prompt('Collection name:');
    if (name?.trim()) {
      createCollection.mutate({ name: name.trim() }, {
        onSuccess: () => showToast('Collection created', 'success'),
        onError: (e) => showToast(e.message, 'error'),
      });
    }
  };

  const renderPage = () => {
    switch (page) {
      case 'snippets':
        return <SnippetsPage showToast={showToast} onSnippetLimit={() => setShowUpgradeModal(true)} />;
      case 'dashboard':
        return <DashboardPage />;
      case 'tags':
        return <TagsPage showToast={showToast} />;
      case 'collections':
        return <CollectionsPage showToast={showToast} />;
      case 'settings':
        return <SettingsPage showToast={showToast} />;
      default:
        return <SnippetsPage showToast={showToast} />;
    }
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      {/* Onboarding wizard for first-run */}
      {showWizard && (
        <WelcomeWizard onComplete={handleWizardComplete} />
      )}

      <Sidebar
        tags={tagsQuery.data?.items ?? []}
        collections={collectionsQuery.data?.items ?? []}
        onCreateTag={handleCreateTag}
        onCreateCollection={handleCreateCollection}
      />

      <main className="flex-1 flex flex-col overflow-hidden bg-white dark:bg-gray-950">
        {/* Upgrade banner for expired trial or grace period */}
        {showUpgradeBanner && (
          <UpgradePrompt
            variant="banner"
            reason={needsUpgrade ? 'trial_expired' : isGracePeriod ? 'feature_locked' : 'generic'}
            daysLeft={license?.days_left}
            onActivate={goToLicenseSettings}
            onDismiss={() => setUpgradeDismissed(true)}
          />
        )}
        <ErrorBoundary>
          {renderPage()}
        </ErrorBoundary>
      </main>

      {/* Toast overlay */}
      {toast && (
        <div className="fixed top-4 right-4 z-50">
          <Toast message={toast.message} type={toast.type} onClose={hideToast} />
        </div>
      )}

      {/* Upgrade modal (triggered by snippet limit error) */}
      {showUpgradeModal && (
        <UpgradePrompt
          variant="modal"
          reason={needsUpgrade ? 'trial_expired' : 'snippet_limit'}
          daysLeft={license?.days_left}
          onActivate={goToLicenseSettings}
          onDismiss={() => setShowUpgradeModal(false)}
        />
      )}

      {/* Keyboard shortcut help */}
      <ShortcutHelp isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </div>
  );
}
