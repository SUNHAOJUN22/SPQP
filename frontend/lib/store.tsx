"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { checkHealth } from "@/lib/api-client";
import type { ModuleId } from "@/types/studio";

/* ── Toast ── */

export interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
}

/* ── Nav Groups ── */

export interface NavGroup {
  label: string;
  emoji: string;
  ids: ModuleId[];
}

export const navGroups: NavGroup[] = [
  { label: "首页", emoji: "🏠", ids: ["integrated", "dashboard"] },
  {
    label: "知识库",
    emoji: "📚",
    ids: ["literature", "data"],
  },
  {
    label: "分子与结构",
    emoji: "🔬",
    ids: ["library", "bond", "density", "orbitals", "charges", "nbo", "qtaim", "esp", "fukui", "difference"],
  },
  {
    label: "量子计算",
    emoji: "🧪",
    ids: ["scientific", "connectors", "builder", "parser", "merged"],
  },
  {
    label: "机理分析",
    emoji: "⚛️",
    ids: ["tea", "poisoning", "insertion", "hydrolysis", "radical", "peroxide", "sic", "degradation", "kinetics", "residence", "microstructure", "mechanisms", "decision"],
  },
  {
    label: "实验闭环",
    emoji: "📈",
    ids: ["experiments"],
  },
  {
    label: "报告",
    emoji: "📝",
    ids: ["reports"],
  },
  {
    label: "自动化",
    emoji: "⚙️",
    ids: ["mcp", "settings"],
  },
];

/* ── Store ── */

interface StudioStore {
  activeModule: ModuleId;
  switchModule: (id: ModuleId) => void;
  selectedMoleculeKey: string;
  setSelectedMoleculeKey: (key: string) => void;
  theme: "dark" | "light";
  toggleTheme: () => void;
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  dismissToast: (id: string) => void;
  backendStatus: "connected" | "disconnected" | "checking";
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
}

const StudioContext = createContext<StudioStore | null>(null);

let toastCounter = 0;

export function StudioProvider({ children }: { children: ReactNode }) {
  const [activeModule, setActiveModule] = useState<ModuleId>("integrated");
  const [selectedMoleculeKey, setSelectedMoleculeKey] = useState("MCSOMe");
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    if (typeof window === "undefined") return "dark";
    return (localStorage.getItem("studio-theme") as "dark" | "light") ?? "dark";
  });
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [backendStatus, setBackendStatus] = useState<
    "connected" | "disconnected" | "checking"
  >("checking");
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const timers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("studio-theme", theme);
  }, [theme]);

  const toggleTheme = useCallback(
    () => setTheme((t) => (t === "dark" ? "light" : "dark")),
    []
  );

  /* backend health */
  useEffect(() => {
    let mounted = true;
    checkHealth().then((ok) => {
      if (mounted) setBackendStatus(ok ? "connected" : "disconnected");
    });
    return () => {
      mounted = false;
    };
  }, []);

  /* module switch */
  const switchModule = useCallback((id: ModuleId) => {
    setActiveModule(id);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  /* toasts */
  const addToast = useCallback((t: Omit<Toast, "id">) => {
    const id = `toast-${++toastCounter}`;
    const toast: Toast = { ...t, id };
    setToasts((prev) => [...prev.slice(-4), toast]);
    const dur = t.duration ?? 4000;
    const timer = setTimeout(() => {
      setToasts((prev) => prev.filter((x) => x.id !== id));
      timers.current.delete(id);
    }, dur);
    timers.current.set(id, timer);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((x) => x.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  /* keyboard shortcuts */
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((v) => !v);
      }
      if (e.key === "Escape") {
        setCommandPaletteOpen(false);
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  return (
    <StudioContext.Provider
      value={{
        activeModule,
        switchModule,
        selectedMoleculeKey,
        setSelectedMoleculeKey,
        theme,
        toggleTheme,
        toasts,
        addToast,
        dismissToast,
        backendStatus,
        commandPaletteOpen,
        setCommandPaletteOpen,
      }}
    >
      {children}
    </StudioContext.Provider>
  );
}

export function useStudio(): StudioStore {
  const ctx = useContext(StudioContext);
  if (!ctx) throw new Error("useStudio must be used within StudioProvider");
  return ctx;
}
