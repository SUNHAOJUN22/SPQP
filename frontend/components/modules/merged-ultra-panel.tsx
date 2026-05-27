"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity,
  Atom,
  FlaskConical,
  GitMerge,
  LineChart as LineIcon,
  RefreshCw,
  Sigma,
  TestTube2,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { runTsGuidanceExample, runVmcPreview } from "@/lib/advanced-science";
import { getAllCatalysts } from "@/lib/integrated-catalyst-database";

type Inventory = {
  title: string;
  merge_strategy: string;
  backend_capabilities: string[];
  frontend_capabilities: string[];
  docs_copied: string[];
  not_merged_directly: string[];
  reliability_note: string;
};

type FourAxisDecision = {
  monomer_key: string;
  scores: {
    monomer_intrinsic: number | null;
    catalyst_compatibility: number | null;
    radical_processability: number | null;
    microphase_performance: number | null;
    overall: number | null;
  };
  label: string;
  explanation: string;
  reliability_note: string;
};

type KineticsPoint = {
  time: number;
  branch: number;
  scission: number;
  oxidation: number;
  monomer: number;
  coagent: number;
};

type KineticsResult = {
  series: KineticsPoint[];
  final: KineticsPoint;
  provenance: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

const defaultDecisionPayload = {
  monomer_key: "MCSOMe",
  data: {
    delta_g_poison_kcal_mol: 6.0,
    delta_g_insert_kcal_mol: 12.0,
    delta_g_pi_kcal_mol: -8.5,
    tea_binding_kcal_mol: -12.0,
    n_o_to_ti_e2_kcal_mol: 4.2,
    pi_c_c_to_ti_e2_kcal_mol: 10.5,
    steric_penalty: 26.0,
    electronic_guiding_score: 78.0,
    bde_sio_kcal_mol: 104.0,
    transparency_percent: 72.0,
    crystallinity_percent: 34.0,
    sequence_length: 4.2,
  },
};

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `请求失败：${response.status}`);
  }
  return (await response.json()) as T;
}

function ChartTooltip() {
  return (
    <Tooltip
      contentStyle={{
        background: "hsl(var(--studio-panel))",
        border: "1px solid hsl(var(--studio-line))",
        borderRadius: 18,
        color: "hsl(var(--studio-text))",
      }}
      labelStyle={{ color: "hsl(var(--studio-text))" }}
    />
  );
}

