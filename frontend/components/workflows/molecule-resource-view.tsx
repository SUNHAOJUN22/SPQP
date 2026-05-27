import type React from "react";

export function MoleculeResourceView({ list, viewer, details }: { list: React.ReactNode; viewer: React.ReactNode; details: React.ReactNode }) {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.2fr)_340px]">
      <section className="min-w-0 rounded-xl border border-studio-line bg-studio-panel/82 p-4">{list}</section>
      <section className="min-w-0 rounded-xl border border-studio-line bg-studio-panel/82 p-4">{viewer}</section>
      <aside className="rounded-xl border border-studio-line bg-studio-panel/82 p-4">{details}</aside>
    </div>
  );
}
