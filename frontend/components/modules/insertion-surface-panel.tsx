"use client";

import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { MiniMetric } from "@/components/shared/mini-metric";
import { chartColors, rateText, toneSurface } from "@/components/shared/tone-helpers";
import { energyRows, pathwayData, sequenceHeatmap } from "@/lib/studio-data";
import { cn } from "@/lib/utils";

export function InsertionSurfacePanel() {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>反应自由能剖面图</CardTitle>
              <CardDescription>free active site + monomer → π-complex → TS → product，单位 kcal/mol。</CardDescription>
            </div>
            <StatusBadge tone="gray">350 K</StatusBadge>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <LineChart data={pathwayData}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} />
                <XAxis dataKey="coordinate" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit=" kcal/mol" axisLine={false} tickLine={false} />
                <ChartTooltip />
                <Legend />
                <Line type="monotone" dataKey="DCS" stroke={chartColors[0]} strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="MCSOMe" stroke={chartColors[1]} strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="DMOS" stroke={chartColors[2]} strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>krel 相对速率</CardTitle>
              <CardDescription>krel = exp[-ΔΔG‡ / RT]，默认 T = 350 K。</CardDescription>
            </div>
          </CardHeader>
          {energyRows.map((row) => (
            <div key={row.molecule} className="mb-4">
              <div className="mb-2 flex justify-between text-sm text-studio-muted">
                <span>{row.molecule}</span>
                <b>{rateText(row.krel)}</b>
              </div>
              <Progress value={row.krel === null ? 0 : Math.min(100, Math.max(2, row.krel * 100))} />
            </div>
          ))}
        </Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <MiniMetric title="ΔG‡complex" value="+23.9" unit="kcal/mol" tone="yellow" />
        <MiniMetric title="ΔGproduct" value="-16.8" unit="kcal/mol" tone="green" />
        <MiniMetric title="TS 验证" value="待上传" unit="虚频 / IRC" tone="yellow" />
      </div>
      <SequenceHeatmap />
      <MechanismConclusion
        title="插入反应中文解释"
        text="若 ΔG‡ 比 DCS 高 3–5 kcal/mol，则在 350 K 下相对插入速率会显著降低。若 π-complex 稳定但 TS 势垒高，说明单体可以配位但插入困难；若 π-complex 不稳定，说明单体难以有效靠近活性中心。"
      />
    </div>
  );
}

function SequenceHeatmap() {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>1-己烯后续插入序列效应热图</CardTitle>
          <CardDescription>sequence effect heatmap</CardDescription>
        </div>
      </CardHeader>
      <div className="grid gap-2 md:grid-cols-3">
        {sequenceHeatmap.map((cell) => (
          <div key={`${cell.first}-${cell.second}`} className={cn("rounded-xl border p-4", cell.value > 70 ? toneSurface("green") : cell.value > 40 ? toneSurface("yellow") : toneSurface("red"))}>
            <p className="text-sm font-medium">{cell.first} → {cell.second}</p>
            <p className="mt-2 text-2xl font-medium">{cell.value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
