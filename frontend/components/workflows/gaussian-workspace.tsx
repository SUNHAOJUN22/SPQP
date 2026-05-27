import type React from "react";

export function GaussianWorkspace({ templates, editor, preview, details }: { templates: React.ReactNode; editor: React.ReactNode; preview: React.ReactNode; details?: React.ReactNode }) {
  return (
    <div className="grid gap-4 xl:grid-cols-[260px_minmax(0,1fr)_minmax(320px,0.8fr)]">
      <aside className="rounded-xl border border-studio-line bg-studio-panel/82 p-4">{templates}</aside>
      <section className="min-w-0 rounded-xl border border-studio-line bg-studio-panel/82 p-4">{editor}</section>
      <aside className="min-w-0 rounded-xl border border-studio-line bg-studio-panel/82 p-4">{preview}{details}</aside>
    </div>
  );
}
