"use client";

import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
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
import { StatusBadge } from "@/components/ui/status-badge";
import { CubeUploadNotice } from "@/components/modules/cube-upload-notice";
import { OrbitalCanvas } from "@/components/modules/electron-density-panel";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { orbitalLevels } from "@/lib/studio-data";
import { cn } from "@/lib/utils";

export function FrontierOrbitalsPanel() {
  return (
    <div className="space-y-4">
      <CubeUploadNotice />
      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <OrbitalEnergyChart />
        <Card>
          <CardHeader>
            <div>
              <CardTitle>HOMO / LUMO 三维等值面</CardTitle>
              <CardDescription>
                轨道正负相位使用不同颜色显示；未上传 cube 时仅显示示意图。
              </CardDescription>
            </div>
            <StatusBadge tone="gray">未上传 HOMO/LUMO cube</StatusBadge>
          </CardHeader>
          <div className="grid gap-4 md:grid-cols-2">
            <OrbitalMini mode="homo" label="HOMO" />
            <OrbitalMini mode="lumo" label="LUMO" />
          </div>
        </Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <OrbitalCanvas mode="homo" title="HOMO 电子云相位示意" />
        <Card>
          <CardHeader>
            <div>
              <CardTitle>自动解释</CardTitle>
              <CardDescription>Frontier orbital interpretation</CardDescription>
            </div>
          </CardHeader>
          <p className="text-sm leading-7 text-studio-muted">
            若 HOMO 主要分布在 OMe 氧原子附近，说明 O 孤对电子是主要给体轨道；
            若 HOMO 主要分布在 C=C 双键附近，则生产性烯烃配位更可能。
          </p>
          <p className="mt-4 text-sm leading-7 text-studio-muted">
            TEA 络合后 HOMO-LUMO gap 降低通常意味着单体-助剂电子耦合增强。
            若 O→Ti 构型中 n(O)→Ti 相互作用增强，则提示 Ti 毒化风险升高。
          </p>
        </Card>
      </div>
    </div>
  );
}

function OrbitalEnergyChart() {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>HOMO / LUMO 能级图</CardTitle>
          <CardDescription>前线轨道 Frontier Orbitals</CardDescription>
        </div>
        <StatusBadge tone="blue">gap = 4.1 eV</StatusBadge>
      </CardHeader>
      <div className="h-80">
        <ResponsiveContainer>
          <BarChart data={orbitalLevels}>
            <CartesianGrid
              stroke="hsl(var(--studio-line))"
              strokeOpacity={0.32}
              vertical={false}
            />
            <XAxis
              dataKey="orbital"
              tick={{ fill: "hsl(var(--studio-muted))" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "hsl(var(--studio-muted))" }}
              unit=" eV"
              axisLine={false}
              tickLine={false}
            />
            <ChartTooltip />
            <Bar
              dataKey="energy"
              radius={[8, 8, 0, 0]}
              fill="hsl(var(--studio-violet))"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function OrbitalMini({ mode, label }: { mode: "homo" | "lumo"; label: string }) {
  return (
    <div className="relative h-56 overflow-hidden rounded-xl border border-studio-line bg-studio-ink">
      <motion.div
        className={cn(
          "absolute left-8 top-12 h-28 w-36 rounded-full opacity-50 blur-xl",
          mode === "homo" ? "bg-studio-violet" : "bg-studio-blue",
        )}
        animate={{ scale: [1, 1.15, 1] }}
        transition={{ duration: 3.6, repeat: Infinity }}
      />
      <motion.div
        className={cn(
          "absolute right-8 top-16 h-24 w-32 rounded-full opacity-50 blur-xl",
          mode === "homo" ? "bg-studio-green" : "bg-studio-orange",
        )}
        animate={{ scale: [1.12, 0.96, 1.12] }}
        transition={{ duration: 3.8, repeat: Infinity }}
      />
      <div className="absolute bottom-4 left-4 text-lg font-medium text-studio-text">
        {label}
      </div>
    </div>
  );
}
