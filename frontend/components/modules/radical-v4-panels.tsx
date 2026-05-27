"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Atom, BookOpenText, FlaskConical, Link2, Play, RotateCcw, Timer } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Radar,
  RadarChart,
  PolarAngleAxis,
  PolarGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FieldLabel, Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiGet, apiPost } from "@/lib/api-client";

type PeroxideSpecies = {
  key: string;
  chinese_name: string;
  english_name: string;
  peroxide_class: string;
  has_carbonyl: boolean;
  radical_type: string;
  typical_role: string;
  example_roor_bde_kcal_mol: number | null;
  source: string;
};

type PeroxideProfile = {
  label: string;
  conversion_percent: number | null;
  activation_score: number | null;
  oxidation_risk_score: number;
  carbonyl_note: string;
  reliability_note: string;
};

type CompetitionResult = {
  label: string;
  dominant_path: string;
  series: { path: string; fraction: number }[];
  indices: Record<string, number>;
  explanation: string;
  reliability_note: string;
};

type SiCResult = {
  label: string;
  interpretations: string[];
  bde_sic_kcal_mol?: number | null;
  reliability_note: string;
};

type ResidenceResult = {
  status: string;
  advice: string;
  conversion_percent: number | null;
  axis_data: { name: string; value: number }[];
  reliability_note: string;
};

type UnifiedFramework = {
  route_comparison: { route: string; chain: string; advantage: string; risk: string }[];
  mechanism_stages: { stage: string; criteria: string[]; output: string }[];
  lcb_efficiency_formula: { formula: string; score_percent: number | null; interpretation: string };
  core_hypothesis: string;
  boss_summary: string;
  reliability_note: string;
};

type CarbonylTaxonomy = {
  title: string;
  items: { type: string; english: string; mechanistic_role: string; examples: string[]; required_data: string[]; boundary: string }[];
  summary: string;
};

type ExperimentalDesign = {
  title: string;
  layers: { name: string; variables: string[] }[];
  required_characterization: string[];
  response_model: string;
  reliability_note: string;
};

type RadicalKineticsResult = {
  species: string[];
  time_unit: string;
  series: Array<Record<string, number>>;
  final: Record<string, number>;
  provenance: string;
};

const chartColors = ["hsl(var(--studio-green))", "hsl(var(--studio-red))", "hsl(var(--studio-orange))", "hsl(var(--studio-violet))", "hsl(var(--studio-cyan))"];

function ChartTooltip() {
  return (
    <Tooltip
      contentStyle={{
        background: "hsl(var(--studio-panel))",
        border: "1px solid hsl(var(--studio-line))",
        borderRadius: 12,
        color: "hsl(var(--studio-text))"
      }}
      labelStyle={{ color: "hsl(var(--studio-text))" }}
    />
  );
}

function ReliabilityNote({ text = "示例数据，不能作为真实结论；真实判断必须来自文献抽取、用户实验或上传计算结果。" }: { text?: string }) {
  return (
    <div className="rounded-xl border border-studio-orange/40 bg-studio-orange/10 p-4 text-sm leading-6 text-studio-orange">
      {text}
    </div>
  );
}

function MetricBox({ label, value, unit }: { label: string; value: string | number | null | undefined; unit?: string }) {
  return (
    <div className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4">
      <p className="text-xs font-medium text-studio-muted">{label}</p>
      <p className="mt-2 text-xl font-medium text-studio-text">
        {value ?? "数据缺失"} {value != null && unit ? <span className="text-sm text-studio-muted">{unit}</span> : null}
      </p>
    </div>
  );
}

