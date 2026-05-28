"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { MiniMetric } from "@/components/shared/mini-metric";
import { poisonLabel, poisonTone } from "@/components/shared/tone-helpers";
import { energyRows } from "@/lib/studio-data";
import { formatEnergy } from "@/lib/utils";

export function TiPoisoningPanel() {
  const data = energyRows.map((row) => ({
    molecule: row.molecule,
    "ΔGpoison": row.deltaGPoison,
    label: poisonLabel(row.deltaGPoison),
  }));

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>C=C π-络合物 vs O→Ti 毒化络合物</CardTitle>
              <CardDescription>ΔGpoison = G(O→Ti complex) − G(C=C π-complex)，单位 kcal/mol。</CardDescription>
            </div>
            <StatusBadge tone="gray">示例数据</StatusBadge>
          </CardHeader>
          <div className="h-96">
            <ResponsiveContainer>
              <BarChart data={data}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} />
                <XAxis dataKey="molecule" tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit=" kcal/mol" axisLine={false} tickLine={false} />
                <ChartTooltip />
                <Bar dataKey="ΔGpoison" radius={[10, 10, 0, 0]}>
                  {data.map((entry) => <Cell key={entry.molecule} fill={`hsl(var(--studio-${poisonTone(entry["ΔGpoison"])}))`} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>毒化风险仪表盘</CardTitle>
              <CardDescription>红黄绿标签只表示示例判据，真实结论需要上传 π-complex 与 O→Ti complex 自由能。</CardDescription>
            </div>
          </CardHeader>
          <div className="space-y-4">
            {energyRows.map((row) => (
              <div key={row.molecule} className="rounded-xl border border-studio-line bg-studio-panel/70 p-4">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <span className="font-medium text-studio-text">{row.molecule}</span>
                  <StatusBadge tone={poisonTone(row.deltaGPoison)}>{formatEnergy(row.deltaGPoison)} kcal/mol</StatusBadge>
                </div>
                <Progress value={row.deltaGPoison === null ? 0 : Math.max(0, Math.min(100, 50 + row.deltaGPoison * 6))} />
                <p className="mt-3 text-xs leading-5 text-studio-muted">{poisonLabel(row.deltaGPoison)}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <MiniMetric title="O→Ti NBO" value="16.1" unit="kcal/mol" tone="red" />
        <MiniMetric title="C=C→Ti NBO" value="18.5" unit="kcal/mol" tone="green" />
        <MiniMetric title="Ti–O / Ti–C 距离" value="2.18 / 2.34" unit="Å" tone="yellow" />
      </div>
      <MechanismConclusion
        title="Ti 毒化判据自动解释"
        text="若 ΔGpoison < 0，说明 O→Ti 非生产性配位比 C=C productive π 配位更稳定，甲氧基可能毒化 Ti 活性中心；0 到 +5 kcal/mol 区间应判定为配位竞争，需结合 NBO 与结构距离共同判断。"
      />
    </div>
  );
}
