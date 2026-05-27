"use client";

import { useEffect, useMemo, useState } from "react";
import { Calculator, ClipboardList, FlaskConical, ShieldCheck } from "lucide-react";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FieldLabel, Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiGet, apiPost } from "@/lib/api-client";

type TaskRow = {
  groupLabel: string;
  task_id: string;
  title: string;
  english_title?: string;
  memory?: string;
  nproc?: number;
  multiplicity?: string | number;
  expected_outputs: string[];
  safety_note: string;
};

type ApiTaskRow = Omit<TaskRow, "groupLabel">;

type TaskMatrixResponse = {
  total_tasks: number;
  groups: Array<{
    group_id: string;
    label: string;
    goal: string;
    tasks: ApiTaskRow[];
  }>;
  provenance: string;
};

type WorkbenchResult = {
  warnings?: string[];
  delta_g_bind?: { kcal_mol: number; hartree: number; classification: string; formula: string };
  delta_g_poison?: { kcal_mol: number; label: string; color: "green" | "yellow" | "red"; formula: string };
  insertion_profile?: Record<string, number | null>;
  reliability_note?: string;
};

type BdeResult = {
  bond_type: string;
  bde_hartree: number;
  bde_kcal_mol: number;
  bde_ev: number;
  interpretation: string;
  formula: string;
  reliability_note: string;
};

const examplePayload = {
  complex_g_hartree: -150.025,
  fragment_g_hartree: [-100, -50],
  o_ti_complex_g_hartree: -100.0,
  pi_complex_g_hartree: -100.02,
  free_site_monomer_g_hartree: -500.0,
  ts_g_hartree: -499.98,
  product_g_hartree: -500.04,
  reference_barrier_kcal_mol: 10,
  temperature_k: 350,
  evidence_grade: "D",
  is_mock: true,
  source: "示例数据",
};

