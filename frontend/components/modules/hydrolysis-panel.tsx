"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { chartColors } from "@/components/shared/tone-helpers";
import { hydrolysisTemplates } from "@/lib/studio-data";

const postReactionData = [
  { step: "硅烷前体", DCS: 0, MCSOMe: 0, DMOS: 0 },
  { step: "水解", DCS: -9, MCSOMe: -6, DMOS: -4 },
  { step: "硅醇", DCS: -14, MCSOMe: -12, DMOS: -10 },
  { step: "Si–O–Si", DCS: -24, MCSOMe: -22, DMOS: -20 },
];

export function HydrolysisPanel() {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>水解缩合后反应能量图</CardTitle>
              <CardDescription>R–SiCl / R–SiOMe → R–SiOH → R–Si–O–Si–R，单位 kcal/mol。</CardDescription>
            </div>
            <StatusBadge tone="gray">示例路径</StatusBadge>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <AreaChart data={postReactionData}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} />
                <XAxis dataKey="step" tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit=" kcal/mol" axisLine={false} tickLine={false} />
                <ChartTooltip />
                <Area dataKey="DCS" stroke={chartColors[0]} fill={chartColors[0]} fillOpacity={0.16} />
                <Area dataKey="MCSOMe" stroke={chartColors[1]} fill={chartColors[1]} fillOpacity={0.16} />
                <Area dataKey="DMOS" stroke={chartColors[2]} fill={chartColors[2]} fillOpacity={0.16} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>内置反应模板</CardTitle>
              <CardDescription>模板只用于 Gaussian 输入构建和报告结构化，不代表已完成真实计算。</CardDescription>
            </div>
          </CardHeader>
          <div className="space-y-3">
            {hydrolysisTemplates.map((item) => (
              <div key={item} className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4 font-mono text-sm text-studio-text">{item}</div>
            ))}
            <div className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4 font-mono text-sm text-studio-text">
              R–SiOH + HO–SiR′ → R–Si–O–Si–R′ + H₂O
            </div>
          </div>
        </Card>
      </div>
      <MechanismConclusion
        title="后反应评价原则"
        text="聚合阶段关注 C=C 插入，后处理阶段关注 Si–Cl / Si–OMe 水解和 Si–O–Si 缩合，两者必须分开评价。不能用后反应潜力高直接推断聚合插入活性高。"
      />
    </div>
  );
}
