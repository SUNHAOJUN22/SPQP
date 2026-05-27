import type React from "react";

export function PageHeader({ title, subtitle, actions, meta }: { title: string; subtitle: string; actions?: React.ReactNode; meta?: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-studio-line/60 bg-studio-panel p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          {meta ? <div className="mb-2 flex flex-wrap gap-2">{meta}</div> : null}
          <h2 className="text-2xl font-medium tracking-normal text-studio-text">{title}</h2>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-studio-muted">{subtitle}</p>
        </div>
        {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
      </div>
    </div>
  );
}
