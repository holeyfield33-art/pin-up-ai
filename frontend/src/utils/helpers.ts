export const KEYBOARD_SHORTCUTS = {
  SEARCH: { key: 'p', ctrl: true, label: 'Ctrl+P' },
  SAVE: { key: 's', ctrl: true, label: 'Ctrl+S' },
  COMMAND_PALETTE: { key: 'k', ctrl: true, label: 'Ctrl+K' },
  FOCUS_TITLE: { key: 't', ctrl: true, label: 'Ctrl+T' },
  DELETE: { key: 'Delete', label: 'Delete' },
  ESCAPE: { key: 'Escape', label: 'Esc' },
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
};

export const highlightCode = (code: string, language: string): string => {
  // Simple escape for now; in production, use highlight.js
  return code
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
};

export const truncate = (str: string, length: number): string => {
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
};

export const debounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};
