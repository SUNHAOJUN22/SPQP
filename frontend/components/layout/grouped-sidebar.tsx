"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import { navItems } from "@/lib/studio-data";
import { navGroups } from "@/lib/store";
import { cn } from "@/lib/utils";
import type { ModuleId } from "@/types/studio";

export function GroupedSidebar({
  activeModule,
  onSwitch,
  collapsedGroups,
  onToggleGroup,
}: {
  activeModule: ModuleId;
  onSwitch: (id: ModuleId) => void;
  collapsedGroups: Set<string>;
  onToggleGroup: (label: string) => void;
}) {
  return (
    <aside className="sticky top-0 hidden h-screen w-[280px] shrink-0 flex-col border-r border-studio-line/60 bg-studio-panel lg:flex">
      <div className="px-4 py-4 border-b border-studio-line/40">
        <h1 className="text-base font-medium text-studio-text">硅氧硅碳机理平台</h1>
        <p className="text-xs text-studio-muted">Catalyst Research Workspace</p>
      </div>
      <nav className="no-scrollbar flex-1 space-y-2 overflow-y-auto px-3 py-2" role="navigation" aria-label="分组导航">
        {navGroups.map((group) => {
          const isCollapsed = collapsedGroups.has(group.label);
          const groupNavItems = navItems.filter((item) => group.ids.includes(item.id));
          return (
            <section key={group.label} aria-label={group.label}>
              <button
                onClick={() => onToggleGroup(group.label)}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-xs font-medium uppercase tracking-[0.08em] text-studio-muted transition hover:bg-studio-panel2 hover:text-studio-text"
              >
                <span>{group.label}</span>
                {isCollapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              </button>
              {!isCollapsed ? (
                <div className="mt-1 space-y-1">
                  {groupNavItems.map((item) => {
                    const Icon = item.icon;
                    const active = activeModule === item.id;
                    return (
                      <button
                        key={item.id}
                        onClick={() => onSwitch(item.id)}
                        className={cn(
                          "focus-ring flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-medium transition",
                          active
                            ? "bg-gm-primary-container text-studio-cyan font-medium"
                            : "text-studio-muted hover:bg-studio-panel2 hover:text-studio-text"
                        )}
                        aria-current={active ? "page" : undefined}
                      >
                        <Icon className="h-5 w-5 shrink-0" />
                        <span className="truncate">{item.label}</span>
                      </button>
                    );
                  })}
                </div>
              ) : null}
            </section>
          );
        })}
      </nav>
      <div className="px-4 py-3 border-t border-studio-line/40 text-xs text-studio-muted">
        当前资源均保留 provenance；示例数据不能写作真实结论。
      </div>
    </aside>
  );
}
