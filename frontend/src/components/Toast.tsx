import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  onClose: () => void;
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const styles = {
  success: 'bg-green-50 border-green-300 text-green-900',
  error: 'bg-red-50 border-red-300 text-red-900',
  warning: 'bg-yellow-50 border-yellow-300 text-yellow-900',
  info: 'bg-blue-50 border-blue-300 text-blue-900',
};

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  const Icon = icons[type];
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border shadow-md animate-slide-in ${styles[type]}`}
      role="alert"
    >
      <Icon className="w-4 h-4 shrink-0" />
      <span className="flex-1 text-sm">{message}</span>
      <button
        onClick={onClose}
        className="opacity-50 hover:opacity-100"
        aria-label="Dismiss"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
