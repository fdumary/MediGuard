// Lightweight toast notification system (context + viewport). Used to
// surface live WebSocket events (sepsis alerts, drug interaction results)
// no matter which page the user is currently on.

import { AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import { createContext, useCallback, useContext, useState } from "react";
import { cn } from "../../lib/utils";

const ToastContext = createContext(null);

const ICONS = { danger: AlertTriangle, success: CheckCircle2, info: Info };
const TONES = {
  danger: "border-red-500/40 bg-red-950/60",
  success: "border-emerald-500/40 bg-emerald-950/60",
  info: "border-accent-500/40 bg-base-900/80",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const pushToast = useCallback((toast) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, tone: "info", duration: 6000, ...toast }]);
    if (toast.duration !== 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, toast.duration ?? 6000);
    }
  }, []);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ pushToast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2">
        {toasts.map((toast) => {
          const Icon = ICONS[toast.tone] ?? Info;
          return (
            <div
              key={toast.id}
              className={cn(
                "pointer-events-auto animate-slide-in rounded-xl border p-3.5 shadow-card backdrop-blur-md",
                TONES[toast.tone] ?? TONES.info
              )}
            >
              <div className="flex items-start gap-2.5">
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-base-100" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-base-50">{toast.title}</p>
                  {toast.description && (
                    <p className="mt-0.5 text-xs leading-relaxed text-base-300">{toast.description}</p>
                  )}
                </div>
                <button
                  onClick={() => dismiss(toast.id)}
                  className="shrink-0 text-base-500 hover:text-base-200"
                  aria-label="Dismiss"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
