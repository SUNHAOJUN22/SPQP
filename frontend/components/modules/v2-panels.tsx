"use client";

import { useEffect, useState } from "react";
import type React from "react";
import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Radar,
  RadarChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis
} from "recharts";
import { BookOpenText, DatabaseZap, FileWarning, FlaskConical, GitCompareArrows, Microscope, ShieldAlert } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/field";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { SourceQualityBadge } from "@/components/data/source-quality-badge";
import { PageHeader } from "@/components/layout/page-header";
import { DetailPanel } from "@/components/layout/detail-panel";
import { LiteratureDriveView, type LiteratureResource } from "@/components/workflows/literature-drive-view";
import {
  catalystModels,
  chainLengthTrend,
  dftExperimentScatter,
  experimentalRecords,
  mechanismHypotheses,
  rankingConsistency,
  thesisEntities
} from "@/lib/studio-data";
import { cn } from "@/lib/utils";

const tones = {
  cyan: "hsl(var(--studio-cyan))",
  violet: "hsl(var(--studio-violet))",
  orange: "hsl(var(--studio-orange))",
  green: "hsl(var(--studio-green))",
  red: "hsl(var(--studio-red))",
  blue: "hsl(var(--studio-blue))"
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type ReportKnowledgeEntity = {
  category: string;
  name: string;
  chinese_name: string;
  axis: string;
  evidence: string;
  confidence: number;
  evidence_level: string;
  data_source: string;
  reliability: string;
  paper_ready: string;
  software_mapping: string;
  source: string;
};

type ReportKnowledgePayload = {
  title: string;
  path?: string;
  source_id?: number | null;
  text_length?: number;
  text_preview?: string;
  entities: ReportKnowledgeEntity[];
  mechanism_models: Array<{ key: string; name: string; axis: string; hypothesis: string; falsification: string; evidence_level: string }>;
  keyword_counts: Record<string, number>;
  warnings: string[];
  provenance: string;
};

type RealInstanceItem = {
  label: string;
  title: string;
  path: string;
  exists: boolean;
  source_id: number | null;
  source_type: string;
  text_length: number;
  parse_quality: string;
  keyword_counts: Record<string, number>;
  warnings: string[];
  evidence_level: string;
  paper_ready: string;
  role: string;
};

type RealInstanceSummaryPayload = {
  instances: RealInstanceItem[];
  quality_policy: Record<string, string>;
  axis_mapping: Record<string, string[]>;
  evidence_boundary: string;
  provenance: string;
};

function SoftTooltip() {
  return (
    <Tooltip
      contentStyle={{
        background: "hsl(var(--studio-panel))",
        border: "1px solid hsl(var(--studio-line))",
        borderRadius: 18,
        color: "hsl(var(--studio-text))"
      }}
      labelStyle={{ color: "hsl(var(--studio-text))" }}
    />
  );
}

function SectionTitle({ icon, title, subtitle }: { icon: React.ReactNode; title: string; subtitle: string }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl border border-studio-line bg-studio-panel-strong text-studio-cyan shadow-elevation-2">
          {icon}
        </div>
        <div>
          <h3 className="text-lg font-medium text-studio-text">{title}</h3>
          <p className="text-sm text-studio-muted">{subtitle}</p>
        </div>
      </div>
      <StatusBadge tone="gray">论文抽取 + 示例数据 / MOCK</StatusBadge>
    </div>
  );
}

function EvidenceCard({ title, children, tone = "cyan" }: { title: string; children: React.ReactNode; tone?: keyof typeof tones }) {
  return (
    <Card className="smooth-layer border-studio-line bg-studio-panel/85 transition hover:border-studio-cyan/40">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: tones[tone] }} />
          {title}
        </CardTitle>
        <CardDescription>{children}</CardDescription>
      </CardHeader>
    </Card>
  );
}

