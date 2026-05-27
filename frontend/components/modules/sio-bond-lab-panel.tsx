"use client";
import dynamic from "next/dynamic";
import { Bar, BarChart, CartesianGrid, Legend, PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/field";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { ChartTooltip } from "@/components/shared/chart-tooltip";
import { chartColors } from "@/components/shared/tone-helpers";
import { bondBars, bondRadarData, moleculeLibrary, sioDescriptors } from "@/lib/studio-data";
import type { StudioMolecule } from "@/types/studio";
const MoleculeViewer = dynamic(() => import("@/components/molecule-viewer").then((m) => m.MoleculeViewer), { ssr: false });

export function SiOBondLabPanel({ selected, onSelect }: { selected: StudioMolecule; onSelect: (key: string) => void }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[1fr_430px]">
        <MoleculeViewer molecule={selected} highlight={selected.descriptors.oCount > 0 ? "Si–O 发光高亮" : "Si–Cl 基准"} />
        <RadarPanel title="Si–O 描述符雷达图" data={bondRadarData} />
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <BondBarChart title="Si–O 键长对比" dataKey="length" unit="Å" color="hsl(var(--studio-cyan))" />
        <BondBarChart title="Si–O 振动红移 / 蓝移" dataKey="freq" unit="cm⁻¹" color="hsl(var(--studio-orange))" />
        <BondBarChart title="WBI / Mayer 键级对比" dataKey="wbi" unit="" color="hsl(var(--studio-violet))" />
      </div>
      <Card>
        <CardHeader><div><CardTitle>Si–O / Si–Cl 指标表</CardTitle><CardDescription>真实结论必须来自 Gaussian log、NBO、QTAIM 或用户验证输入。</CardDescription></div>
          <Select value={selected.key} onChange={(e) => onSelect(e.target.value)} className="w-32">{moleculeLibrary.map((m) => <option key={m.key}>{m.key}</option>)}</Select></CardHeader>
        <div className="overflow-x-auto"><table className="w-full min-w-[820px] border-separate border-spacing-y-2 text-sm"><thead className="text-left text-xs uppercase tracking-[0.16em] text-studio-muted"><tr><th className="px-3 py-2">指标</th><th>DCS</th><th>MCSOMe</th><th>DMOS</th><th>单位</th></tr></thead><tbody>{sioDescriptors.map((row) => (<tr key={row.metric} className="bg-studio-panel/70 hover:bg-studio-cyan/5 transition"><td className="rounded-l-xl px-3 py-3 font-medium">{row.metric}</td><td>{row.DCS ?? "当前文件未提供"}</td><td>{row.MCSOMe ?? "当前文件未提供"}</td><td>{row.DMOS ?? "当前文件未提供"}</td><td className="rounded-r-xl">{row.unit}</td></tr>))}</tbody></table></div>
      </Card>
      <MechanismConclusion title="自动机制结论" text="当前 Si–O 键在配位后出现键长增大、Wiberg 键级降低和振动红移，说明 O 原子孤对电子参与 Lewis 酸配位并削弱 Si–O 键。若真实数据未上传，该判断仅作为示例逻辑。" />
    </div>
  );
}

function RadarPanel({ title, data }: { title: string; data: Array<Record<string, string | number>> }) {
  return (<Card><CardHeader><div><CardTitle>{title}</CardTitle></div></CardHeader><div className="h-80"><ResponsiveContainer><RadarChart data={data}><PolarGrid stroke="hsl(var(--studio-line))" /><PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} /><Radar dataKey="DCS" stroke={chartColors[0]} fill={chartColors[0]} fillOpacity={0.15} /><Radar dataKey="MCSOMe" stroke={chartColors[1]} fill={chartColors[1]} fillOpacity={0.15} /><Radar dataKey="DMOS" stroke={chartColors[2]} fill={chartColors[2]} fillOpacity={0.15} /><Legend /></RadarChart></ResponsiveContainer></div></Card>);
}

function BondBarChart({ title, dataKey, unit, color }: { title: string; dataKey: "length" | "freq" | "wbi"; unit: string; color: string }) {
  return (<Card><CardHeader><div><CardTitle>{title}</CardTitle><CardDescription>before / after coordination</CardDescription></div></CardHeader><div className="h-64"><ResponsiveContainer><BarChart data={bondBars}><CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.32} vertical={false} /><XAxis dataKey="name" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 10 }} axisLine={false} tickLine={false} /><YAxis tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} unit={unit} axisLine={false} tickLine={false} /><ChartTooltip /><Bar dataKey={dataKey} fill={color} radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div></Card>);
}
