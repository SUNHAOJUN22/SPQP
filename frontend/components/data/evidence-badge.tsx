import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/types/studio";

const evidenceTone: Record<string, StatusTone> = {
  A: "green",
  B: "blue",
  C: "yellow",
  D: "gray",
};

export function EvidenceBadge({ level = "C", compact = false }: { level?: string; compact?: boolean }) {
  const normalized = level.trim().toUpperCase().slice(0, 1) || "C";
  return (
    <StatusBadge tone={evidenceTone[normalized] ?? "yellow"} className={compact ? "h-7 px-2" : undefined}>
      {normalized}级证据
    </StatusBadge>
  );
}
