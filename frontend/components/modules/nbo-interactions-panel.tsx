"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageIntro } from "@/components/shared/page-intro";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { InteractionLine } from "@/components/shared/mini-metric";
import { nboData } from "@/lib/studio-data";

export function NBOInteractionsPanel() {
  return (
    <div className="space-y-4">
      <PageIntro
        title="NBO donor-acceptor 网络与给体-受体相互作用"
        subtitle="NBO 相互作用 / Donor-Acceptor E(2)"
        note="节点表示 O、Cl、C=C、Al、Ti、Si 等关键片段；边宽表示二阶微扰能 E(2) 大小。真实 NBO 结论必须来自 Gaussian/NBO 输出。"
      />
      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <NboNetwork />
        <NboBars />
      </div>
      <Card>
        <CardHeader>
          <div>
            <CardTitle>轨道相互作用表</CardTitle>
            <CardDescription>NBO donor-acceptor second-order perturbation E(2)</CardDescription>
          </div>
        </CardHeader>
        <div className="grid gap-3 md:grid-cols-5">
          {nboData.map((item) => (
            <div key={item.channel} className="rounded-xl border border-studio-line bg-studio-panel/70 p-4 transition hover:bg-studio-cyan/5">
              <p className="font-medium">{item.channel}</p>
              <p className="mt-2 text-sm text-studio-muted">{item.donor} → {item.acceptor}</p>
              <p className="mt-4 text-2xl font-medium">{item.value}</p>
              <p className="text-xs text-studio-muted">kcal/mol</p>
            </div>
          ))}
        </div>
      </Card>
      <MechanismConclusion
        title="NBO 自动解释"
        text="若 n(O)→Ti E(2) 大于 π(C=C)→Ti E(2)，说明 OMe 毒化配位可能竞争甚至压倒生产性 C=C 配位。若 n(O)→Al 强而 n(O)→Ti 弱，说明 TEA 可能屏蔽 OMe 毒化并起导向作用。"
      />
    </div>
  );
}

function NboNetwork() {
  const nodes: Array<[string, number, number, string]> = [
    ["O", 125, 95, "hsl(var(--studio-red))"],
    ["Cl", 120, 260, "hsl(var(--studio-green))"],
    ["C=C", 295, 300, "hsl(var(--studio-blue))"],
    ["Al", 480, 110, "hsl(var(--studio-cyan))"],
    ["Ti", 485, 265, "hsl(var(--studio-orange))"],
    ["Si", 300, 165, "hsl(var(--studio-violet))"],
  ];

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>donor-acceptor 网络图</CardTitle>
          <CardDescription>边宽表示 E(2) 大小；颜色表示相互作用类型。</CardDescription>
        </div>
      </CardHeader>
      <div className="relative h-96 overflow-hidden rounded-xl border border-studio-line bg-studio-panel molecule-grid">
        <svg viewBox="0 0 620 360" className="h-full w-full">
          {nodes.map(([label, x, y, color]) => (
            <g key={label}>
              <circle cx={x} cy={y} r="30" fill={color} opacity="0.9" />
              <text x={x} y={y + 6} textAnchor="middle" fill="white" fontWeight="700">{label}</text>
            </g>
          ))}
          <InteractionLine x1={155} y1={95} x2={450} y2={110} color="hsl(var(--studio-cyan))" width={8} label="O→Al" />
          <InteractionLine x1={155} y1={105} x2={455} y2={250} color="hsl(var(--studio-red))" width={5} label="O→Ti" />
          <InteractionLine x1={325} y1={292} x2={455} y2={270} color="hsl(var(--studio-green))" width={9} label="C=C→Ti" />
          <InteractionLine x1={150} y1={250} x2={455} y2={125} color="hsl(var(--studio-blue))" width={5} label="Cl→Al" />
        </svg>
      </div>
    </Card>
  );
}

function NboBars() {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>NBO E(2) 相互作用强度</CardTitle>
          <CardDescription>单位：kcal/mol</CardDescription>
        </div>
      </CardHeader>
      <div className="h-96">
        <ResponsiveContainer>
          <BarChart data={nboData}>
            <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} />
            <XAxis dataKey="channel" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} />
            <ChartTooltip />
            <Bar dataKey="value" radius={[8, 8, 0, 0]}>
              {nboData.map((item) => (
                <Cell key={item.channel} fill={item.channel.includes("O→Ti") ? "hsl(var(--studio-red))" : item.channel.includes("C=C") ? "hsl(var(--studio-green))" : "hsl(var(--studio-cyan))"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
