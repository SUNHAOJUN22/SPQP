"use client";

import { Copy, Download, FileText, Table2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { PageHeader } from "@/components/layout/page-header";
import { CandidateHeatmap } from "@/components/shared/candidate-heatmap";
import { MechanismConclusion } from "@/components/shared/mechanism-conclusion";
import { decisionMatrix, energyRows } from "@/lib/studio-data";
import type { DecisionRow, StatusTone } from "@/types/studio";

const CONCLUSION_TEXT =
  "当前页面仅汇总示例趋势和 C/D 级线索：MCSOMe 在示例矩阵中表现为平衡候选，但没有真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 计算或真实实验数据时，不能写成确定性论文结论。正式排序必须由 ΔGpoison、ΔG‡insert、Si–C BDE、NBO E(2)、QTAIM/NCI 与实验闭环共同支撑。";

const scoreRows = decisionMatrix.map((row) => {
  const energy = energyRows.find((item) => item.molecule === row.molecule);
  return {
    ...row,
    deltaGPoison: energy?.deltaGPoison ?? null,
    deltaGBarrier: energy?.deltaGBarrier ?? null,
    krel: energy?.krel ?? null,
    source: energy?.source ?? "示例矩阵 / MOCK",
  };
});

type DecisionResource = DecisionRow & {
  deltaGPoison: number | null;
  deltaGBarrier: number | null;
  krel: number | null;
  source: string;
};

function poisonTone(value: number | null): StatusTone {
  if (value === null) return "gray";
  if (value > 5) return "green";
  if (value >= 0) return "yellow";
  return "red";
}

function poisonLabel(value: number | null): string {
  if (value === null) return "数据缺失";
  if (value > 5) return "生产性 C=C 插入占优";
  if (value >= 0) return "O→Ti 与 C=C 配位竞争";
  return "Ti 活性中心存在甲氧基毒化风险";
}

export function DecisionEnginePanel() {
  const columns: ResourceColumn<DecisionResource>[] = [
    {
      key: "molecule",
      header: "候选结构",
      render: (row) => (
        <div>
          <p className="font-medium text-studio-text">{row.molecule}</p>
          <p className="mt-1 text-xs text-studio-muted">{row.source}</p>
        </div>
      ),
    },
    {
      key: "poison",
      header: "Ti 毒化判据",
      render: (row) => (
        <div className="space-y-1">
          <StatusBadge tone={poisonTone(row.deltaGPoison)} className="h-7 px-2">
            {row.deltaGPoison === null ? "ΔGpoison 缺失" : `${row.deltaGPoison.toFixed(1)} kcal/mol`}
          </StatusBadge>
          <p className="text-xs text-studio-muted">{poisonLabel(row.deltaGPoison)}</p>
        </div>
      ),
    },
    {
      key: "insert",
      header: "插入 / 后反应",
      render: (row) => (
        <div className="text-sm leading-6 text-studio-muted">
          <p>势垒：{row.insertionBarrier}</p>
          <p>后反应：{row.postFunctionality}</p>
        </div>
      ),
    },
    {
      key: "evidence",
      header: "证据边界",
      render: () => (
        <div className="flex flex-wrap gap-2">
          <EvidenceBadge level="D" compact />
          <StatusBadge tone="gray" className="h-7 px-2">示例数据</StatusBadge>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title="量子判据引擎"
        subtitle="把 Si–O/Si–C 本征属性、TEA 捕获、Ti 毒化、插入势垒、后反应潜力和自由基风险压缩为可追溯的候选排序。"
        meta={<><EvidenceBadge level="D" /><StatusBadge tone="yellow">当前为示例趋势</StatusBadge></>}
        actions={<><Button variant="secondary" icon={<Copy className="h-4 w-4" />} onClick={() => navigator.clipboard?.writeText(CONCLUSION_TEXT)}>复制中文结论</Button><Button icon={<Download className="h-4 w-4" />}>导出判据矩阵</Button></>}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>判据资源表</CardTitle>
              <CardDescription>行点击式候选排序视图。所有数值必须保留 source、unit、method/basis 和 mock 标记。</CardDescription>
            </div>
            <StatusBadge tone="gray">Google Sheets 式矩阵</StatusBadge>
          </CardHeader>
          <ResourceTable rows={scoreRows} columns={columns} getRowKey={(row) => row.molecule} />
        </Card>

        <ProvenancePanel
          title="证据与结论边界"
          source="示例趋势 / MOCK"
          evidenceLevel="D"
          quality="example"
          warnings={[
            "当前没有真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 数据。",
            "当前没有真实实验 GPC/MFR/gel/SAOS/FTIR/NMR 数据。",
            "示例候选排序不能作为真实科学结论。",
          ]}
          provenance="判据引擎以公式和阈值组织数据，但只有 A/B 级数据才能支持论文级结论。"
          paperReady="否，当前仅可作为方法演示和下一步计算任务清单"
        />
      </div>

      <CandidateHeatmap />

      <div className="grid gap-4 lg:grid-cols-3">
        {scoreRows.map((row) => (
          <Card key={row.molecule}>
            <CardHeader>
              <div>
                <CardTitle>{row.molecule}</CardTitle>
                <CardDescription>{poisonLabel(row.deltaGPoison)}</CardDescription>
              </div>
              <StatusBadge tone={row.molecule === "MCSOMe" ? "green" : row.molecule === "DMOS" ? "red" : "blue"}>
                {row.molecule === "MCSOMe" ? "平衡候选" : row.molecule === "DMOS" ? "毒化风险" : "基准参考"}
              </StatusBadge>
            </CardHeader>
            <div className="space-y-2 text-sm text-studio-muted">
              <div className="flex justify-between gap-3"><span>Si–O 极化</span><b className="text-studio-text">{row.siOPolarity}</b></div>
              <div className="flex justify-between gap-3"><span>TEA 捕获</span><b className="text-studio-text">{row.alCapture}</b></div>
              <div className="flex justify-between gap-3"><span>Ti 毒化</span><b className="text-studio-text">{row.tiPoison}</b></div>
              <div className="flex justify-between gap-3"><span>ΔG‡insert</span><b className="text-studio-text">{row.deltaGBarrier === null ? "缺失" : `${row.deltaGBarrier} kcal/mol`}</b></div>
              <div className="flex justify-between gap-3"><span>krel</span><b className="text-studio-text">{row.krel === null ? "缺失" : row.krel}</b></div>
            </div>
          </Card>
        ))}
      </div>

      <MechanismConclusion title="中文论文式结论模板" text={CONCLUSION_TEXT} />

      <Card>
        <CardHeader>
          <div>
            <CardTitle>导出与审计</CardTitle>
            <CardDescription>导出前必须检查证据等级，避免 C/D 级线索被写成 A/B 级结论。</CardDescription>
          </div>
        </CardHeader>
        <div className="flex flex-wrap gap-3">
          <Button icon={<Copy className="h-4 w-4" />} onClick={() => navigator.clipboard?.writeText(CONCLUSION_TEXT)}>
            复制中文结论
          </Button>
          <Button variant="secondary" icon={<FileText className="h-4 w-4" />}>导出 Markdown</Button>
          <Button variant="secondary" icon={<Table2 className="h-4 w-4" />}>生成对比表格</Button>
          <Button variant="secondary" icon={<Download className="h-4 w-4" />}>下载判据矩阵</Button>
        </div>
      </Card>
    </div>
  );
}