export function LiteratureKnowledgeBase() {
  const [reportKnowledge, setReportKnowledge] = useState<ReportKnowledgePayload | null>(null);
  const [realSummary, setRealSummary] = useState<RealInstanceSummaryPayload | null>(null);
  const [reportMessage, setReportMessage] = useState("等待导入报告 docx；文献抽取结果固定为 C 级线索。");
  const [ocrMessage, setOcrMessage] = useState("OCR 文本作为用户输入导入，证据等级固定为 C 级证据。");
  const [isImportingReport, setIsImportingReport] = useState(false);
  const [isImportingOcr, setIsImportingOcr] = useState(false);
  const [reportPath, setReportPath] = useState("C:/Users/resj6/Downloads/SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx");
  const [ocrTitle, setOcrTitle] = useState("");
  const [ocrPath, setOcrPath] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [selectedInstanceKey, setSelectedInstanceKey] = useState<string | undefined>(undefined);
  const entityScores = thesisEntities.map((entity) => ({
    name: entity.chineseName,
    confidence: Math.round(entity.confidence * 100)
  }));
  const keywordChartData = Object.entries(
    realSummary?.instances.find((item) => item.label.includes("张志箭"))?.keyword_counts
      ?? realSummary?.instances.find((item) => Object.values(item.keyword_counts ?? {}).some((value) => Number(value) > 0))?.keyword_counts
      ?? {}
  ).map(([name, value]) => ({ name, value }));
  const realInstances: LiteratureResource[] = realSummary?.instances ?? [];
  const selectedInstance = realInstances.find((item) => item.label === selectedInstanceKey) ?? realInstances[0];

  async function loadRealSummary() {
    const response = await fetch(`${apiBase}/literature/real-instance-summary`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    setRealSummary((await response.json()) as RealInstanceSummaryPayload);
  }

  async function importDefaultReport() {
    setIsImportingReport(true);
    setReportMessage("正在只读解析报告 docx，不执行宏或外部化学软件。");
    try {
      const response = await fetch(`${apiBase}/literature/import-report-docx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: reportPath,
          title: "SiO/SiC/过氧化物/PP 长链支化交联降解全景深度报告"
        })
      });
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(detail?.detail || `HTTP ${response.status}`);
      }
      const payload = (await response.json()) as ReportKnowledgePayload;
      setReportKnowledge(payload);
      setReportMessage(`已导入报告线索：${payload.entities.length} 个实体，文本长度 ${payload.text_length ?? 0} 字符。证据等级仍为 C。`);
    } catch (error) {
      setReportMessage(`报告导入失败：${error instanceof Error ? error.message : "无法连接后端 API"}`);
    } finally {
      setIsImportingReport(false);
    }
  }

  async function importOcrText() {
    setIsImportingOcr(true);
    setOcrMessage("正在导入 OCR 文本；服务器只读取用户输入文本，不执行 OCR 程序。");
    try {
      const response = await fetch(`${apiBase}/literature/import-ocr-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_title: ocrTitle, source_path: ocrPath, ocr_text: ocrText })
      });
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(detail?.detail || `HTTP ${response.status}`);
      }
      const payload = await response.json() as { text_length: number; entities: unknown[]; warnings: string[] };
      setOcrMessage(`已导入 OCR 文本：${payload.text_length} 字符，抽取 ${payload.entities.length} 个报告实体；证据等级仍为 C级证据。`);
      await loadRealSummary();
    } catch (error) {
      setOcrMessage(`OCR 文本导入失败：${error instanceof Error ? error.message : "无法连接后端 API"}`);
    } finally {
      setIsImportingOcr(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBase}/literature/report-knowledge`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<ReportKnowledgePayload>;
      })
      .then((payload) => {
        setReportKnowledge(payload);
        setReportMessage(payload.source_id ? "已读取报告 docx 抽取线索。" : "尚未导入报告 docx，当前显示内置 C 级报告方向线索。");
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          setReportMessage(`报告知识库读取失败：${error instanceof Error ? error.message : "无法连接后端 API"}`);
        }
      });
    fetch(`${apiBase}/literature/real-instance-summary`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<RealInstanceSummaryPayload>;
      })
      .then((payload) => setRealSummary(payload))
      .catch(() => {});
    return () => controller.abort();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="文献与报告知识库"
        subtitle="把博士论文与 SiO/SiC/过氧化物 PP 长链支化报告统一抽取为 C 级可证伪线索"
        meta={<StatusBadge tone="yellow">C级证据 · 文献线索</StatusBadge>}
        actions={
          <>
            <Button variant="secondary" onClick={() => void importDefaultReport()} disabled={isImportingReport}>
              {isImportingReport ? "正在导入报告" : "导入文献"}
            </Button>
            <Button onClick={() => void importOcrText()} disabled={isImportingOcr || !ocrText.trim()}>
              {isImportingOcr ? "正在导入 OCR 文本" : "导入 OCR 文本"}
            </Button>
          </>
        }
      />

      <Card className="overflow-hidden border-studio-cyan/30 bg-studio-panel/90">
        <CardHeader>
          <div>
            <CardTitle>报告驱动知识映射</CardTitle>
            <CardDescription>
              来源：SiO/SiC/过氧化物/PP 长链支化交联降解全景报告；只读解析，所有线索均标记为 C 级，不能替代真实计算或实验。
            </CardDescription>
          </div>
          <StatusBadge tone={reportKnowledge?.source_id ? "green" : "yellow"}>
            {reportKnowledge?.source_id ? "报告已导入" : "内置线索"}
          </StatusBadge>
        </CardHeader>
        <div className="grid gap-4 p-5 pt-0 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4">
            <p className="text-sm leading-6 text-studio-muted">{reportMessage}</p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-studio-muted">
              {Object.entries(reportKnowledge?.keyword_counts ?? {}).map(([key, value]) => (
                <div key={key} className="rounded-xl bg-studio-panel2/40 px-3 py-2">
                  {key}: <span className="font-medium text-studio-text">{value}</span>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <p className="mb-2 text-xs font-medium text-studio-muted">报告 docx 本地路径</p>
              <Input value={reportPath} onChange={(event) => setReportPath(event.target.value)} />
              <p className="mt-2 text-xs leading-5 text-studio-muted">服务器仅读取 docx 文本；若路径不存在，会保留内置 C 级报告方向线索，不伪造抽取内容。</p>
            </div>
            <Button className="mt-4 w-full" onClick={() => void importDefaultReport()} disabled={isImportingReport}>
              {isImportingReport ? "正在导入报告" : "导入报告 docx"}
            </Button>
            <p className="mt-3 text-xs leading-5 text-studio-muted">
              {reportKnowledge?.provenance ?? "报告线索尚未读取。"}
            </p>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {(reportKnowledge?.entities ?? []).slice(0, 8).map((entity) => (
              <div key={`${entity.axis}-${entity.name}`} className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-studio-text">{entity.chinese_name}</p>
                    <p className="mt-1 text-xs text-studio-muted">{entity.axis} / {entity.category}</p>
                  </div>
                  <StatusBadge tone="yellow">{entity.evidence_level}级证据</StatusBadge>
                </div>
                <p className="mt-3 line-clamp-3 text-sm leading-6 text-studio-muted">{entity.evidence}</p>
                <p className="mt-2 text-xs leading-5 text-studio-muted">
                  可靠性：{entity.reliability}；论文结论：{entity.paper_ready}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="grid gap-3 p-5 pt-0 lg:grid-cols-3">
          {(reportKnowledge?.mechanism_models ?? []).map((model) => (
            <div key={model.key} className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium text-studio-text">{model.name}</p>
                <StatusBadge tone="yellow">{model.evidence_level}级</StatusBadge>
              </div>
              <p className="mt-2 text-xs text-studio-muted">占位机制模型</p>
              <p className="mt-3 text-sm leading-6 text-studio-muted">{model.hypothesis}</p>
              <p className="mt-3 rounded-xl bg-studio-red/10 p-3 text-xs leading-5 text-studio-muted">反证条件：{model.falsification}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="overflow-hidden border-studio-orange/30 bg-studio-panel/90">
        <CardHeader>
          <div>
            <CardTitle>真实文件实例</CardTitle>
            <CardDescription>博士论文、张志箭 PDF、PP 自由基综述 PDF 与 SiO/SiC 报告的只读解析质量、关键词和 C 级证据边界。</CardDescription>
          </div>
          <StatusBadge tone="yellow">C级证据</StatusBadge>
        </CardHeader>
        <div className="grid gap-4 p-5 pt-0 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="min-w-0 space-y-3">
            <div className="rounded-expressive border border-studio-orange/30 bg-studio-orange/10 p-4">
              <div className="flex items-start gap-3">
                <FileWarning className="mt-0.5 h-5 w-5 shrink-0 text-studio-orange" />
                <p className="text-sm leading-6 text-studio-muted">
                  PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；建议提供 OCR 文本或可复制文本版 PDF。
                </p>
              </div>
              <p className="mt-2 text-xs leading-5 text-studio-muted">
                {realSummary?.evidence_boundary ?? "真实文件实例摘要尚未读取；所有文献抽取默认属于 C级证据。"}
              </p>
            </div>
            <LiteratureDriveView
              resources={realInstances}
              selectedKey={selectedInstance?.label}
              onSelect={(resource) => setSelectedInstanceKey(resource.label)}
            />
          </div>
          <div className="space-y-4">
            <DetailPanel title="文件详情" subtitle={selectedInstance?.label ?? "选择真实文件实例查看详情"}>
              {selectedInstance ? (
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <SourceQualityBadge quality={selectedInstance.parse_quality} />
                    <EvidenceBadge level={selectedInstance.evidence_level} />
                  </div>
                  <p className="break-all text-xs leading-5 text-studio-muted">{selectedInstance.path}</p>
                  <p className="text-sm leading-6 text-studio-muted">{selectedInstance.role}</p>
                  <ProvenancePanel
                    title="证据与数据来源"
                    source={selectedInstance.source_type}
                    evidenceLevel={selectedInstance.evidence_level}
                    quality={selectedInstance.parse_quality}
                    warnings={selectedInstance.warnings}
                    provenance={selectedInstance.paper_ready}
                    paperReady={selectedInstance.paper_ready}
                  />
                </div>
              ) : (
                <p className="text-sm text-studio-muted">当前没有可选中文件实例。</p>
              )}
            </DetailPanel>
            <div className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4">
              <p className="text-sm font-medium text-studio-text">关键词统计柱状图</p>
              <p className="mt-1 text-xs text-studio-muted">显示可读文本中的 crosslink/branching、ethylene/isotacticity、peroxide/radical 等计数；乱码 PDF 的 0 值不作为缺失机制证据。</p>
              <div className="mt-4 h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={keywordChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--studio-line))" />
                    <XAxis dataKey="name" stroke="hsl(var(--studio-muted))" tick={{ fontSize: 10 }} interval={0} angle={-18} textAnchor="end" height={62} />
                    <YAxis stroke="hsl(var(--studio-muted))" tick={{ fontSize: 11 }} />
                    <SoftTooltip />
                    <Bar dataKey="value" name="关键词计数" fill={tones.orange} radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="rounded-expressive border border-studio-cyan/30 bg-studio-panel-strong p-4">
              <p className="text-sm font-medium text-studio-text">导入 OCR 文本</p>
              <p className="mt-1 text-xs leading-5 text-studio-muted">不执行外部 OCR 程序。用户粘贴的 OCR 文本按 C级证据进入报告知识库，用于替代乱码 PDF 的关键词统计。</p>
              <div className="mt-3 grid gap-2">
                <Input value={ocrTitle} onChange={(event) => setOcrTitle(event.target.value)} placeholder="OCR 来源标题" />
                <Input value={ocrPath} onChange={(event) => setOcrPath(event.target.value)} placeholder="原始 PDF 路径或来源说明" />
                <Textarea value={ocrText} onChange={(event) => setOcrText(event.target.value)} rows={5} placeholder="粘贴 OCR 文本，不上传或执行程序" />
              </div>
              <Button className="mt-3 w-full" onClick={() => void importOcrText()} disabled={isImportingOcr || !ocrText.trim()}>
                {isImportingOcr ? "正在导入 OCR 文本" : "导入 OCR 文本"}
              </Button>
              <p className="mt-3 text-xs leading-5 text-studio-muted">{ocrMessage}</p>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="overflow-hidden border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>论文研究图谱</CardTitle>
            <CardDescription>主线：Ziegler–Natta 催化剂下功能 α-烯烃与乙烯 丙烯共聚的空间位阻与电子效应分解。</CardDescription>
          </CardHeader>
          <div className="grid gap-3 p-5 pt-0 md:grid-cols-3">
            {["单体族", "催化剂模型", "机制判据"].map((group, index) => (
              <motion.div
                key={group}
                className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="text-sm font-medium text-studio-text">{group}</div>
                <div className="mt-3 space-y-2 text-sm text-studio-muted">
                  {(group === "单体族"
                    ? ["ω-烯烃基三甲硅烷", "ω-烯烃基甲基二氯硅烷", "甲氧基硅烷衍生物"]
                    : group === "催化剂模型"
                      ? ["MgCl2/TiCl4/Et", "MgCl2/BMMF/TiCl4/iBU", "TEA 助催化剂"]
                      : ["链长窗口效应", "电子效应导向", "TEA 预组织", "O→Ti 毒化"]
                  ).map((item) => (
                    <div key={item} className="rounded-full bg-studio-panel2/40 px-3 py-2">
                      {item}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </Card>

        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>抽取置信度</CardTitle>
            <CardDescription>来源为论文题目和摘要线索，详细章节级抽取仍需继续导入全文段落。</CardDescription>
          </CardHeader>
          <div className="h-64 px-4 pb-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={entityScores} layout="vertical" margin={{ left: 12, right: 12 }}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={116} tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} />
                <SoftTooltip />
                <Bar dataKey="confidence" fill={tones.cyan} radius={[0, 12, 12, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {thesisEntities.map((entity) => (
          <EvidenceCard key={`${entity.category}-${entity.name}`} title={`${entity.category}：${entity.chineseName}`} tone="violet">
            <span className="block text-studio-text">{entity.evidence}</span>
            <span className="mt-2 block text-xs text-studio-muted">来源：{entity.source}；置信度 {Math.round(entity.confidence * 100)}%</span>
          </EvidenceCard>
        ))}
      </div>

      <Card className="border-studio-line bg-studio-panel/90">
        <CardHeader>
          <CardTitle>催化剂模型库</CardTitle>
          <CardDescription>用于把论文中的实验 DFT 模型映射到计算任务和机制假设。</CardDescription>
        </CardHeader>
        <div className="grid gap-3 p-5 pt-0 lg:grid-cols-3">
          {catalystModels.map((model) => (
            <div key={model.key} className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4">
              <div className="flex items-center justify-between gap-2">
                <div className="font-medium text-studio-text">{model.name}</div>
                <StatusBadge tone="blue">模型</StatusBadge>
              </div>
              <p className="mt-3 text-sm text-studio-muted">{model.role}</p>
              <div className="mt-3 rounded-xl bg-studio-panel2/40 p-3 text-xs text-studio-muted">
                <div>活性位点：{model.activeSite}</div>
                <div className="mt-1">论文映射：{model.thesisLink}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export function ExperimentDftComparison() {
  const [selectedRecord, setSelectedRecord] = useState<(typeof experimentalRecords)[number]>(experimentalRecords[0]);
  const columns: ResourceColumn<(typeof experimentalRecords)[number]>[] = [
    {
      key: "monomer",
      header: "单体 / 体系",
      render: (record) => (
        <div>
          <p className="font-medium text-studio-text">{record.monomer}</p>
          <p className="mt-1 text-xs text-studio-muted">{record.polymerization} · {record.chainLength}</p>
        </div>
      ),
    },
    {
      key: "experiment",
      header: "实验观测",
      render: (record) => (
        <div className="text-sm leading-6 text-studio-muted">
          <p>活性：{record.activity ?? "待导入"} a.u.</p>
          <p>插入率：{record.insertionRatio ?? "待导入"} %</p>
        </div>
      ),
    },
    {
      key: "dft",
      header: "DFT 描述符",
      render: (record) => (
        <div className="text-sm leading-6 text-studio-muted">
          <p>ΔG‡：{record.deltaGBarrier ?? "缺失"} kcal/mol</p>
          <p>ΔGpoison：{record.deltaGPoison ?? "缺失"} kcal/mol</p>
        </div>
      ),
    },
    {
      key: "source",
      header: "来源",
      render: (record) => (
        <div className="flex flex-wrap gap-2">
          <EvidenceBadge level={record.source.includes("MOCK") || record.source.includes("示例") ? "D" : "C"} compact />
          <StatusBadge tone="gray" className="h-7 px-2">{record.source.includes("MOCK") || record.source.includes("示例") ? "示例数据" : "用户输入"}</StatusBadge>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="实验-DFT 对照"
        subtitle="用 Google Sheets 式资源表把聚合活性、插入率、链长效应与 ΔG‡、ΔGpoison、TEA binding、位阻惩罚和电子导向描述符放在同一套可追溯数据结构中。"
        meta={<><StatusBadge tone="yellow">示例趋势</StatusBadge><EvidenceBadge level="D" /></>}
        actions={<Button variant="secondary" icon={<GitCompareArrows className="h-4 w-4" />}>计算相关性</Button>}
      />
      <ExperimentCsvImporter />

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>实验活性 vs 插入势垒</CardTitle>
            <CardDescription>横轴为 ΔG‡，纵轴为聚合活性。真实判断必须同时导入实验 CSV 与 Gaussian 输出。</CardDescription>
          </CardHeader>
          <div className="h-72 px-4 pb-4">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ left: 8, right: 24, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 3" />
                <XAxis dataKey="barrier" name="ΔG‡" unit=" kcal/mol" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <YAxis dataKey="activity" name="聚合活性" unit=" a.u." tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <ZAxis range={[90, 280]} dataKey="insertion" />
                <SoftTooltip />
                <Scatter data={dftExperimentScatter} fill={tones.cyan}>
                  {dftExperimentScatter.map((entry) => (
                    <Cell key={entry.name} fill={(entry.activity ?? 0) > 70 ? tones.green : (entry.activity ?? 0) > 50 ? tones.orange : tones.red} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>链长效应趋势</CardTitle>
            <CardDescription>链长窗口不能只看碳数，必须同时比较体系、活性中心、π-络合物稳定性与插入 TS。</CardDescription>
          </CardHeader>
          <div className="h-72 px-4 pb-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chainLengthTrend}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <YAxis tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <SoftTooltip />
                <Legend />
                <Area dataKey="insertion" name="插入率趋势" stroke={tones.cyan} fill={tones.cyan} fillOpacity={0.18} />
                <Area dataKey="activity" name="聚合活性趋势" stroke={tones.violet} fill={tones.violet} fillOpacity={0.16} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>电子效应 / 位阻效应二维图</CardTitle>
            <CardDescription>右上区域表示电子导向强但位阻也高，是最需要 TS 与 NCI 反证的位置。</CardDescription>
          </CardHeader>
          <div className="h-72 px-4 pb-4">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ left: 8, right: 24, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="hsl(var(--studio-line))" strokeDasharray="3 3" />
                <XAxis dataKey="steric" name="位阻惩罚" unit="%" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <YAxis dataKey="electronic" name="电子导向" unit="%" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <SoftTooltip />
                <Scatter data={dftExperimentScatter} fill={tones.orange} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>DFT 排序与实验趋势一致性矩阵</CardTitle>
            <CardDescription>“实验待导入”行为空白占位，等待用户导入真实实验 CSV 后替换。</CardDescription>
          </CardHeader>
          <div className="grid gap-3 p-5 pt-0">
            {rankingConsistency.map((row) => (
              <div key={row.row} className="grid grid-cols-[120px_repeat(3,1fr)] gap-2">
                <div className="rounded-xl bg-studio-panel2/40 px-3 py-3 text-sm font-medium text-studio-text">{row.row}</div>
                {(["C4", "C6", "C8"] as const).map((key) => (
                  <div
                    key={key}
                    className="rounded-xl px-3 py-3 text-center text-sm font-medium text-white"
                    style={{ background: row[key] > 70 ? tones.green : row[key] > 40 ? tones.orange : "hsl(var(--studio-line))" }}
                  >
                    {key}: {row[key] ? `${row[key]}%` : "待导入"}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="border-studio-line bg-studio-panel/90">
        <CardHeader>
          <CardTitle>实验数据记录</CardTitle>
          <CardDescription>所有示例数值均为论文趋势抽取后的演示量化，不能作为真实科学结论。行点击后在右侧查看来源边界。</CardDescription>
        </CardHeader>
        <div className="grid gap-4 p-5 pt-0 xl:grid-cols-[minmax(0,1fr)_340px]">
          <ResourceTable
            rows={experimentalRecords}
            columns={columns}
            getRowKey={(record) => record.id}
            selectedKey={selectedRecord.id}
            onSelect={setSelectedRecord}
          />
          <ProvenancePanel
            title="实验记录来源"
            source={selectedRecord.source}
            evidenceLevel={selectedRecord.source.includes("示例") || selectedRecord.source.includes("MOCK") ? "D" : "B"}
            quality="experimental-table"
            warnings={["示例趋势不能作为真实结论；真实实验需给出样品、温度、Al/Ti 比、表征条件和重复性。"]}
            provenance={`${selectedRecord.monomer} / ${selectedRecord.catalyst} / ${selectedRecord.polymerization}`}
            paperReady="需要补充真实实验条件和原始数据"
          />
        </div>
      </Card>
    </div>
  );
}

function ExperimentCsvImporter() {
  const [csvText, setCsvText] = useState(
    "monomer,catalyst_system,polymerization,temperature_c,al_ti_ratio,activity,insertion_ratio,hexene_content,sequence_length,melting_point_c,crystallinity,transparency\nC6-DCS,MgCl2/TiCl4/TEA,乙烯共聚,70,100,80,60,,,,,\n"
  );
  const [message, setMessage] = useState("等待导入实验 CSV；导入数据按用户输入保存，不能自动升级为真实科学结论。");
  const [isImporting, setIsImporting] = useState(false);

  async function importCsv() {
    setIsImporting(true);
    try {
      const response = await fetch(`${apiBase}/experiments/import-csv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_name: "Imported Data", csv_text: csvText, source: "User" })
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = (await response.json()) as { count?: number; provenance?: string };
      setMessage(`已导入 ${payload.count ?? 0} 条实验记录；${payload.provenance ?? "请继续补充数据来源和实验条件。"}`);
    } catch (error) {
      setMessage(`导入失败：${error instanceof Error ? error.message : "API 错误"}`);
    } finally {
      setIsImporting(false);
    }
  }

  return (
    <Card className="border-studio-line bg-studio-panel/90">
      <CardHeader>
        <div>
          <CardTitle>导入实验 CSV</CardTitle>
          <CardDescription>支持中文或英文表头；导入数据作为用户输入保存，不能自动变成真实结论。</CardDescription>
        </div>
        <StatusBadge tone={message.startsWith("已导入") ? "green" : message.startsWith("导入失败") ? "red" : "gray"}>
          {isImporting ? "导入中" : "用户输入"}
        </StatusBadge>
      </CardHeader>
      <div className="grid gap-4 p-5 pt-0 lg:grid-cols-[1fr_280px]">
        <Textarea className="min-h-40" value={csvText} onChange={(event) => setCsvText(event.target.value)} />
        <div className="rounded-xl border border-studio-line bg-studio-panel2/40 p-4">
          <p className="text-sm leading-6 text-studio-muted">{message}</p>
          <Button className="mt-4 w-full" onClick={() => void importCsv()} disabled={isImporting || !csvText.trim()}>
            导入 CSV
          </Button>
        </div>
      </div>
    </Card>
  );
}

