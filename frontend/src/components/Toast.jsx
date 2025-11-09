import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

const toastTypes = {
  success: { icon: CheckCircle, bg: 'bg-green-500', text: 'text-white' },
  error: { icon: XCircle, bg: 'bg-red-500', text: 'text-white' },
  warning: { icon: AlertCircle, bg: 'bg-yellow-500', text: 'text-white' },
  info: { icon: Info, bg: 'bg-blue-500', text: 'text-white' },
};

export default function Toast({ toasts, removeToast }) {
  return (
    <div className="fixed top-20 right-4 z-[9999] space-y-2 max-w-md w-full">
      <AnimatePresence>
        {toasts.map((toast) => {
          const { icon: Icon, bg, text } = toastTypes[toast.type] || toastTypes.info;
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 300, scale: 0.8 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 300, scale: 0.8 }}
              className={`${bg} ${text} rounded-lg shadow-2xl p-4 flex items-start space-x-3 backdrop-blur-sm`}
            >
              <Icon size={20} className="flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                {toast.title && (
                  <p className="font-semibold text-sm mb-1">{toast.title}</p>
                )}
                <p className="text-sm">{toast.message}</p>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="flex-shrink-0 hover:opacity-80 transition-opacity"
              >
                <X size={18} />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

