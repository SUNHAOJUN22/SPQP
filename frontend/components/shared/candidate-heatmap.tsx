"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { toneSurface } from "@/components/shared/tone-helpers";
import { heatmapCells } from "@/lib/studio-data";
import { cn } from "@/lib/utils";
import type { StatusTone } from "@/types/studio";

export function CandidateHeatmap() {
  const metrics = Array.from(new Set(heatmapCells.map((c) => c.metric)));
  const molecules = Array.from(new Set(heatmapCells.map((c) => c.molecule)));
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>三单体候选矩阵热图</CardTitle>
          <CardDescription>DCS / MCSOMe / DMOS mechanism score heatmap</CardDescription>
        </div>
        <Button variant="secondary" size="sm" icon={<Download className="h-4 w-4" />}>下载图表</Button>
      </CardHeader>
      <div className="overflow-x-auto">
        <div className="min-w-[720px]">
          <div className="grid grid-cols-[120px_repeat(6,1fr)] gap-2 text-xs font-medium text-studio-muted">
            <div />
            {metrics.map((m) => (<div key={m} className="text-center">{m}</div>))}
          </div>
          {molecules.map((mol) => (
            <div key={mol} className="mt-2 grid grid-cols-[120px_repeat(6,1fr)] gap-2">
              <div className="flex items-center rounded-xl bg-studio-panel2 px-4 text-sm font-medium">{mol}</div>
              {metrics.map((metric) => {
                const cell = heatmapCells.find((i) => i.molecule === mol && i.metric === metric);
                return (
                  <div key={`${mol}-${metric}`} className={cn("rounded-xl border p-3 text-center transition-all hover:scale-[1.03]", toneSurface(cell?.tone ?? "gray"))}>
                    <div className="text-xl font-medium">{cell?.value}</div>
                    <div className="mt-1 text-[11px] opacity-80">评分</div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
