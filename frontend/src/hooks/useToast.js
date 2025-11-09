import { useState, useCallback, useRef } from 'react';

let toastId = 0;

export function useToast() {
  const [toasts, setToasts] = useState([]);
  const removeToastRef = useRef(null);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  // removeToast'u ref'e kaydet
  removeToastRef.current = removeToast;

  const showToast = useCallback((type, message, title = null, duration = 5000) => {
    const id = ++toastId;
    const toast = { id, type, message, title };
    
    setToasts(prev => [...prev, toast]);
    
    if (duration > 0) {
      setTimeout(() => {
        if (removeToastRef.current) {
          removeToastRef.current(id);
        }
      }, duration);
    }
    
    return id;
  }, []);

  const success = useCallback((message, title = null, duration = 5000) => {
    return showToast('success', message, title, duration);
  }, [showToast]);

  const error = useCallback((message, title = null, duration = 5000) => {
    return showToast('error', message, title, duration);
  }, [showToast]);

  const warning = useCallback((message, title = null, duration = 5000) => {
    return showToast('warning', message, title, duration);
  }, [showToast]);

  const info = useCallback((message, title = null, duration = 5000) => {
    return showToast('info', message, title, duration);
  }, [showToast]);

  return {
    toasts,
    success,
    error,
    warning,
    info,
    removeToast,
  };
}

