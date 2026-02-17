import { useState, useCallback, useRef } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastData {
  message: string;
  type: ToastType;
}

export function useToast(defaultDuration = 3000) {
  const [toast, setToast] = useState<ToastData | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const hideToast = useCallback(() => {
    setToast(null);
    if (timerRef.current) clearTimeout(timerRef.current);
  }, []);

  const showToast = useCallback(
    (message: string, type: ToastType = 'info', duration?: number) => {
      if (timerRef.current) clearTimeout(timerRef.current);
      setToast({ message, type });
      const ms = duration ?? defaultDuration;
      if (ms > 0) {
        timerRef.current = setTimeout(() => setToast(null), ms);
      }
    },
    [defaultDuration],
  );

  return { toast, showToast, hideToast };
}