export function MechanismHypothesisEngine() {
  const radarData = mechanismHypotheses.map((item) => ({
    axis: item.name.replace("模型", ""),
    confidence: Math.round(item.confidence * 100),
    evidence: item.supportingEvidence.length * 18,
    falsifiable: item.falsification.length * 24
  }));

  return (
    <div className="space-y-6">
      <SectionTitle
        icon={<Microscope className="h-5 w-5" />}
        title="可证伪机制模型"
        subtitle="每个机制假说必须同时给出支持证据、反证条件、所需数据和当前证据等级"
      />

      <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <Card className="border-studio-line bg-studio-panel/90">
          <CardHeader>
            <CardTitle>机制可信度雷达图</CardTitle>
            <CardDescription>高置信度不等于真实结论；它只表示当前文献线索和示例描述更支持该假说。</CardDescription>
          </CardHeader>
          <div className="h-80 px-4 pb-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="hsl(var(--studio-line))" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "hsl(var(--studio-muted))", fontSize: 10 }} />
                <Radar dataKey="confidence" name="可信度" stroke={tones.cyan} fill={tones.cyan} fillOpacity={0.22} />
                <Radar dataKey="evidence" name="证据数量" stroke={tones.green} fill={tones.green} fillOpacity={0.16} />
                <Legend />
                <SoftTooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <div className="grid gap-3">
          <EvidenceCard title="当前自动判断" tone="green">
            当前示例数据更支持“链长窗口效应 + 电子效应导向 + TEA 预组织”的组合机制，而非单纯位阻主导。该判断仍依赖示例量化，必须由真实实验 CSV、Gaussian log、NBO/QTAIM 文件共同验证。
          </EvidenceCard>
          <EvidenceCard title="关键反证路径" tone="red">
            若真实 ΔGbind 很负但 ΔGπ 不稳定、ΔG‡ 升高，则 TEA 捕获不是有效预组织；若 n(O)→Ti 弱且 ΔGpoison 明显为正，则 OMe 毒化不是主导机制。
          </EvidenceCard>
          <EvidenceCard title="数据可靠性" tone="orange">
            当前页面的论文实体来自文档抽取，数值图表为示例量化。真实科学结论必须来自上传 Gaussian 输出、用户实验数据或经过审查的论文表格录入。
          </EvidenceCard>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-medium text-studio-text">机制假说卡片</h3>
          <p className="mt-1 text-sm text-studio-muted">每张卡片同时列出支持证据、反证条件、所需数据状态与可信度评分。</p>
        </div>
        <StatusBadge tone="orange">示例机制判断，需真实数据验证</StatusBadge>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {mechanismHypotheses.map((item) => (
          <Card key={item.key} className="border-studio-line bg-studio-panel/90">
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle className="text-base">{item.name}</CardTitle>
                <StatusBadge tone={item.confidence > 0.8 ? "green" : item.confidence > 0.7 ? "yellow" : "gray"}>
                  可信度 {Math.round(item.confidence * 100)}%
                </StatusBadge>
              </div>
              <CardDescription>{item.summary}</CardDescription>
            </CardHeader>
            <div className="grid gap-3 px-5 pb-5 md:grid-cols-2">
              <div className="rounded-xl border border-studio-line bg-studio-panel2/40 p-3">
                <div className="mb-2 flex items-center gap-2 text-sm font-medium text-studio-text">
                  <DatabaseZap className="h-4 w-4 text-studio-green" />
                  支持证据
                </div>
                <ul className="space-y-2 text-xs text-studio-muted">
                  {item.supportingEvidence.map((evidence) => (
                    <li key={evidence}>• {evidence}</li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl border border-studio-line bg-studio-panel2/40 p-3">
                <div className="mb-2 flex items-center gap-2 text-sm font-medium text-studio-text">
                  <FileWarning className="h-4 w-4 text-studio-red" />
                  反证条件
                </div>
                <ul className="space-y-2 text-xs text-studio-muted">
                  {item.falsification.map((evidence) => (
                    <li key={evidence}>• {evidence}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="px-5 pb-5">
              <div className="mb-2 flex items-center justify-between text-xs text-studio-muted">
                <span>数据状态：{item.currentStatus}</span>
                <span>{item.source}</span>
              </div>
              <Progress value={Math.round(item.confidence * 100)} />
            </div>
          </Card>
        ))}
      </div>

      <div className="rounded-expressive border border-studio-red/30 bg-studio-red/10 p-5 text-sm text-studio-muted">
        <div className="mb-2 flex items-center gap-2 font-medium text-studio-text">
          <ShieldAlert className="h-4 w-4 text-studio-red" />
          结论约束
        </div>
        当前仅有示例数据，不能生成真实科学结论。请导入真实 Gaussian 输出、实验 CSV、NBO/QTAIM/Multiwfn 文件后再导出正式报告。
      </div>
    </div>
  );
}

export function CubeUploadNotice() {
  return (
    <div className={cn("rounded-expressive border border-studio-line bg-studio-panel-strong p-4 text-sm text-studio-muted")}>
      未上传真实 cube 文件，当前仅显示示例等值面。支持 electron density、ESP、HOMO、LUMO、spin density cube 元数据导入；服务器只读取文件头和网格信息，不执行文件。
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant="secondary" size="sm" icon={<FlaskConical className="h-4 w-4" />}>
          上传 cube 元数据
        </Button>
        <Button variant="ghost" size="sm">
          查看导入要求
        </Button>
      </div>
    </div>
  );
}
