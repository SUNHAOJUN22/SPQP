"use client";

import { Download, FileText, FlaskConical, UploadCloud } from "lucide-react";
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { CandidateHeatmap } from "@/components/shared/candidate-heatmap";
import { chartColors } from "@/components/shared/tone-helpers";
import {
  energyRows,
  fiveEnergyRadar,
  moleculeLibrary,
  riskGauges,
  statusChinese,
} from "@/lib/studio-data";
import { cn } from "@/lib/utils";
import type { RiskGauge, StatusTone, StudioMolecule } from "@/types/studio";

const consoleCards = [
  {
    label: "数据健康状态",
    value: "C/D 级线索为主",
    note: "真实 Gaussian、cube、NBO/QTAIM 与实验数据仍需补充。",
    tone: "yellow" as StatusTone,
  },
  {
    label: "待处理任务",
    value: "补充 π / O→Ti 能量",
    note: "缺少配位竞争能量时不能计算可靠 ΔGpoison。",
    tone: "orange" as StatusTone,
  },
  {
    label: "当前最佳示例候选",
    value: "MCSOMe",
    note: "仅为示例矩阵趋势，不能写作真实论文结论。",
    tone: "green" as StatusTone,
  },
];

const taskRows = [
  {
    id: "task-log",
    name: "上传 Gaussian 输出",
    type: "数据补全",
    status: "待处理",
    owner: "量子计算",
    evidence: "A 级入口",
  },
  {
    id: "task-cube",
    name: "上传 HOMO / LUMO / ESP cube",
    type: "电子结构",
    status: "待上传",
    owner: "波函数分析",
    evidence: "A 级入口",
  },
  {
    id: "task-exp",
    name: "导入 GPC / MFR / gel / SAOS CSV",
    type: "实验闭环",
    status: "待导入",
    owner: "实验数据",
    evidence: "B 级入口",
  },
];

const taskColumns: ResourceColumn<(typeof taskRows)[number]>[] = [
  { key: "name", header: "任务", render: (row) => <span className="font-medium text-studio-text">{row.name}</span> },
  { key: "type", header: "类型", render: (row) => row.type },
  { key: "status", header: "状态", render: (row) => <StatusBadge tone="yellow">{row.status}</StatusBadge> },
  { key: "owner", header: "模块", render: (row) => row.owner },
  { key: "evidence", header: "证据入口", render: (row) => <StatusBadge tone={row.evidence.startsWith("A") ? "green" : "blue"}>{row.evidence}</StatusBadge> },
];

const moleculeColumns: ResourceColumn<StudioMolecule>[] = [
  {
    key: "molecule",
    header: "候选 / 资源",
    render: (row) => (
      <div>
        <p className="font-medium text-studio-text">{row.key}</p>
        <p className="mt-1 text-xs text-studio-muted">{row.smiles}</p>
      </div>
    ),
  },
  { key: "family", header: "分子族", render: (row) => row.family ?? "未分类" },
  { key: "sites", header: "功能位点", render: (row) => <span className="text-xs leading-5">{row.functionalSites?.join(" / ")}</span> },
  { key: "progress", header: "完成度", render: (row) => <Progress value={row.completion} /> },
  { key: "source", header: "来源", render: (row) => <StatusBadge tone="gray">{row.source.includes("MOCK") ? statusChinese.example : row.source}</StatusBadge> },
];