export function MergedUltraPanel() {
  const [inventory, setInventory] = useState<Inventory | null>(null);
  const [decision, setDecision] = useState<FourAxisDecision | null>(null);
  const [kinetics, setKinetics] = useState<KineticsResult | null>(null);
  const [tsGuidance, setTsGuidance] = useState(() => runTsGuidanceExample());
  const [vmcPreview, setVmcPreview] = useState(() => runVmcPreview());
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const integratedCatalysts = useMemo(() => getAllCatalysts(), []);

  useEffect(() => {
    void loadInventory();
  }, []);

  const radarData = useMemo(() => {
    if (!decision) {
      return [
        { axis: "单体本征", value: 0 },
        { axis: "催化兼容", value: 0 },
        { axis: "自由基加工", value: 0 },
        { axis: "微相性能", value: 0 },
      ];
    }
    return [
      { axis: "单体本征", value: decision.scores.monomer_intrinsic ?? 0 },
      { axis: "催化兼容", value: decision.scores.catalyst_compatibility ?? 0 },
      { axis: "自由基加工", value: decision.scores.radical_processability ?? 0 },
      { axis: "微相性能", value: decision.scores.microphase_performance ?? 0 },
    ];
  }, [decision]);

  async function loadInventory() {
    setError(null);
    try {
      setInventory(await requestJson<Inventory>("/merged/ultra-inventory"));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "合并清单读取失败。");
    }
  }

  async function runDecision() {
    setBusy(true);
    setError(null);
    try {
      const result = await requestJson<FourAxisDecision>("/merged/four-axis-decision", {
        method: "POST",
        body: JSON.stringify(defaultDecisionPayload),
      });
      setDecision(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "四轴判据计算失败。");
    } finally {
      setBusy(false);
    }
  }

  async function runKinetics() {
    setBusy(true);
    setError(null);
    try {
      const result = await requestJson<KineticsResult>("/merged/radical-kinetics", {
        method: "POST",
        body: JSON.stringify({ t_end: 10, steps: 80 }),
      });
      setKinetics(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "后反应动力学计算失败。");
    } finally {
      setBusy(false);
    }
  }

  function rerunLocalSciencePreview() {
    setTsGuidance(runTsGuidanceExample());
    setVmcPreview(runVmcPreview());
  }

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="grid gap-6 xl:grid-cols-[1.1fr_340px]">
          <div>
            <StatusBadge tone="violet">非破坏式合并</StatusBadge>
            <h2 className="mt-5 text-3xl font-medium tracking-normal md:text-5xl">合并工作台</h2>
            <p className="mt-3 text-sm font-medium text-studio-muted">Merged Si-O Ultra Scientific Extensions</p>
            <p className="mt-5 max-w-4xl text-sm leading-7 text-studio-muted">
              该模块吸收原 Si-O 子项目中的高级物理化学公式、四轴机制判据和后反应动力学扩展，但不覆盖当前中文主线。所有示例结果只用于验证接口与可视化，不作为真实论文结论。
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button onClick={runDecision} disabled={busy} icon={<Sigma className="h-4 w-4" />}>运行四轴判据示例</Button>
              <Button onClick={runKinetics} disabled={busy} variant="secondary" icon={<LineIcon className="h-4 w-4" />}>运行后反应动力学</Button>
              <Button onClick={loadInventory} disabled={busy} variant="ghost" icon={<RefreshCw className="h-4 w-4" />}>刷新合并清单</Button>
              <Button onClick={rerunLocalSciencePreview} variant="ghost" icon={<TestTube2 className="h-4 w-4" />}>重算本地科学预览</Button>
            </div>
          </div>
          <ProvenancePanel
            title="合并边界"
            source="integrated/origin-* 来源资产"
            evidenceLevel="D"
            quality="readable"
            paperReady="否。工程合并信息不能作为真实科学结论。"
            provenance={inventory?.merge_strategy ?? "非破坏式吸收合并：保留根项目中文主线，只迁入可复用科学核心、API 和文档。"}
            warnings={["重型旧前端页面不会直接覆盖根项目。", "合并工作台中的数值预览仍属于示例数据。"]}
          />
        </div>
      </Card>

      {error ? (
        <Card className="border-studio-red/40 bg-studio-red/10">
          <p className="text-sm font-medium text-studio-red">合并工作台错误：{error}</p>
        </Card>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>四轴机制雷达</CardTitle>
              <CardDescription>单体本征 / 催化兼容 / 自由基加工 / 微相性能</CardDescription>
            </div>
            <StatusBadge tone={decision ? "green" : "gray"}>{decision?.label ?? "待运行"}</StatusBadge>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <RadarChart data={radarData}>
                <PolarGrid stroke="hsl(var(--studio-line))" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <Radar dataKey="value" stroke="hsl(var(--studio-cyan))" fill="hsl(var(--studio-cyan))" fillOpacity={0.32} />
                <ChartTooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-3 text-sm leading-7 text-studio-muted">
            {decision?.explanation ?? "点击“运行四轴判据示例”后，会把合并自子项目的四轴模型投影到当前平台的候选单体评价中。"}
          </p>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>后反应动力学曲线</CardTitle>
              <CardDescription>自由基后处理扩展，不替代 Ziegler–Natta 插入主判据。</CardDescription>
            </div>
            <StatusBadge tone={kinetics ? "blue" : "gray"}>{kinetics ? "已计算" : "待计算"}</StatusBadge>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <LineChart data={kinetics?.series ?? []}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
                <XAxis dataKey="time" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <ChartTooltip />
                <Line type="monotone" dataKey="branch" name="支化生成" stroke="hsl(var(--studio-green))" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="scission" name="断链累积" stroke="hsl(var(--studio-red))" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="oxidation" name="氧化累积" stroke="hsl(var(--studio-orange))" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="monomer" name="单体剩余" stroke="hsl(var(--studio-cyan))" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-3 text-sm leading-7 text-studio-muted">
            {kinetics?.provenance ?? "点击“运行后反应动力学”后显示 RK4 积分示例；真实动力学常数需由实验或独立计算提供。"}
          </p>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>贝叶斯 TS 搜索指导</CardTitle>
              <CardDescription>合并自子项目的 GPR / Expected Improvement 轻量工具。</CardDescription>
            </div>
            <StatusBadge tone="blue">本地计算</StatusBadge>
          </CardHeader>
          <div className="grid gap-3 md:grid-cols-2">
            {tsGuidance.map((row, index) => (
              <div key={row.label} className="rounded-xl border border-studio-line bg-studio-panel2/75 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-studio-text">{row.label}</p>
                  <StatusBadge tone={index === 0 ? "green" : "gray"}>{index === 0 ? "优先候选" : "候选"}</StatusBadge>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-xs text-studio-muted">
                  <MetricCell label="预测得分" value={row.predictedScore.toFixed(2)} />
                  <MetricCell label="不确定度" value={row.uncertainty.toFixed(2)} />
                  <MetricCell label="EI" value={row.expectedImprovement.toFixed(3)} />
                </div>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm leading-7 text-studio-muted">
            该预览用于提示下一批过渡态搜索优先级；训练点和目标函数为示例，不会写入真实科学结论。
          </p>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>VMC 统计预览</CardTitle>
              <CardDescription>Metropolis 采样与 block average 示例。</CardDescription>
            </div>
            <StatusBadge tone="violet">示例采样</StatusBadge>
          </CardHeader>
          <div className="grid gap-3 md:grid-cols-3">
            <MetricCell label="平均能量 / Hartree" value={vmcPreview.meanEnergyHartree.toFixed(4)} />
            <MetricCell label="标准误 / Hartree" value={vmcPreview.stdErrorHartree.toFixed(4)} />
            <MetricCell label="接受率" value={`${(vmcPreview.acceptanceRatio * 100).toFixed(1)}%`} />
          </div>
          <p className="mt-4 text-sm leading-7 text-studio-muted">{vmcPreview.note}</p>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <CapabilityCard icon={<Atom className="h-5 w-5" />} title="科学公式核心" items={inventory?.backend_capabilities ?? ["等待后端合并清单"]} />
        <CapabilityCard icon={<FlaskConical className="h-5 w-5" />} title="前端接入策略" items={inventory?.frontend_capabilities ?? ["等待前端合并清单"]} />
        <CapabilityCard icon={<TestTube2 className="h-5 w-5" />} title="未直接合并项" items={inventory?.not_merged_directly ?? ["等待冲突说明"]} />
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>文档资产</CardTitle>
            <CardDescription>迁入 docs/merged-from-si-o 的设计、单位和测试说明。</CardDescription>
          </div>
          <Activity className="h-5 w-5 text-studio-green" />
        </CardHeader>
        <div className="flex flex-wrap gap-2">
          {(inventory?.docs_copied ?? ["PHYSICAL_MODELS.md", "FUNCTION_MATRIX.md", "UNIT_SYSTEM.md"]).map((doc) => (
            <span key={doc} className="rounded-pill border border-studio-line bg-studio-panel2 px-4 py-2 text-sm font-medium text-studio-muted">{doc}</span>
          ))}
        </div>
        <p className="mt-4 text-sm leading-7 text-studio-muted">
          {inventory?.reliability_note ?? "所有合并能力继续遵守中文平台的数据可靠性边界：示例数据必须标注，真实结论必须来自上传解析或用户核验。"}
        </p>
      </Card>

      <CatalystResourceTable catalysts={integratedCatalysts} />
    </div>
  );
}

function CapabilityCard({ icon, title, items }: { icon: ReactNode; title: string; items: string[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle className="flex items-center gap-2">{icon}{title}</CardTitle>
          <CardDescription>从子项目吸收的可复用能力</CardDescription>
        </div>
      </CardHeader>
      <ul className="space-y-2 text-sm leading-6 text-studio-muted">
        {items.map((item) => <li key={item}>• {item}</li>)}
      </ul>
    </Card>
  );
}

function CatalystResourceTable({ catalysts }: { catalysts: ReturnType<typeof getAllCatalysts> }) {
  const columns: ResourceColumn<(typeof catalysts)[number]>[] = [
    { key: "id", header: "条目", render: (row) => <span className="font-medium text-studio-text">{row.id}</span> },
    { key: "formula", header: "化学式", render: (row) => row.formula },
    { key: "name", header: "名称", render: (row) => row.name },
    { key: "gap", header: "HOMO-LUMO gap / eV", render: (row) => row.gapEv.toFixed(2) },
    { key: "dipole", header: "偶极矩 / Debye", render: (row) => row.dipoleMoment.magnitude.toFixed(2) },
  ];

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>已拆入根目录的催化剂数据库</CardTitle>
          <CardDescription>来源：frontend/lib/integrated-catalyst-database.ts</CardDescription>
        </div>
        <StatusBadge tone="blue">{catalysts.length} 个条目</StatusBadge>
      </CardHeader>
      <ResourceTable rows={catalysts.slice(0, 6)} columns={columns} getRowKey={(row) => row.id} />
      <p className="mt-4 text-sm leading-7 text-studio-muted">
        这些条目来自子项目示例数据库，用于界面和算法联调；仍必须标注为示例数据，不能直接作为真实量子化学结论。
      </p>
    </Card>
  );
}

function MetricCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-studio-line bg-studio-panel2/70 p-3">
      <p className="text-[11px] font-medium uppercase tracking-[0.12em] text-studio-muted">{label}</p>
      <p className="mt-2 text-lg font-medium text-studio-text">{value}</p>
    </div>
  );
}
