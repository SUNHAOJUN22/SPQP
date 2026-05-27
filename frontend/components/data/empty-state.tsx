import type React from "react";

export function EmptyState({ icon, title, description, action }: { icon?: React.ReactNode; title: string; description: string; action?: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-studio-line bg-studio-panel/55 p-8 text-center">
      {icon ? <div className="mx-auto mb-3 grid h-11 w-11 place-items-center rounded-xl bg-studio-panel2 text-studio-muted">{icon}</div> : null}
      <p className="text-sm font-medium text-studio-text">{title}</p>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-studio-muted">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
