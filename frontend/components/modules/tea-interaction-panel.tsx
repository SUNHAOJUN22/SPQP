"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageIntro } from "@/components/shared/page-intro";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { energyRows } from "@/lib/studio-data";
import type { StatusTone } from "@/types/studio";

export function TEAInteractionPanel() {
  const data = energyRows.map((row) => ({
    molecule: row.molecule,
    "ΔGbind": row.deltaGBind,
    "n(O)→Al": row.molecule === "DCS" ? 0 : row.molecule === "MCSOMe" ? 14.2 : 27.4,
  }));

  return (
    <div className="space-y-4">
      <PageIntro
        title="TEA 助催化剂作用"
        subtitle="Al···Cl / Al←O / Al···C=C"
        note="比较三乙基铝助剂与氯、甲氧基氧、烯烃双键的络合通道，并用 ΔGbind、Al–O / Al–Cl 距离和 NBO E(2) 判断预组织或过度捕获。"
      />
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <PathwayCards />
        <Card>
          <CardHeader>
            <div>
              <CardTitle>ΔGbind 与 NBO 捕获强度</CardTitle>
              <CardDescription>TEA 捕获风险需要同时看结合自由能、后续 Ti π-络合物稳定性和 NBO 给体-受体强度。</CardDescription>
            </div>
          </CardHeader>
          <div className="h-96">
            <ResponsiveContainer>
              <BarChart data={data}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} />
                <XAxis dataKey="molecule" tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} />
                <ChartTooltip />
                <Legend />
                <Bar dataKey="ΔGbind" fill="hsl(var(--studio-cyan))" radius={[8, 8, 0, 0]} />
                <Bar dataKey="n(O)→Al" fill="hsl(var(--studio-orange))" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
      <MechanismConclusion
        title="TEA 助催化剂中文判据"
        text="若 ΔGbind 适中为负且后续 Ti π-络合物仍稳定，可判定为有效预组织；若 ΔGbind 过强为负但 π-络合物不稳定或插入势垒升高，则 TEA 捕获可能与插入活性脱耦，属于过度捕获风险。"
      />
    </div>
  );
}

function PathwayCards() {
  const modes: Array<[string, string, StatusTone, string]> = [
    ["Al···Cl", "弱导向", "yellow", "氯硅烷可能通过 Al···Cl 接触帮助单体靠近活性中心。"],
    ["Al←O", "甲氧基主导捕获", "violet", "OMe 氧孤对电子可与 Al 形成较强 Lewis 酸碱相互作用。"],
    ["Al···C=C", "有效预组织", "green", "如果不破坏 C=C π-络合，Al···C=C 可作为插入前预组织通道。"],
  ];

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>三路径络合模式</CardTitle>
          <CardDescription>Al···Cl / Al←O / Al···C=C</CardDescription>
        </div>
      </CardHeader>
      <div className="space-y-3">
        {modes.map(([mode, label, tone, detail]) => (
          <div key={mode} className="rounded-xl border border-studio-line bg-studio-panel/70 p-4">
            <div className="flex items-center justify-between gap-3">
              <span className="font-medium text-studio-text">{mode}</span>
              <StatusBadge tone={tone}>{label}</StatusBadge>
            </div>
            <p className="mt-3 text-sm leading-6 text-studio-muted">{detail}</p>
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <span className="rounded-xl bg-studio-panel2 p-3">r(Al–O)<br /><span className="font-medium text-studio-text">2.02 Å</span></span>
              <span className="rounded-xl bg-studio-panel2 p-3">r(Al–Cl)<br /><span className="font-medium text-studio-text">2.31 Å</span></span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
