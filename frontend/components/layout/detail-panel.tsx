import type React from "react";

export function DetailPanel({ title = "详情", subtitle, children }: { title?: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <aside className="rounded-xl border border-studio-line/60 bg-studio-panel p-4 lg:sticky lg:top-16">
      <p className="text-sm font-medium text-studio-text">{title}</p>
      {subtitle ? <p className="mt-1 text-xs leading-5 text-studio-muted">{subtitle}</p> : null}
      <div className="mt-4">{children}</div>
    </aside>
  );
}
