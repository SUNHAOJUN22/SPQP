"use client";

import { useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Search } from "lucide-react";
import { navItems } from "@/lib/studio-data";
import { navGroups, useStudio } from "@/lib/store";
import { cn } from "@/lib/utils";
import type { ModuleId } from "@/types/studio";

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen, switchModule } =
    useStudio();
  const [query, setQueryRaw] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const prevOpenRef = useRef(false);

  // Reset on open (no useEffect needed)
  if (commandPaletteOpen && !prevOpenRef.current) {
    if (query !== "") setQueryRaw("");
    if (selectedIndex !== 0) setSelectedIndex(0);
    setTimeout(() => inputRef.current?.focus(), 50);
  }
  prevOpenRef.current = commandPaletteOpen;

  function setQuery(value: string) {
    setQueryRaw(value);
    setSelectedIndex(0);
  }

  const results = navItems.filter((item) => {
    if (!query) return true;
    const q = query.toLowerCase();
    return (
      item.label.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q)
    );
  });

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && results[selectedIndex]) {
      e.preventDefault();
      selectItem(results[selectedIndex].id);
    }
  }

  function selectItem(id: ModuleId) {
    switchModule(id);
    setCommandPaletteOpen(false);
  }

  function getGroupLabel(id: ModuleId): string {
    const group = navGroups.find((g) => g.ids.includes(id));
    return group ? `${group.emoji} ${group.label}` : "";
  }

  return (
    <AnimatePresence>
      {commandPaletteOpen && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/40"
            onClick={() => setCommandPaletteOpen(false)}
          />

          {/* Dialog */}
          <motion.div
            className="relative w-full max-w-[580px] mx-4 rounded-xl bg-studio-panel border border-studio-line/60 shadow-elevation-3 overflow-hidden"
            initial={{ opacity: 0, y: -20, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.96 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            {/* Search input */}
            <div className="flex items-center gap-3 border-b border-studio-line px-5 py-4">
              <Search className="h-5 w-5 text-studio-muted shrink-0" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="搜索分子、任务、报告、证据…"
                className="flex-1 bg-transparent text-base text-studio-text placeholder:text-studio-muted outline-none"
              />
              <kbd className="hidden sm:inline-flex shrink-0 items-center gap-1 rounded-lg border border-studio-line bg-studio-panel2/60 px-2 py-0.5 text-xs text-studio-muted">
                ESC
              </kbd>
            </div>

            {/* Results */}
            <div className="max-h-[400px] overflow-y-auto p-2">
              {results.length === 0 ? (
                <div className="p-8 text-center text-sm text-studio-muted">
                  没有找到匹配的模块
                </div>
              ) : (
                results.map((item, index) => {
                  const Icon = item.icon;
                  const isSelected = index === selectedIndex;
                  return (
                    <button
                      key={item.id}
                      onClick={() => selectItem(item.id)}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-xl px-4 py-2.5 text-left text-sm transition",
                        isSelected
                          ? "bg-gm-primary-container text-studio-cyan"
                          : "text-studio-muted hover:bg-studio-panel2 hover:text-studio-text"
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      <span className="flex-1 font-medium">{item.label}</span>
                      <span className="text-xs opacity-60">
                        {getGroupLabel(item.id)}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            {/* Footer hints */}
            <div className="flex items-center gap-4 border-t border-studio-line px-5 py-2.5 text-xs text-studio-muted">
              <span>
                <kbd className="rounded border border-studio-line px-1.5 py-0.5">↑↓</kbd>{" "}
                导航
              </span>
              <span>
                <kbd className="rounded border border-studio-line px-1.5 py-0.5">↵</kbd>{" "}
                选择
              </span>
              <span>
                <kbd className="rounded border border-studio-line px-1.5 py-0.5">Esc</kbd>{" "}
                关闭
              </span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
