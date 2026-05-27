import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/types/studio";

export function MetricCard({
  label,
  value,
  unit,
  tone = "blue",
  detail
}: {
  label: string;
  value: string | number;
  unit?: string;
  tone?: StatusTone;
  detail?: string;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-studio-muted">{label}</p>
          <div className="mt-3 flex items-end gap-2">
            <span className="text-2xl font-medium tracking-normal text-studio-text">{value}</span>
            {unit ? <span className="pb-1 text-xs font-medium text-studio-muted">{unit}</span> : null}
          </div>
        </div>
        <StatusBadge tone={tone}>{detail ?? tone}</StatusBadge>
      </div>
    </Card>
  );
}
