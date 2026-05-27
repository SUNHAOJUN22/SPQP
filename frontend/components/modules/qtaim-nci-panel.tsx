"use client";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { qtaimData } from "@/lib/studio-data";
import { toneSurface } from "@/components/shared/tone-helpers";
import type { StatusTone } from "@/types/studio";

export function QTAIMNCIPanel() {
  return (<div className="space-y-4"><div className="grid gap-4 xl:grid-cols-[1fr_420px]"><Card><CardHeader><div><CardTitle>QTAIM BCP</CardTitle><CardDescription>Bond critical point topology</CardDescription></div></CardHeader><div className="relative h-96 overflow-hidden rounded-xl border border-studio-line bg-studio-ink gm-chart-container"><svg viewBox="0 0 620 360" className="h-full w-full"><path d="M130 180 C220 70, 390 70, 500 180" stroke="hsl(var(--studio-cyan))" strokeWidth="4" fill="none" /><path d="M130 180 C250 285, 380 285, 500 180" stroke="hsl(var(--studio-violet))" strokeWidth="4" fill="none" />{[130,300,500].map((x,i)=><circle key={x} cx={x} cy={180} r={i===1?8:28} fill={i===1?"hsl(var(--studio-orange))":"hsl(var(--studio-panel-2))"} />)}<text x="130" y="186" textAnchor="middle" fill="white">O</text><text x="300" y="164" textAnchor="middle" fill="hsl(var(--studio-orange))" fontWeight="700">BCP</text><text x="500" y="186" textAnchor="middle" fill="white">Ti</text></svg></div></Card><Card><CardHeader><div><CardTitle>NCI/RDG</CardTitle><CardDescription>color scale</CardDescription></div></CardHeader><div className="space-y-3">{[["Blue","Strong","green"],["Green","vdW","blue"],["Red","Steric","red"]].map(([color,meaning,tone])=><StatusBadge key={String(color)} tone={tone as StatusTone}>{color}:{meaning}</StatusBadge>)}</div><div className="mt-6 h-48 rounded-xl bg-studio-panel-strong" /></Card></div><div className="grid gap-4 xl:grid-cols-2"><QtaimBars dataKey="rho" title="Chart" /><QtaimBars dataKey="laplacian" title="Chart 2" /></div><MechanismConclusion title="QTAIM / NCI Auto Explain" text="Explanation" /></div>);
}

function QtaimBars({ dataKey, title }: { dataKey: "rho" | "laplacian"; title: string }) {
  return (<Card><CardHeader><CardTitle>{title}</CardTitle></CardHeader><div className="h-72"><ResponsiveContainer><BarChart data={qtaimData}><CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} /><XAxis dataKey="bond" tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} /><YAxis tick={{ fill: "hsl(var(--studio-muted))" }} axisLine={false} tickLine={false} /><ChartTooltip /><Bar dataKey={dataKey} fill="hsl(var(--studio-cyan))" radius={[8,8,0,0]} /></BarChart></ResponsiveContainer></div></Card>);
}
