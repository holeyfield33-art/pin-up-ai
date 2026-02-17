import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { setBootstrap } from './api/client';
import './index.css';

// ── Apply stored theme immediately (avoid flash) ────────────────────────────
(function applyInitialTheme() {
  const stored = localStorage.getItem('pinup_theme') || 'system';
  const isDark = stored === 'dark' || (stored === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', isDark);
})();

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5_000,
      refetchOnWindowFocus: false,
    },
  },
});

// ── Tauri bootstrap ─────────────────────────────────────────────────────────
// When running inside Tauri, fetch backend URL + token from Rust IPC.
// In dev mode (no Tauri), falls back to VITE_API_URL / VITE_API_TOKEN env vars.
async function bootstrap() {
  if (typeof window !== 'undefined' && (window as any).__TAURI__) {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      const config = await invoke<{ base_url: string; token: string; data_dir: string }>(
        'get_bootstrap',
      );
      setBootstrap(config.base_url, config.token);
    } catch (e) {
      console.warn('Tauri bootstrap failed, using env defaults:', e);
    }
  }
}

bootstrap().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </React.StrictMode>,
  );
});