export function DashboardPanel({
  selected,
  onSelect,
}: {
  selected: StudioMolecule;
  onSelect: (key: string) => void;
}) {
  const candidateRows = moleculeLibrary.filter((item) => ["DCS", "MCSOMe", "DMOS"].includes(item.key));

  return (
    <div className="space-y-4">
      <PageHeader
        title="总览"
        subtitle="Google Cloud Console 式科研首页：集中显示最近任务、数据可靠性、候选排序和关键风险，不把示例趋势伪装成真实结论。"
        meta={
          <>
            <StatusBadge tone="blue">中文科研工作台</StatusBadge>
            <StatusBadge tone="yellow">示例数据不能作为真实结论</StatusBadge>
          </>
        }
        actions={
          <>
            <Button variant="secondary" icon={<UploadCloud className="h-4 w-4" />}>上传数据</Button>
            <Button icon={<FileText className="h-4 w-4" />}>生成报告</Button>
          </>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {consoleCards.map((card) => (
          <Card key={card.label} className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.14em] text-studio-muted">{card.label}</p>
                <p className="mt-3 text-xl font-medium text-studio-text">{card.value}</p>
              </div>
              <StatusBadge tone={card.tone}>{card.tone === "green" ? "可继续" : "需检查"}</StatusBadge>
            </div>
            <p className="mt-3 text-sm leading-6 text-studio-muted">{card.note}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>待处理任务</CardTitle>
              <CardDescription>按 Google Workspace 的资源逻辑组织缺失数据、解析入口和可恢复路径。</CardDescription>
            </div>
            <StatusBadge tone="yellow">待补充真实数据</StatusBadge>
          </CardHeader>
          <ResourceTable rows={taskRows} columns={taskColumns} getRowKey={(row) => row.id} />
        </Card>
        <ProvenancePanel
          title="数据可靠性提醒"
          source="Dashboard 示例矩阵 / MOCK"
          evidenceLevel="D"
          quality="missing"
          paperReady="否。当前只能作为演示和任务规划。"
          provenance="总览页不会把示例候选排序写成真实科学结论；需要真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 或实验数据升级证据等级。"
          warnings={["缺少 π-complex 与 O→Ti complex 时不能计算可靠 ΔGpoison。", "缺少 TS 与 IRC 时不能判定插入路径可靠性。"]}
        />
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>全链条机制状态</CardTitle>
            <CardDescription>从功能单体到助催化剂、Ti 配位竞争、插入 TS、IRC 和 Si–O–Si 后反应的最小闭环。</CardDescription>
          </div>
          <Button variant="secondary" size="sm" icon={<Download className="h-4 w-4" />}>下载流程图</Button>
        </CardHeader>
        <div className="grid gap-3 md:grid-cols-6">
          {[
            ["单体", "DCS / MCSOMe / DMOS"],
            ["TEA 络合", "Al←O / Al···Cl"],
            ["Ti 配位竞争", "C=C π vs O→Ti"],
            ["插入过渡态", "ΔG‡ / 虚频"],
            ["IRC 验证", "连接反应物与产物"],
            ["后反应", "水解缩合 / Si–O–Si"],
          ].map(([step, detail], index) => (
            <div key={step} className="rounded-xl border border-studio-line bg-studio-panel2/60 p-3">
              <div className="mb-2 grid h-7 w-7 place-items-center rounded-full bg-studio-cyan/15 text-xs font-medium text-studio-cyan">
                {index + 1}
              </div>
              <p className="text-sm font-medium text-studio-text">{step}</p>
              <p className="mt-1 text-xs leading-5 text-studio-muted">{detail}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[1fr_0.85fr]">
        <CandidateHeatmap />
        <RadarPanel />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        {riskGauges.map((risk) => (
          <GaugeCard key={risk.label} risk={risk} />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>候选与资源表</CardTitle>
              <CardDescription>分子候选按资源表管理；点击行可切换当前研究对象并查看右侧详情。</CardDescription>
            </div>
            <StatusBadge tone="gray">{statusChinese.example}</StatusBadge>
          </CardHeader>
          <ResourceTable
            rows={candidateRows}
            columns={moleculeColumns}
            getRowKey={(row) => row.key}
            selectedKey={selected.key}
            onSelect={(row) => onSelect(row.key)}
          />
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>当前对象</CardTitle>
              <CardDescription>{selected.name}</CardDescription>
            </div>
            <FlaskConical className="h-5 w-5 text-studio-cyan" />
          </CardHeader>
          <div className="space-y-3 text-sm">
            <InfoRow label="SMILES" value={selected.smiles} />
            <InfoRow label="取代基" value={selected.substituents} />
            <InfoRow label="分子族" value={selected.family ?? "未分类"} />
            <InfoRow label="研究角色" value={selected.role} />
            <InfoRow label="数据来源" value={selected.source} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <StatusBadge tone={selected.teaCaptureRisk}>TEA 捕获</StatusBadge>
            <StatusBadge tone={selected.poisonRisk}>O→Ti 毒化</StatusBadge>
            <StatusBadge tone={selected.insertionActivity}>插入活性</StatusBadge>
            <StatusBadge tone={selected.postPotential}>后反应潜力</StatusBadge>
          </div>
        </Card>
      </div>
    </div>
  );
}

function RadarPanel() {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>五能量项雷达图</CardTitle>
          <CardDescription>E_intrinsic、E_Al_capture、E_Ti_poison、E_insert 与 E_post 的示例评分。</CardDescription>
        </div>
        <StatusBadge tone="gray">{statusChinese.example}</StatusBadge>
      </CardHeader>
      <div className="h-80">
        <ResponsiveContainer>
          <RadarChart data={fiveEnergyRadar}>
            <PolarGrid stroke="hsl(var(--studio-line))" />
            <PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} />
            {energyRows.map((row, index) => (
              <Radar
                key={row.molecule}
                dataKey={row.molecule}
                stroke={chartColors[index]}
                fill={chartColors[index]}
                fillOpacity={0.16}
                strokeWidth={2}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function GaugeCard({ risk }: { risk: RiskGauge }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-studio-text">{risk.label}</p>
          <p className="mt-1 text-xs text-studio-muted">{risk.subtitle}</p>
        </div>
        <StatusBadge tone={risk.tone}>{risk.value}%</StatusBadge>
      </div>
      <div className="mt-4 h-2 rounded-full bg-studio-panel2">
        <div
          className={cn(
            "h-full rounded-full",
            risk.tone === "green" && "bg-studio-green",
            risk.tone === "yellow" && "bg-studio-yellow",
            risk.tone === "red" && "bg-studio-red",
            risk.tone === "blue" && "bg-studio-blue",
            risk.tone === "orange" && "bg-studio-orange",
            risk.tone === "violet" && "bg-studio-violet",
            risk.tone === "gray" && "bg-studio-muted",
          )}
          style={{ width: `${risk.value}%` }}
        />
      </div>
    </Card>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-studio-muted">{label}</p>
      <p className="mt-1 break-words leading-6 text-studio-text">{value}</p>
    </div>
  );
}
