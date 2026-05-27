"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, FileCode2, Microscope, PlayCircle, ShieldCheck } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FieldLabel, Input } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { PageHeader } from "@/components/layout/page-header";

type ToolRow = {
  name: string;
  title: string;
  description: string;
  input_schema: Record<string, string>;
};

type ResourceRow = {
  uri: string;
  title: string;
  description: string;
};

type EvidenceLevel = {
  level: string;
  name: string;
  criteria: string;
  paper_ready: string;
};

type ProtocolPayload = {
  name: string;
  quantum_tasks: string[];
  experimental_mapping: { method: string; logic: string }[];
  forbidden_behaviors: string[];
  evidence_levels: EvidenceLevel[];
  mechanism_rules: { name: string; rule: string }[];
  software_mapping: { type: string; mapping: string }[];
  report_driven_extension?: { title: string; source_role: string; required_topics: string[]; evidence_policy: string; software_targets: string[] };
  provenance: string;
};

type ReportKnowledgePayload = {
  source_id?: number | null;
  entities: Array<{ chinese_name: string; axis: string; evidence_level: string; reliability: string; paper_ready: string; software_mapping: string }>;
  keyword_counts: Record<string, number>;
  provenance: string;
};

export function McpWorkflowPanel() {
  const [tools, setTools] = useState<ToolRow[]>([]);
  const [resources, setResources] = useState<ResourceRow[]>([]);
  const [protocol, setProtocol] = useState<ProtocolPayload | null>(null);
  const [reportKnowledge, setReportKnowledge] = useState<ReportKnowledgePayload | null>(null);
  const [topic, setTopic] = useState("MCSOMe 中 Si-C 稳定性与 O→Ti 毒化");
  const [prompt, setPrompt] = useState("");
  const [runResult, setRunResult] = useState<Record<string, unknown> | null>(null);
  const [selectedToolName, setSelectedToolName] = useState("");
  const [selectedResourceUri, setSelectedResourceUri] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      apiGet<{ tools: ToolRow[] }>("/mcp/tools", controller.signal),
      apiGet<{ resources: ResourceRow[] }>("/mcp/resources", controller.signal),
      apiGet<ProtocolPayload>("/research/top-scientist-protocol", controller.signal),
      apiGet<ReportKnowledgePayload>("/literature/report-knowledge", controller.signal),
    ])
      .then(([toolPayload, resourcePayload, protocolPayload, reportPayload]) => {
        setTools(toolPayload.tools);
        setResources(resourcePayload.resources);
        setSelectedToolName((current) => current || toolPayload.tools[0]?.name || "");
        setSelectedResourceUri((current) => current || resourcePayload.resources[0]?.uri || "");
        setProtocol(protocolPayload);
        setReportKnowledge(reportPayload);
      })
      .catch((cause) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "MCP 工作流读取失败。");
        }
      });
    return () => controller.abort();
  }, []);

  async function buildPrompt() {
    setLoading(true);
    setError(null);
    try {
      const result = await apiPost<{ prompt: string }>("/research/top-scientist-prompt", { topic, include_safety: true });
      setPrompt(result.prompt);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "中文 Prompt 生成失败。");
    } finally {
      setLoading(false);
    }
  }

  async function validateExampleUpload() {
    setLoading(true);
    setError(null);
    try {
      const result = await apiPost<Record<string, unknown>>("/mcp/run-tool", {
        tool_name: "validate-upload",
        arguments: { file_name: "MCSOMe_pi_complex.log" },
      });
      setRunResult(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "安全工具执行失败。");
    } finally {
      setLoading(false);
    }
  }

  const activeTool = useMemo(() => tools.find((tool) => tool.name === selectedToolName) ?? tools[0] ?? null, [selectedToolName, tools]);
  const activeResource = useMemo(() => resources.find((resource) => resource.uri === selectedResourceUri) ?? resources[0] ?? null, [selectedResourceUri, resources]);
  const toolColumns: ResourceColumn<ToolRow>[] = [
    {
      key: "tool",
      header: "工具",
      render: (tool) => (
        <div>
          <p className="font-medium text-studio-text">{tool.title}</p>
          <p className="mt-1 font-mono text-xs text-studio-muted">{tool.name}</p>
        </div>
      ),
    },
    {
      key: "scope",
      header: "用途",
      render: (tool) => <p className="max-w-[320px] text-sm leading-6 text-studio-muted">{tool.description}</p>,
    },
    {
      key: "state",
      header: "边界",
      render: () => <StatusBadge tone="green" className="h-7 px-2">受控工具</StatusBadge>,
    },
  ];
  const resourceColumns: ResourceColumn<ResourceRow>[] = [
    {
      key: "resource",
      header: "资源",
      render: (resource) => (
        <div>
          <p className="font-medium text-studio-text">{resource.title}</p>
          <p className="mt-1 break-all font-mono text-xs text-studio-muted">{resource.uri}</p>
        </div>
      ),
    },
    {
      key: "description",
      header: "说明",
      render: (resource) => <p className="text-sm leading-6 text-studio-muted">{resource.description}</p>,
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title="MCP 自动化工作流"
        subtitle="采用 Google Cloud Console 式工具控制台：工具列表、工具详情、输入 schema、运行结果和安全边界集中呈现。"
        meta={<><StatusBadge tone="blue">仅读取与受控执行</StatusBadge><StatusBadge tone="green">不会执行 Gaussian / Multiwfn / shell</StatusBadge></>}
        actions={<><Button onClick={buildPrompt} disabled={loading} icon={<FileCode2 className="h-4 w-4" />}>生成 Prompt</Button><Button variant="secondary" onClick={validateExampleUpload} disabled={loading} icon={<PlayCircle className="h-4 w-4" />}>运行安全示例</Button></>}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>工具列表</CardTitle>
              <CardDescription>安全白名单内的 MCP 工具。行点击后在右侧查看 schema、运行结果和边界说明。</CardDescription>
            </div>
            <StatusBadge tone="green">受控工具</StatusBadge>
          </CardHeader>
          <ResourceTable
            rows={tools}
            columns={toolColumns}
            getRowKey={(tool) => tool.name}
            selectedKey={activeTool?.name}
            onSelect={(tool) => setSelectedToolName(tool.name)}
          />
          <div className="mt-4">
            <p className="text-sm font-medium">受控资源索引</p>
            <p className="mt-1 text-sm text-studio-muted">资源仅公开索引，不开放项目目录外路径。</p>
            <div className="mt-3">
              <ResourceTable
                rows={resources}
                columns={resourceColumns}
                getRowKey={(resource) => resource.uri}
                selectedKey={activeResource?.uri}
                onSelect={(resource) => setSelectedResourceUri(resource.uri)}
              />
            </div>
          </div>
        </Card>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>工具详情</CardTitle>
                <CardDescription>{activeTool?.description ?? "正在读取工具定义。"}</CardDescription>
              </div>
              <Bot className="h-5 w-5 text-studio-cyan" />
            </CardHeader>
            <div className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <p className="text-sm font-medium">输入 schema</p>
              <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap rounded-xl bg-studio-ink p-3 text-xs leading-5 text-studio-text">
                {JSON.stringify(activeTool?.input_schema ?? {}, null, 2)}
              </pre>
            </div>
            <div className="mt-3 rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <p className="text-sm font-medium">运行结果</p>
              <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap rounded-xl bg-studio-ink p-3 text-xs leading-5 text-studio-text">
                {runResult ? JSON.stringify(runResult, null, 2) : "待运行。点击“运行安全示例”后会显示 validate-upload 的只读校验结果。"}
              </pre>
            </div>
            <div className="mt-3 rounded-xl border border-studio-green/30 bg-studio-green/10 p-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-studio-green" />
                <p className="text-sm font-medium">安全边界</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-studio-muted">
                工具页不暴露 arbitrary shell；未配置 Gaussian16、cubegen、Multiwfn 时禁止外部执行。示例数据不能作为真实科学结论。
              </p>
            </div>
          </Card>
          <ProvenancePanel
            title="资源详情"
            source={activeResource?.uri}
            evidenceLevel="C"
            quality="indexed"
            provenance={activeResource?.description ?? "资源索引用于 MCP 上下文，不等同真实计算或实验结果。"}
            paperReady="否，索引资源需真实数据验证后才能写入论文结论"
          />
        </div>
      </div>
      {error ? <p className="text-sm text-studio-red">{error}</p> : null}

      <Card className="border-studio-violet/30">
        <CardHeader>
          <div>
            <CardTitle>顶尖科学家进化协议</CardTitle>
            <CardDescription>证据等级、最小可证伪任务与软件化执行映射，防止弱推断被写成确定结论</CardDescription>
          </div>
          <Microscope className="h-5 w-5 text-studio-violet" />
        </CardHeader>
        <div className="grid gap-3 lg:grid-cols-4">
          {(protocol?.evidence_levels ?? []).map((level) => (
            <div key={level.level} className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{level.level}级证据</p>
                <StatusBadge tone={level.level === "A" || level.level === "B" ? "green" : level.level === "C" ? "yellow" : "red"}>{level.name}</StatusBadge>
              </div>
              <p className="mt-3 text-sm leading-6 text-studio-muted">{level.criteria}</p>
              <p className="mt-2 text-xs leading-5 text-studio-muted">{level.paper_ready}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">机制判据必须可证伪</p>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-studio-muted">
              {(protocol?.mechanism_rules ?? []).slice(0, 4).map((rule) => (
                <li key={rule.name}>
                  <span className="text-studio-text">{rule.name}：</span>{rule.rule}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">软件化执行映射</p>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-studio-muted">
              {(protocol?.software_mapping ?? []).map((item) => (
                <li key={item.type}>
                  <span className="text-studio-text">{item.type}：</span>{item.mapping}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">量子化学任务矩阵</p>
            <p className="mt-2 text-sm leading-6 text-studio-muted">
              {(protocol?.quantum_tasks ?? []).slice(0, 8).join("、")}
            </p>
            <p className="mt-2 text-xs text-studio-muted">完整协议包含 20 类 Gaussian / Multiwfn-like 任务。</p>
          </div>
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">实验表征映射</p>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-studio-muted">
              {(protocol?.experimental_mapping ?? []).slice(0, 4).map((item) => (
                <li key={item.method}>
                  <span className="text-studio-text">{item.method}：</span>{item.logic}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">禁止行为约束</p>
            <p className="mt-2 text-sm leading-6 text-studio-muted">
              {(protocol?.forbidden_behaviors ?? []).slice(0, 8).join("；")}
            </p>
          </div>
        </div>
        <p className="mt-3 text-xs leading-5 text-studio-muted">{protocol?.provenance ?? "正在读取内置协议。"}</p>
      </Card>

      <Card className="border-studio-orange/30">
        <CardHeader>
          <div>
            <CardTitle>报告证据闭环</CardTitle>
            <CardDescription>报告 docx 抽取结果作为 C 级线索进入 Prompt、报告和可证伪软件任务</CardDescription>
          </div>
          <StatusBadge tone={reportKnowledge?.source_id ? "green" : "yellow"}>
            {reportKnowledge?.source_id ? "已导入报告" : "内置报告方向"}
          </StatusBadge>
        </CardHeader>
        <div className="grid gap-3 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="rounded-xl border border-studio-line p-4">
            <p className="text-sm font-medium">报告驱动扩展槽位</p>
            <p className="mt-2 text-sm leading-6 text-studio-muted">{protocol?.report_driven_extension?.source_role}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {(protocol?.report_driven_extension?.software_targets ?? []).map((target) => (
                <span key={target} className="rounded-pill border border-studio-line bg-studio-panel2 px-3 py-1 text-xs text-studio-muted">
                  {target}
                </span>
              ))}
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {(reportKnowledge?.entities ?? []).slice(0, 4).map((entity) => (
              <div key={`${entity.axis}-${entity.chinese_name}`} className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">{entity.chinese_name}</p>
                  <StatusBadge tone="yellow">{entity.evidence_level}级</StatusBadge>
                </div>
                <p className="mt-2 text-xs leading-5 text-studio-muted">{entity.axis}；可靠性 {entity.reliability}；论文结论：{entity.paper_ready}</p>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-studio-muted">{entity.software_mapping}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-3 rounded-xl border border-studio-orange/30 bg-studio-orange/10 p-4">
          <p className="text-sm font-medium">OCR 文本导入提示</p>
          <p className="mt-2 text-sm leading-6 text-studio-muted">
            若 PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；请在“论文与报告知识库”粘贴 OCR 文本。
            OCR 文本作为用户输入保存，证据等级仍为 C级证据，不会自动升级为真实计算或实验结论。
          </p>
        </div>
        <p className="mt-3 text-xs leading-5 text-studio-muted">{reportKnowledge?.provenance ?? "正在读取报告知识库。"}</p>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Prompt 生成器</CardTitle>
              <CardDescription>主语言中文，附带数据可靠性、证据等级和外部程序安全边界</CardDescription>
            </div>
            <StatusBadge tone="blue">Prompt 生成</StatusBadge>
          </CardHeader>
          <div className="mb-4 grid gap-3 lg:grid-cols-[1fr_auto]">
            <div>
              <FieldLabel htmlFor="mcp-topic">科研任务主题</FieldLabel>
              <Input id="mcp-topic" value={topic} onChange={(event) => setTopic(event.target.value)} />
            </div>
            <Button onClick={buildPrompt} disabled={loading} icon={<FileCode2 className="h-4 w-4" />}>生成顶尖科学家 Prompt</Button>
          </div>
          <pre className="min-h-44 overflow-auto whitespace-pre-wrap rounded-xl border border-studio-line bg-studio-ink p-4 text-sm leading-6 text-studio-text">
            {prompt || "待生成。当前没有真实 Gaussian、GoodVibes、QTAIM 或 NCI 数据时，Prompt 只定义可证伪工作流。"}
          </pre>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>工具控制台说明</CardTitle>
              <CardDescription>与 Google Cloud Console 类似，工具、schema、日志和证据边界集中在同一页。</CardDescription>
            </div>
          </CardHeader>
          <div className="space-y-3 text-sm leading-6 text-studio-muted">
            <p>所有输出必须保留 provenance；示例校验不触发文件执行。</p>
            <p>当前仅允许只读解析、白名单工具和 Prompt 生成；外部化学软件调用必须在系统设置中显式配置。</p>
            <p>当只有 C/D 级证据时，报告必须写“当前数据不足，不能形成可靠结论”。</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
