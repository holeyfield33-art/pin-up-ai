import React, { useEffect } from 'react';
import { X, Keyboard } from 'lucide-react';

interface ShortcutHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

const SHORTCUTS = [
  { keys: ['⌘', 'K'], description: 'Focus search bar' },
  { keys: ['⌘', 'N'], description: 'New snippet' },
  { keys: ['⌘', 'S'], description: 'Save snippet' },
  { keys: ['⌘', ','], description: 'Open settings' },
  { keys: ['⌘', 'E'], description: 'Export' },
  { keys: ['⌘', '?'], description: 'Show this help' },
  { keys: ['Esc'], description: 'Cancel / close modal' },
];

export const ShortcutHelp: React.FC<ShortcutHelpProps> = ({ isOpen, onClose }) => {
  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3">
          <div className="flex items-center gap-2">
            <Keyboard className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Keyboard Shortcuts
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Shortcut list */}
        <div className="px-6 pb-6">
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {SHORTCUTS.map(({ keys, description }) => (
              <div
                key={description}
                className="flex items-center justify-between py-2.5"
              >
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {description}
                </span>
                <div className="flex items-center gap-1">
                  {keys.map((key) => (
                    <kbd
                      key={key}
                      className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md shadow-sm"
                    >
                      {key}
                    </kbd>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <p className="mt-4 text-xs text-gray-400 dark:text-gray-500 text-center">
            On Windows/Linux, use Ctrl instead of ⌘
          </p>
        </div>
      </div>
    </div>
  );
};