function parseFragments(value: string): number[] {
  return value
    .split(/[,\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map(Number)
    .filter((item) => Number.isFinite(item));
}

function formatJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

export function ScientificComputationPanel() {
  const [taskRows, setTaskRows] = useState<TaskRow[]>([]);
  const [taskProvenance, setTaskProvenance] = useState("正在读取计算任务矩阵。");
  const [taskError, setTaskError] = useState("");
  const [loadingTasks, setLoadingTasks] = useState(true);

  const [complexEnergy, setComplexEnergy] = useState("-150.025");
  const [fragments, setFragments] = useState("-100, -50");
  const [otiEnergy, setOtiEnergy] = useState("-100.000");
  const [piEnergy, setPiEnergy] = useState("-100.020");
  const [freeEnergy, setFreeEnergy] = useState("-500.000");
  const [tsEnergy, setTsEnergy] = useState("-499.980");
  const [productEnergy, setProductEnergy] = useState("-500.040");
  const [referenceBarrier, setReferenceBarrier] = useState("10.0");
  const [workbenchLoading, setWorkbenchLoading] = useState(false);
  const [workbenchResult, setWorkbenchResult] = useState<WorkbenchResult | null>(null);
  const [workbenchError, setWorkbenchError] = useState("");

  const [bondType, setBondType] = useState("Si-C");
  const [fragmentEnergy, setFragmentEnergy] = useState("-199.860");
  const [parentEnergy, setParentEnergy] = useState("-200.000");
  const [bdeLoading, setBdeLoading] = useState(false);
  const [bdeResult, setBdeResult] = useState<BdeResult | null>(null);
  const [bdeError, setBdeError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    apiGet<TaskMatrixResponse>("/scientific-computation/task-matrix", controller.signal)
      .then((payload) => {
        const rows = payload.groups.flatMap((group) =>
          group.tasks.map((task) => ({ ...task, groupLabel: group.label }))
        );
        setTaskRows(rows);
        setTaskProvenance(payload.provenance);
        setTaskError("");
      })
      .catch((error: Error) => {
        setTaskError(error.message || "计算任务矩阵读取失败。");
      })
      .finally(() => setLoadingTasks(false));
    return () => controller.abort();
  }, []);

  const taskColumns: ResourceColumn<TaskRow>[] = useMemo(
    () => [
      {
        key: "task",
        header: "计算任务",
        render: (row) => (
          <div>
            <p className="font-medium text-studio-text">{row.title}</p>
            <p className="mt-1 text-xs text-studio-muted">{row.english_title}</p>
            <p className="mt-1 font-mono text-xs text-studio-muted">{row.task_id}</p>
          </div>
        ),
      },
      {
        key: "group",
        header: "机制分组",
        render: (row) => <StatusBadge tone="blue">{row.groupLabel}</StatusBadge>,
      },
      {
        key: "setting",
        header: "默认资源",
        render: (row) => (
          <div className="text-sm leading-6 text-studio-muted">
            <p>内存：{row.memory ?? "命令模板"}</p>
            <p>核数：{row.nproc ?? "未指定"}</p>
            <p>自旋：{row.multiplicity ?? "需核验"}</p>
          </div>
        ),
      },
      {
        key: "outputs",
        header: "关键输出",
        render: (row) => (
          <ul className="max-w-[360px] space-y-1 text-xs leading-5 text-studio-muted">
            {row.expected_outputs.slice(0, 3).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ),
      },
    ],
    []
  );

  async function runWorkbench() {
    setWorkbenchLoading(true);
    setWorkbenchError("");
    try {
      const payload = {
        complex_g_hartree: Number(complexEnergy),
        fragment_g_hartree: parseFragments(fragments),
        o_ti_complex_g_hartree: Number(otiEnergy),
        pi_complex_g_hartree: Number(piEnergy),
        free_site_monomer_g_hartree: Number(freeEnergy),
        ts_g_hartree: Number(tsEnergy),
        product_g_hartree: Number(productEnergy),
        reference_barrier_kcal_mol: Number(referenceBarrier),
        temperature_k: 350,
        evidence_grade: "C",
        is_mock: false,
        source: "用户输入",
      };
      const result = await apiPost<WorkbenchResult>("/scientific-computation/energy-workbench", payload);
      setWorkbenchResult(result);
    } catch (error) {
      setWorkbenchError(error instanceof Error ? error.message : "能量公式计算失败。");
    } finally {
      setWorkbenchLoading(false);
    }
  }

  async function runBde() {
    setBdeLoading(true);
    setBdeError("");
    try {
      const result = await apiPost<BdeResult>("/analysis/bde", {
        bond_type: bondType,
        g_fragments_hartree: Number(fragmentEnergy),
        g_molecule_hartree: Number(parentEnergy),
        source: "用户输入",
        evidence_grade: "C",
        is_mock: false,
      });
      setBdeResult(result);
    } catch (error) {
      setBdeError(error instanceof Error ? error.message : "BDE 计算失败。");
    } finally {
      setBdeLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="科学计算工作流"
        subtitle="把 Si–O / Si–C / TEA / Ti 毒化 / 插入 / 过氧化物自由基问题转成可执行计算任务、可解析字段、可证伪判据和中文报告输出。"
        meta={
          <>
            <EvidenceBadge level="C" />
            <StatusBadge tone="green">只生成与解析，不执行外部软件</StatusBadge>
          </>
        }
        actions={
          <>
            <Button
              variant="secondary"
              icon={<ClipboardList className="h-4 w-4" />}
              onClick={() => setWorkbenchResult(examplePayload as unknown as WorkbenchResult)}
            >
              填入示例数据
            </Button>
            <Button icon={<Calculator className="h-4 w-4" />} onClick={runWorkbench} disabled={workbenchLoading}>
              {workbenchLoading ? "正在计算…" : "计算自由能差"}
            </Button>
          </>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>计算任务矩阵</CardTitle>
              <CardDescription>
                覆盖单体本征、TEA/Ti 竞争、插入 TS/IRC、水解缩合、过氧化物自由基和波函数后处理。模板只生成文本，不执行 Gaussian/cubegen/Multiwfn。
              </CardDescription>
            </div>
            <StatusBadge tone={loadingTasks ? "gray" : "blue"}>
              {loadingTasks ? "读取中" : `${taskRows.length} 个任务`}
            </StatusBadge>
          </CardHeader>
          {taskError ? (
            <div className="rounded-xl border border-studio-red/40 bg-studio-red/10 p-4 text-sm text-studio-red">{taskError}</div>
          ) : (
            <ResourceTable rows={taskRows} columns={taskColumns} getRowKey={(row) => row.task_id} />
          )}
        </Card>

        <ProvenancePanel
          title="证据与安全边界"
          source="内置任务模板 / 用户输入能量"
          evidenceLevel="C"
          quality="template-or-user-input"
          provenance={taskProvenance}
          paperReady="否，除非后续上传真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 或实验数据"
          warnings={[
            "计算模板不是计算结果。",
            "BDE 片段必须核验电荷、自旋多重度和频率。",
            "示例数据不能作为真实科学结论。",
          ]}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>能量公式工作台</CardTitle>
              <CardDescription>
                输入 Hartree 能量后计算 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex 和 krel。单位和公式由后端统一返回。
              </CardDescription>
            </div>
            <StatusBadge tone="yellow">用户输入 / C级证据</StatusBadge>
          </CardHeader>
          <div className="grid gap-3 md:grid-cols-2">
            <div><FieldLabel>G(complex) / Hartree</FieldLabel><Input className="mt-2" value={complexEnergy} onChange={(event) => setComplexEnergy(event.target.value)} /></div>
            <div><FieldLabel>ΣG(fragments) / Hartree，用逗号分隔</FieldLabel><Input className="mt-2" value={fragments} onChange={(event) => setFragments(event.target.value)} /></div>
            <div><FieldLabel>G(O→Ti complex) / Hartree</FieldLabel><Input className="mt-2" value={otiEnergy} onChange={(event) => setOtiEnergy(event.target.value)} /></div>
            <div><FieldLabel>G(C=C π-complex) / Hartree</FieldLabel><Input className="mt-2" value={piEnergy} onChange={(event) => setPiEnergy(event.target.value)} /></div>
            <div><FieldLabel>G(free site + monomer) / Hartree</FieldLabel><Input className="mt-2" value={freeEnergy} onChange={(event) => setFreeEnergy(event.target.value)} /></div>
            <div><FieldLabel>G(TS) / Hartree</FieldLabel><Input className="mt-2" value={tsEnergy} onChange={(event) => setTsEnergy(event.target.value)} /></div>
            <div><FieldLabel>G(product) / Hartree</FieldLabel><Input className="mt-2" value={productEnergy} onChange={(event) => setProductEnergy(event.target.value)} /></div>
            <div><FieldLabel>参考势垒 / kcal mol^-1</FieldLabel><Input className="mt-2" value={referenceBarrier} onChange={(event) => setReferenceBarrier(event.target.value)} /></div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button icon={<Calculator className="h-4 w-4" />} onClick={runWorkbench} disabled={workbenchLoading}>
              {workbenchLoading ? "正在计算…" : "计算自由能差"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                setComplexEnergy("-150.025");
                setFragments("-100, -50");
                setOtiEnergy("-100.000");
                setPiEnergy("-100.020");
                setFreeEnergy("-500.000");
                setTsEnergy("-499.980");
                setProductEnergy("-500.040");
                setReferenceBarrier("10.0");
              }}
            >
              恢复示例输入
            </Button>
          </div>
          {workbenchError ? <p className="mt-3 text-sm text-studio-red">{workbenchError}</p> : null}
          {workbenchResult ? (
            <div className="mt-4 grid gap-3">
              {workbenchResult.delta_g_bind ? (
                <StatusBadge tone="blue">ΔGbind = {workbenchResult.delta_g_bind.kcal_mol.toFixed(2)} kcal/mol · {workbenchResult.delta_g_bind.classification}</StatusBadge>
              ) : null}
              {workbenchResult.delta_g_poison ? (
                <StatusBadge tone={workbenchResult.delta_g_poison.color}>ΔGpoison = {workbenchResult.delta_g_poison.kcal_mol.toFixed(2)} kcal/mol · {workbenchResult.delta_g_poison.label}</StatusBadge>
              ) : null}
              <pre className="max-h-72 overflow-auto rounded-xl border border-studio-line bg-studio-panel2/60 p-4 text-xs leading-5 text-studio-muted">{formatJson(workbenchResult)}</pre>
            </div>
          ) : null}
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>BDE 计算与 Si–C 稳定性</CardTitle>
              <CardDescription>
                按 BDE = ΣG(fragments) − G(parent) 计算 Si–C、Si–O、Si–Cl 或 RO–OR 键解离能，并输出中文判据边界。
              </CardDescription>
            </div>
            <StatusBadge tone="green"><FlaskConical className="mr-1 h-3.5 w-3.5" />BDE</StatusBadge>
          </CardHeader>
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <FieldLabel>键类型</FieldLabel>
              <Select className="mt-2" value={bondType} onChange={(event) => setBondType(event.target.value)}>
                <option value="Si-C">Si–C</option>
                <option value="Si-O">Si–O</option>
                <option value="Si-Cl">Si–Cl</option>
                <option value="RO-OR">RO–OR</option>
              </Select>
            </div>
            <div><FieldLabel>证据等级</FieldLabel><Input className="mt-2" readOnly value="C级证据 / 用户输入" /></div>
            <div><FieldLabel>ΣG(fragments) / Hartree</FieldLabel><Input className="mt-2" value={fragmentEnergy} onChange={(event) => setFragmentEnergy(event.target.value)} /></div>
            <div><FieldLabel>G(parent) / Hartree</FieldLabel><Input className="mt-2" value={parentEnergy} onChange={(event) => setParentEnergy(event.target.value)} /></div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button icon={<Calculator className="h-4 w-4" />} onClick={runBde} disabled={bdeLoading}>
              {bdeLoading ? "正在计算…" : "计算 BDE"}
            </Button>
            <Button variant="secondary" icon={<ShieldCheck className="h-4 w-4" />} disabled title="需要真实片段输出才能升级证据等级">
              A/B 级结论需真实数据
            </Button>
          </div>
          {bdeError ? <p className="mt-3 text-sm text-studio-red">{bdeError}</p> : null}
          {bdeResult ? (
            <div className="mt-4 space-y-3">
              <div className="grid gap-3 sm:grid-cols-3">
                <StatusBadge tone="blue">{bdeResult.bde_kcal_mol.toFixed(2)} kcal/mol</StatusBadge>
                <StatusBadge tone="gray">{bdeResult.bde_hartree.toFixed(6)} Hartree</StatusBadge>
                <StatusBadge tone="gray">{bdeResult.bde_ev.toFixed(3)} eV</StatusBadge>
              </div>
              <p className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4 text-sm leading-6 text-studio-muted">{bdeResult.interpretation}</p>
              <pre className="max-h-72 overflow-auto rounded-xl border border-studio-line bg-studio-panel2/60 p-4 text-xs leading-5 text-studio-muted">{formatJson(bdeResult)}</pre>
            </div>
          ) : null}
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>报告输出边界</CardTitle>
            <CardDescription>本页产生的计算结果将进入中文报告的“科学计算工作流”章节，但证据等级会保留，不会自动升级为真实论文结论。</CardDescription>
          </div>
          <StatusBadge tone="gray">缺数据不下结论</StatusBadge>
        </CardHeader>
        <div className="grid gap-3 text-sm leading-6 text-studio-muted md:grid-cols-3">
          <p>若缺少 Gibbs 自由能，报告写入“当前文件未提供吉布斯自由能，不能计算自由能差”。</p>
          <p>若缺少 π-complex 或 O→Ti complex，报告写入“无法计算 ΔGpoison”。</p>
          <p>若仅有示例数据，报告写入“示例数据，不能作为真实结论”。</p>
        </div>
      </Card>
    </div>
  );
}
