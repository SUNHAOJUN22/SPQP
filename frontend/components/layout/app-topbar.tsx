"use client";

import { Moon, Search, Settings, ShieldCheck, Sun } from "lucide-react";
import type React from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import type { ModuleId } from "@/types/studio";

export function AppTopbar({
  title,
  subtitle,
  breadcrumb,
  backendStatus,
  theme,
  onToggleTheme,
  onOpenSearch,
  selectedMoleculeKey,
  onSelectMolecule,
  moleculeKeys,
}: {
  title: string;
  subtitle: string;
  breadcrumb: string;
  backendStatus: "connected" | "disconnected" | "checking";
  theme: "dark" | "light";
  onToggleTheme: () => void;
  onOpenSearch: () => void;
  selectedMoleculeKey: string;
  onSelectMolecule: (key: string) => void;
  moleculeKeys: string[];
}) {
  const statusLabel = backendStatus === "connected" ? "数据源在线" : backendStatus === "checking" ? "正在检查" : "后端离线";
  return (
    <header className="sticky top-0 z-20 border-b border-studio-line/60 bg-studio-ink px-4">
      <div className="flex items-center gap-4 h-14">
        <div className="min-w-0 shrink-0">
          <div className="flex items-center gap-1 text-xs text-studio-muted">
            <span>{breadcrumb}</span>
            <span>/</span>
            <span className="truncate">{subtitle}</span>
          </div>
          <h2 className="truncate text-base font-medium">{title}</h2>
        </div>
        <div
          className="focus-ring flex flex-1 max-w-[720px] mx-auto h-10 items-center gap-3 rounded-full border border-studio-line/60 bg-studio-panel px-4 text-left text-sm text-studio-muted transition hover:border-studio-cyan/55 hover:bg-studio-panel2 cursor-pointer"
          onClick={onOpenSearch}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") onOpenSearch();
          }}
          aria-label="全局搜索"
        >
          <Search className="h-4 w-4 shrink-0" />
          <input
            readOnly
            onFocus={onOpenSearch}
            placeholder="搜索分子、任务、报告、证据…"
            className="min-w-0 flex-1 cursor-pointer bg-transparent outline-none placeholder:text-studio-muted"
          />
          <kbd className="ml-auto hidden rounded-lg border border-studio-line px-2 py-0.5 text-[10px] sm:inline">Ctrl K</kbd>
        </div>
        <div className="flex min-w-0 items-center justify-end gap-2 shrink-0">
          <StatusBadge tone={backendStatus === "connected" ? "green" : backendStatus === "checking" ? "yellow" : "red"} className="hidden md:inline-flex">
            <ShieldCheck className="mr-1 h-3.5 w-3.5" />
            {statusLabel}
          </StatusBadge>
          <Select value={selectedMoleculeKey} onChange={(event) => onSelectMolecule(event.target.value)} className="hidden w-32 md:block">
            {moleculeKeys.map((key) => <option key={key} value={key}>{key}</option>)}
          </Select>
          <Button variant="secondary" size="icon" aria-label="系统设置" icon={<Settings className="h-4 w-4" />} />
          <Button
            variant="secondary"
            size="icon"
            aria-label="切换主题"
            icon={theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            onClick={onToggleTheme}
          />
        </div>
      </div>
    </header>
  );
}

export function MobileModuleRail({ activeModule, items, onSwitch }: { activeModule: ModuleId; items: { id: ModuleId; label: string; icon: React.ElementType }[]; onSwitch: (id: ModuleId) => void }) {
  return (
    <div className="no-scrollbar mb-4 flex snap-x gap-2 overflow-x-auto lg:hidden">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <button
            key={item.id}
            onClick={() => onSwitch(item.id)}
            className={`focus-ring inline-flex shrink-0 snap-start items-center gap-2 rounded-pill px-4 py-2 text-sm font-medium ${activeModule === item.id ? "bg-gm-primary-container text-studio-cyan" : "bg-studio-panel text-studio-muted"}`}
            aria-current={activeModule === item.id ? "page" : undefined}
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </button>
        );
      })}
    </div>
  );
}
