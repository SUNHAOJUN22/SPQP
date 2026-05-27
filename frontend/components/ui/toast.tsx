"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
  XCircle,
} from "lucide-react";
import type { Toast } from "@/lib/store";

const icons = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const iconColors = {
  success: "text-studio-green",
  error: "text-studio-red",
  warning: "text-studio-orange",
  info: "text-studio-blue",
};

export function ToastContainer({
  toasts,
  onDismiss,
}: {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}) {
  return (
    <div className="fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 flex-col gap-2" role="status" aria-live="polite" aria-label="通知消息">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon = icons[toast.type];
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 24, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 24, scale: 0.95 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex min-w-[320px] max-w-[440px] items-center gap-3 rounded-lg bg-studio-text px-5 py-3 shadow-elevation-2"
            >
              <Icon className={`h-5 w-5 shrink-0 ${iconColors[toast.type]}`} />
              <span className="flex-1 text-sm font-medium text-studio-ink">
                {toast.message}
              </span>
              <button
                onClick={() => onDismiss(toast.id)}
                className="shrink-0 rounded-full p-1 text-studio-ink opacity-60 transition duration-150 hover:opacity-100"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