export function RadicalPostReactionPanel() {
  const [competition, setCompetition] = useState<CompetitionResult | null>(null);
  const [framework, setFramework] = useState<UnifiedFramework | null>(null);
  const [design, setDesign] = useState<ExperimentalDesign | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiPost<UnifiedFramework>("/analysis/unified-lcb-framework", {
      chi_insert: 0.78,
      chi_hydrolysis: 0.72,
      chi_condensation: 0.68,
      chi_radical_recombination: 0.45,
      chi_beta_scission: 0.28,
      chi_oxidation: 0.12,
      chi_ti_poison: 0.18,
      chi_over_gel: 0.15
    })
      .then(setFramework)
      .catch((cause) => setError(cause instanceof Error ? cause.message : "统一 LCB 框架读取失败。"));
    apiGet<ExperimentalDesign>("/analysis/peroxide-experimental-design")
      .then(setDesign)
      .catch(() => undefined);
  }, []);

  const radar = useMemo(() => {
    if (!competition) {
      return [
        { axis: "三级 C–H 位点", value: 65 },
        { axis: "链段运动", value: 45 },
        { axis: "立构约束", value: 55 },
        { axis: "氧化因子", value: 15 }
      ];
    }
    return [
      { axis: "三级 C–H 位点", value: competition.indices.tertiary_site_factor * 100 },
      { axis: "链段运动", value: competition.indices.amorphous_mobility * 100 },
      { axis: "立构约束", value: competition.indices.stereoregularity_constraint * 100 },
      { axis: "氧化因子", value: Math.min(100, competition.indices.oxygen_factor * 42) }
    ];
  }, [competition]);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      setCompetition(
        await apiPost<CompetitionResult>("/analysis/radical-branching-vs-scission", {
          coagent_phr: 0.35,
          ethylene_mol_percent: 4,
          isotacticity_percent: 94,
          crystallinity_percent: 48,
          oxygen_level_percent: 0.3,
          residence_time_min: 6,
          temperature_c: 185
        })
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "自由基竞争模型计算失败。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <CardHeader>
          <div>
            <StatusBadge tone="violet">V4 新模块</StatusBadge>
            <CardTitle className="mt-3 text-3xl">自由基后反应总览</CardTitle>
            <CardDescription>RO–OR 均裂 → RO• 抽氢 → PP• → β-scission / 交联 / 长链支化</CardDescription>
          </div>
          <Button onClick={run} disabled={busy} icon={<Play className="h-4 w-4" />}>{busy ? "计算中…" : "运行示例机制图"}</Button>
        </CardHeader>
        <p className="text-sm leading-7 text-studio-muted">
          该研究线用于把 Ziegler–Natta 插入后的硅烷聚烯烃样品继续接到过氧化物加工窗口：聚丙烯三级 C–H 抽氢后易发生 β-scission，
          但共剂、双官能单体、硅烷水解缩合位点和链段接近概率可把路径导向复合、交联或长链支化。
        </p>
      </Card>
      <div className="grid gap-4 xl:grid-cols-2">
        {(framework?.route_comparison ?? []).map((route) => (
          <Card key={route.route}>
            <CardHeader>
              <div>
                <CardTitle>{route.route}</CardTitle>
                <CardDescription>两条长链支化/交联路线的本质差异</CardDescription>
              </div>
              <StatusBadge tone={route.route.includes("Si") ? "green" : "orange"}>{route.route.includes("Si") ? "可设计支化" : "自由基竞争"}</StatusBadge>
            </CardHeader>
            <div className="space-y-3 text-sm leading-7 text-studio-muted">
              <p className="rounded-xl border border-studio-line bg-studio-panel2/70 p-3 font-mono">{route.chain}</p>
              <p><span className="font-medium text-studio-green">优势：</span>{route.advantage}</p>
              <p><span className="font-medium text-studio-red">风险：</span>{route.risk}</p>
            </div>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <div>
            <CardTitle>统一有效长链支化效率 ΦLCB</CardTitle>
            <CardDescription>把配位插入、水解缩合和自由基后改性压缩到同一个可证伪框架</CardDescription>
          </div>
          <StatusBadge tone={(framework?.lcb_efficiency_formula.score_percent ?? 0) >= 70 ? "green" : "yellow"}>
            {framework?.lcb_efficiency_formula.score_percent?.toFixed(0) ?? "待计算"} / 100
          </StatusBadge>
        </CardHeader>
        <p className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4 font-mono text-sm leading-7 text-studio-muted">
          {framework?.lcb_efficiency_formula.formula ?? "ΦLCB 公式待加载"}
        </p>
        <p className="mt-4 text-sm leading-7 text-studio-muted">{framework?.core_hypothesis}</p>
        <ReliabilityNote text={framework?.boss_summary} />
      </Card>
      {error ? <ReliabilityNote text={error} /> : null}
      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>降解 / 交联 / 支化竞争</CardTitle>
              <CardDescription>路径占比为参数化机制模型输出，单位：%</CardDescription>
            </div>
            <StatusBadge tone={competition ? "blue" : "gray"}>{competition?.label ?? "待计算"}</StatusBadge>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <BarChart data={competition?.series ?? []}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
                <XAxis dataKey="path" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} interval={0} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit="%" />
                <ChartTooltip />
                <Bar dataKey="fraction" name="机制占比 / %" radius={[14, 14, 4, 4]}>
                  {(competition?.series ?? []).map((_, index) => <Cell key={index} fill={chartColors[index % chartColors.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>微结构控制因子</CardTitle>
              <CardDescription>乙烯引入、等规度、结晶度与氧含量的综合投影</CardDescription>
            </div>
          </CardHeader>
          <div className="h-80">
            <ResponsiveContainer>
              <RadarChart data={radar}>
                <PolarGrid stroke="hsl(var(--studio-line))" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <Radar dataKey="value" stroke="hsl(var(--studio-cyan))" fill="hsl(var(--studio-cyan))" fillOpacity={0.3} />
                <ChartTooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
      <ReliabilityNote text={competition?.reliability_note ?? "点击运行后显示示例竞争结果；真实结论必须用 GPC、流变、凝胶分数、ESR 或真实动力学常数验证。"} />
      <Card>
        <CardHeader>
          <div>
            <CardTitle>下一步三层正交实验矩阵</CardTitle>
            <CardDescription>{design?.response_model ?? "MFR / Mw / gel / LCB index = f(T, t, peroxide, coagent, crystallinity, ethylene content)"}</CardDescription>
          </div>
          <BookOpenText className="h-5 w-5 text-studio-cyan" />
        </CardHeader>
        <div className="grid gap-3 md:grid-cols-3">
          {(design?.layers ?? []).map((layer) => (
            <div key={layer.name} className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4">
              <p className="font-medium text-studio-text">{layer.name}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {layer.variables.map((item) => (
                  <span key={item} className="rounded-pill border border-studio-line bg-studio-panel px-3 py-1 text-xs font-medium text-studio-muted">{item}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export function PeroxideLibraryPanel() {
  const [species, setSpecies] = useState<PeroxideSpecies[]>([]);
  const [taxonomy, setTaxonomy] = useState<CarbonylTaxonomy | null>(null);
  const [selected, setSelected] = useState("dicumyl-peroxide");
  const [profile, setProfile] = useState<PeroxideProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<{ species: PeroxideSpecies[] }>("/analysis/peroxide-library")
      .then((result) => setSpecies(result.species))
      .catch((cause) => setError(cause instanceof Error ? cause.message : "过氧化物结构库读取失败。"));
    apiGet<CarbonylTaxonomy>("/analysis/carbonyl-taxonomy")
      .then(setTaxonomy)
      .catch(() => undefined);
  }, []);

  const current = species.find((item) => item.key === selected) ?? species[0];

  async function evaluate() {
    if (!current) return;
    setError(null);
    try {
      setProfile(
        await apiPost<PeroxideProfile>("/analysis/peroxide-profile", {
          name: current.chinese_name,
          peroxide_class: current.peroxide_class,
          has_carbonyl: current.has_carbonyl,
          roor_bde_kcal_mol: current.example_roor_bde_kcal_mol,
          half_life_min: 4.5,
          residence_time_min: 5.5,
          temperature_c: 180,
          oxygen_level_percent: current.has_carbonyl ? 1.0 : 0.2
        })
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "过氧化物画像计算失败。");
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>过氧化物结构库</CardTitle>
            <CardDescription>Peroxide structure library / 羰基、O–O BDE、半衰期与自由基类型</CardDescription>
          </div>
          <Button onClick={evaluate} disabled={!current} icon={<FlaskConical className="h-4 w-4" />}>计算过氧化物画像</Button>
        </CardHeader>
        <div className="grid gap-4 xl:grid-cols-[0.65fr_1.35fr]">
          <div className="space-y-3">
            <FieldLabel>选择过氧化物</FieldLabel>
            <Select value={selected} onChange={(event) => setSelected(event.target.value)}>
              {species.map((item) => <option key={item.key} value={item.key}>{item.chinese_name}</option>)}
            </Select>
            {current ? (
              <div className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4 text-sm leading-7 text-studio-muted">
                <p className="font-medium text-studio-text">{current.english_name}</p>
                <p>{current.typical_role}</p>
                <p className="mt-2">自由基类型：{current.radical_type}</p>
              </div>
            ) : null}
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <MetricBox label="是否含羰基" value={current?.has_carbonyl ? "是" : "否"} />
            <MetricBox label="示例 RO–OR BDE" value={current?.example_roor_bde_kcal_mol ?? null} unit="kcal/mol" />
            <MetricBox label="停留窗口判定" value={profile?.label ?? "待计算"} />
            <MetricBox label="分解转化率" value={profile?.conversion_percent?.toFixed(1) ?? null} unit="%" />
            <MetricBox label="活化适配评分" value={profile?.activation_score?.toFixed(0) ?? null} />
            <MetricBox label="氧化风险评分" value={profile?.oxidation_risk_score?.toFixed(0) ?? null} />
          </div>
        </div>
      </Card>
      {error ? <ReliabilityNote text={error} /> : null}
      <ReliabilityNote text={profile?.carbonyl_note ?? "含羰基与否不是直接结论；必须结合 O–O BDE、半衰期、自由基产物、氧含量和副产物分析。"} />
      <Card>
        <CardHeader>
          <div>
            <CardTitle>{taxonomy?.title ?? "羰基效应三分法"}</CardTitle>
            <CardDescription>过氧化物羰基、接枝单体羰基、氧化副产物羰基必须分开评价</CardDescription>
          </div>
        </CardHeader>
        <div className="grid gap-3 xl:grid-cols-3">
          {(taxonomy?.items ?? []).map((item) => (
            <div key={item.type} className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4">
              <p className="font-medium text-studio-text">{item.type}</p>
              <p className="text-xs font-medium text-studio-muted">{item.english}</p>
              <p className="mt-3 text-sm leading-6 text-studio-muted">{item.mechanistic_role}</p>
              <p className="mt-3 text-sm leading-6 text-studio-orange">{item.boundary}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm leading-7 text-studio-muted">{taxonomy?.summary}</p>
      </Card>
    </div>
  );
}

export function SiCStabilityPanel() {
  const [sic, setSic] = useState("86");
  const [sio, setSio] = useState("105");
  const [barrier, setBarrier] = useState("15");
  const [result, setResult] = useState<SiCResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    try {
      setResult(
        await apiPost<SiCResult>("/analysis/sic-stability", {
          bde_sic_kcal_mol: Number(sic),
          bde_sio_kcal_mol: Number(sio),
          radical_attack_barrier_kcal_mol: Number(barrier)
        })
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Si–C 稳定性计算失败。");
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Si–C 键稳定性</CardTitle>
            <CardDescription>硅碳键不能只按“惰性侧基”处理，需要与 Si–O / Si–Cl 后反应通道比较</CardDescription>
          </div>
          <Button onClick={run} icon={<Link2 className="h-4 w-4" />}>评价 Si–C 稳定性</Button>
        </CardHeader>
        <div className="grid gap-4 md:grid-cols-3">
          <label className="space-y-2"><FieldLabel>Si–C BDE / kcal/mol</FieldLabel><Input value={sic} onChange={(e) => setSic(e.target.value)} /></label>
          <label className="space-y-2"><FieldLabel>Si–O BDE / kcal/mol</FieldLabel><Input value={sio} onChange={(e) => setSio(e.target.value)} /></label>
          <label className="space-y-2"><FieldLabel>自由基攻击势垒 / kcal/mol</FieldLabel><Input value={barrier} onChange={(e) => setBarrier(e.target.value)} /></label>
        </div>
      </Card>
      <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>判定结果</CardTitle>
              <CardDescription>BDE(Si–C) = G(R3Si• + •R) − G(R3Si–R)</CardDescription>
            </div>
            <StatusBadge tone={result?.label.includes("稳定") ? "green" : "yellow"}>{result?.label ?? "待计算"}</StatusBadge>
          </CardHeader>
          <MetricBox label="Si–C BDE" value={result?.bde_sic_kcal_mol ?? null} unit="kcal/mol" />
        </Card>
        <Card>
          <CardHeader><CardTitle>中文机制解释</CardTitle><Atom className="h-5 w-5 text-studio-cyan" /></CardHeader>
          <div className="space-y-3">
            {(result?.interpretations ?? ["当前尚未计算。Si–C 键稳定性需要真实 BDE 或用户核验输入支撑。"]).map((item) => (
              <div key={item} className="rounded-xl border border-studio-line bg-studio-panel2/70 p-3 text-sm leading-6 text-studio-muted">{item}</div>
            ))}
          </div>
        </Card>
      </div>
      {error ? <ReliabilityNote text={error} /> : <ReliabilityNote text={result?.reliability_note} />}
    </div>
  );
}

export function DegradationCrosslinkPanel() {
  const [result, setResult] = useState<CompetitionResult | null>(null);
  const [coagent, setCoagent] = useState("0.35");
  const [oxygen, setOxygen] = useState("0.3");

  async function run() {
    setResult(
      await apiPost<CompetitionResult>("/analysis/radical-branching-vs-scission", {
        coagent_phr: Number(coagent),
        oxygen_level_percent: Number(oxygen),
        ethylene_mol_percent: 3,
        isotacticity_percent: 93,
        crystallinity_percent: 46,
        residence_time_min: 7,
        temperature_c: 185
      })
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>降解-交联竞争图</CardTitle>
            <CardDescription>PP 过氧化物加工中 β-scission、自由基复合、共剂接枝和氧化的竞争</CardDescription>
          </div>
          <Button onClick={run} icon={<RotateCcw className="h-4 w-4" />}>更新竞争图</Button>
        </CardHeader>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2"><FieldLabel>共剂浓度 / phr</FieldLabel><Input value={coagent} onChange={(e) => setCoagent(e.target.value)} /></label>
          <label className="space-y-2"><FieldLabel>氧含量 / %</FieldLabel><Input value={oxygen} onChange={(e) => setOxygen(e.target.value)} /></label>
        </div>
      </Card>
      <Card>
        <CardHeader>
          <div>
            <CardTitle>{result?.label ?? "等待输入参数"}</CardTitle>
            <CardDescription>图表 tooltip 和坐标轴单位均为中文；空数据不输出结论</CardDescription>
          </div>
        </CardHeader>
        <div className="h-96">
          <ResponsiveContainer>
            <BarChart data={result?.series ?? []}>
              <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
              <XAxis dataKey="path" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} interval={0} />
              <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit="%" />
              <ChartTooltip />
              <Bar dataKey="fraction" name="路径占比 / %" radius={[14, 14, 4, 4]} fill="hsl(var(--studio-cyan))" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <ReliabilityNote text={result?.explanation ?? "请先运行竞争图；没有真实样品数据时，不判定聚丙烯一定降解或一定交联。"} />
    </div>
  );
}

export function RadicalKineticsPanel() {
  const [result, setResult] = useState<RadicalKineticsResult | null>(null);
  const [coagent, setCoagent] = useState("0.18");
  const [scission, setScission] = useState("0.035");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setError("");
    try {
      setResult(
        await apiPost<RadicalKineticsResult>("/merged/radical-kinetics", {
          initial: { ROOR: 1.0, RO: 0, PPH: 1.0, PP_radical: 0, monomer: 0.35, coagent: 0.12, branch: 0, scission: 0, oxidation: 0 },
          rate_constants: { k_add_c: Number(coagent), k_scission: Number(scission), k_oxidation: 0.015 },
          t_end: 12,
          steps: 90
        })
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "自由基动力学模拟失败。");
    } finally {
      setBusy(false);
    }
  }

  const final = result?.final;
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>自由基动力学</CardTitle>
            <CardDescription>RK4 示例：RO–OR 分解、RO• 抽氢、PP• β-scission、复合/接枝和氧化竞争</CardDescription>
          </div>
          <Button onClick={run} disabled={busy} icon={<Play className="h-4 w-4" />}>{busy ? "积分中…" : "运行 RK4 动力学"}</Button>
        </CardHeader>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2"><FieldLabel>共剂捕获速率 kc</FieldLabel><Input value={coagent} onChange={(e) => setCoagent(e.target.value)} /></label>
          <label className="space-y-2"><FieldLabel>β-scission 速率 kβ</FieldLabel><Input value={scission} onChange={(e) => setScission(e.target.value)} /></label>
        </div>
      </Card>
      {error ? <ReliabilityNote text={error} /> : null}
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>自由基物种随时间变化</CardTitle>
              <CardDescription>{result?.time_unit ?? "单位：示例动力学时间；真实速率常数需实验或计算校准"}</CardDescription>
            </div>
            <StatusBadge tone={result ? "blue" : "gray"}>{result ? "已积分" : "待计算"}</StatusBadge>
          </CardHeader>
          <div className="h-96">
            <ResponsiveContainer>
              <LineChart data={result?.series ?? []}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
                <XAxis dataKey="time" tick={{ fill: "hsl(var(--studio-muted))" }} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} />
                <ChartTooltip />
                <Line type="monotone" dataKey="PP_radical" name="PP•" stroke="hsl(var(--studio-orange))" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="branch" name="支化/接枝" stroke="hsl(var(--studio-green))" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="scission" name="β-断裂" stroke="hsl(var(--studio-red))" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="oxidation" name="氧化" stroke="hsl(var(--studio-violet))" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardHeader><CardTitle>终态指标</CardTitle><CardDescription>全部为模型量纲；不直接等同实验含量</CardDescription></CardHeader>
          <div className="grid gap-3">
            <MetricBox label="PP• 终态" value={final?.PP_radical?.toFixed(4) ?? null} />
            <MetricBox label="支化/接枝累积" value={final?.branch?.toFixed(4) ?? null} />
            <MetricBox label="β-断裂累积" value={final?.scission?.toFixed(4) ?? null} />
            <MetricBox label="氧化累积" value={final?.oxidation?.toFixed(4) ?? null} />
          </div>
        </Card>
      </div>
      <ReliabilityNote text={result?.provenance ?? "当前仅为参数化自由基动力学模型。真实结论需要过氧化物半衰期、ESR、GPC、MFR、凝胶分数和流变共同验证。"} />
    </div>
  );
}

export function ResidenceTimeWindowPanel() {
  const [halfLife, setHalfLife] = useState("4.5");
  const [residence, setResidence] = useState("5.5");
  const [result, setResult] = useState<ResidenceResult | null>(null);

  async function run() {
    setResult(
      await apiPost<ResidenceResult>("/analysis/residence-time-window", {
        name: "DCP 示例",
        half_life_min: Number(halfLife),
        residence_time_min: Number(residence),
        target_conversion_low_percent: 20,
        target_conversion_high_percent: 80
      })
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>停留时间窗口</CardTitle>
            <CardDescription>kd = ln2 / t1/2；转化率 = 1 − exp(−kd × 停留时间)</CardDescription>
          </div>
          <Button onClick={run} icon={<Timer className="h-4 w-4" />}>计算停留窗口</Button>
        </CardHeader>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2"><FieldLabel>半衰期 / min</FieldLabel><Input value={halfLife} onChange={(e) => setHalfLife(e.target.value)} /></label>
          <label className="space-y-2"><FieldLabel>停留时间 / min</FieldLabel><Input value={residence} onChange={(e) => setResidence(e.target.value)} /></label>
        </div>
      </Card>
      <div className="grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>{result?.status ?? "待计算"}</CardTitle>
              <CardDescription>{result?.advice ?? "输入半衰期和停留时间后计算自由基通量窗口。"}</CardDescription>
            </div>
          </CardHeader>
          <MetricBox label="过氧化物转化率" value={result?.conversion_percent?.toFixed(1) ?? null} unit="%" />
        </Card>
        <Card>
          <CardHeader><CardTitle>目标窗口对比</CardTitle><CardDescription>单位：过氧化物分解转化率 / %</CardDescription></CardHeader>
          <div className="h-72">
            <ResponsiveContainer>
              <LineChart data={result?.axis_data ?? []}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
                <XAxis dataKey="name" tick={{ fill: "hsl(var(--studio-muted))" }} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} unit="%" />
                <ChartTooltip />
                <Line type="monotone" dataKey="value" name="转化率 / %" stroke="hsl(var(--studio-cyan))" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
      <ReliabilityNote text={result?.reliability_note} />
    </div>
  );
}

export function EthyleneIsotacticityPanel() {
  const data = [
    { name: "乙烯 0%", scission: 62, branching: 22, mobility: 38 },
    { name: "乙烯 3%", scission: 54, branching: 28, mobility: 44 },
    { name: "乙烯 8%", scission: 43, branching: 34, mobility: 52 },
    { name: "低等规度", scission: 48, branching: 38, mobility: 66 },
    { name: "高等规度", scission: 58, branching: 24, mobility: 34 }
  ];
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>乙烯/等规度影响</CardTitle>
            <CardDescription>Ethylene incorporation / isotacticity / crystallinity / solid-state radical mobility</CardDescription>
          </div>
          <AlertTriangle className="h-5 w-5 text-studio-orange" />
        </CardHeader>
        <p className="text-sm leading-7 text-studio-muted">
          乙烯引入会稀释聚丙烯三级 C–H 位点并改变结晶度；等规度越高通常结晶约束越强，固态自由基扩散和链段复合概率受限。
          因此乙烯含量、等规度、结晶度与停留时间必须共同进入模型。
        </p>
      </Card>
      <Card>
        <CardHeader><CardTitle>微结构趋势示意</CardTitle><CardDescription>示例趋势 / MOCK，单位：相对指数</CardDescription></CardHeader>
        <div className="h-96">
          <ResponsiveContainer>
            <BarChart data={data}>
              <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 6" />
              <XAxis dataKey="name" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
              <YAxis tick={{ fill: "hsl(var(--studio-muted))" }} />
              <ChartTooltip />
              <Bar dataKey="scission" name="断链倾向" fill="hsl(var(--studio-red))" radius={[12, 12, 0, 0]} />
              <Bar dataKey="branching" name="支化倾向" fill="hsl(var(--studio-green))" radius={[12, 12, 0, 0]} />
              <Bar dataKey="mobility" name="链段运动性" fill="hsl(var(--studio-cyan))" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <ReliabilityNote text="该图是机制示意：真实判断需要 DSC 结晶度、NMR 等规度、乙烯含量、GPC 分子量变化和流变数据共同支撑。" />
    </div>
  );
}
