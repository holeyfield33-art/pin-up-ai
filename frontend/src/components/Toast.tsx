import React from 'react';
import { AlertCircle, CheckCircle, InfoIcon, AlertTriangle } from 'lucide-react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
    info: <InfoIcon className="w-5 h-5" />,
  };

  const colors = {
    success: 'bg-green-50 border-green-200 text-green-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900',
  };

  return (
    <div
      className={`flex items-center gap-3 p-4 rounded-lg border ${colors[type]} shadow-md`}
      role="alert"
    >
      {icons[type]}
      <span className="flex-1">{message}</span>
      <button
        onClick={onClose}
        className="text-xl font-bold opacity-50 hover:opacity-75"
        aria-label="Close toast"
      >
        ×
      </button>
    </div>
  );
};
