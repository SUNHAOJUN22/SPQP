"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { chargeData } from "@/lib/studio-data";
import type { StatusTone } from "@/types/studio";

export function ChargePopulationPanel() {
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_430px]">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>电荷布居对比</CardTitle>
            <CardDescription>
              Mulliken / NPA / RESP / Hirshfeld charge population
            </CardDescription>
          </div>
          <StatusBadge tone="gray">示例数据</StatusBadge>
        </CardHeader>
        <div className="h-96">
          <ResponsiveContainer>
            <BarChart data={chargeData}>
              <CartesianGrid
                stroke="hsl(var(--studio-line))"
                strokeOpacity={0.32}
                vertical={false}
              />
              <XAxis
                dataKey="atom"
                tick={{ fill: "hsl(var(--studio-muted))" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(var(--studio-muted))" }}
                unit=" e"
                axisLine={false}
                tickLine={false}
              />
              <ChartTooltip />
              <Legend />
              <Bar
                dataKey="Mulliken"
                fill="hsl(var(--studio-cyan))"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="NPA"
                fill="hsl(var(--studio-violet))"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="RESP"
                fill="hsl(var(--studio-orange))"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="Hirshfeld"
                fill="hsl(var(--studio-green))"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <Card>
        <CardHeader>
          <div>
            <CardTitle>分子表面电荷映射</CardTitle>
            <CardDescription>Charge mapped surface schematic</CardDescription>
          </div>
        </CardHeader>
        <div className="relative h-56 overflow-hidden rounded-xl border border-studio-line bg-studio-ink">
          <div className="absolute left-8 top-12 h-28 w-36 rounded-full bg-studio-violet opacity-50 blur-xl" />
          <div className="absolute right-8 top-16 h-24 w-32 rounded-full bg-studio-green opacity-50 blur-xl" />
          <div className="absolute bottom-4 left-4 text-lg font-medium text-studio-text">
            OMe 区域负电荷富集
          </div>
        </div>
        <div className="mt-4 space-y-3">
          <p className="text-sm leading-7 text-studio-muted">
            q(O) 越负，O 原子 Lewis 碱性越强，越可能与 Al 或 Ti 配位。
          </p>
          <p className="text-sm leading-7 text-studio-muted">
            TEA 络合后 O 原子负电荷降低，说明 O 向 Al 发生电子给体作用。
          </p>
          <p className="text-sm leading-7 text-studio-muted">
            Cα/Cβ 电荷极化增强可能影响 C=C 插入的区域选择性和过渡态稳定性。
          </p>
        </div>
      </Card>
      <FragmentChargeMap />
    </div>
  );
}

function FragmentChargeMap() {
  const fragments = [
    ["Si 取代基片段", 36, "violet"],
    ["烯烃片段", 28, "blue"],
    ["TEA 片段", 52, "blue"],
    ["Ti 活性中心片段", 64, "orange"],
  ] as const;
  return (
    <Card className="xl:col-span-2">
      <CardHeader>
        <div>
          <CardTitle>片段电荷分解图</CardTitle>
          <CardDescription>Fragment charge decomposition</CardDescription>
        </div>
      </CardHeader>
      <div className="grid gap-3 md:grid-cols-4">
        {fragments.map(([label, value, tone]) => (
          <div
            key={label}
            className="rounded-xl border border-studio-line bg-studio-panel/70 p-4"
          >
            <p className="text-sm font-medium">{label}</p>
            <div className="mt-4">
              <Progress value={value} />
            </div>
            <StatusBadge className="mt-4" tone={tone as StatusTone}>
              电荷转移 {value}%
            </StatusBadge>
          </div>
        ))}
      </div>
    </Card>
  );
}
