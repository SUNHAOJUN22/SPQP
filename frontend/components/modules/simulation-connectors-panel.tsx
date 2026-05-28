"use client";

import { useEffect, useMemo, useState } from "react";
import { Cable, FileCode2, ShieldCheck } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FieldLabel, Input } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { PageHeader } from "@/components/layout/page-header";

type SimulationTool = {
  id: number;
  tool_type: string;
  display_name: string;
  executable_path: string | null;
  is_configured: boolean;
  can_execute: boolean;
  default_mode: string;
  safety_level: string;
  allowed_extensions: string[];
  working_directory: string | null;
  validation_status: string;
  warnings: string[];
};

type SimulationJob = {
  id: number;
  tool_type: string;
  job_type: string;
  execution_mode: string;
  status: string;
  output_files_expected: string[];
  generated_text: string | null;
  command_template: string | null;
  will_execute: boolean;
  requires_user_confirmation: boolean;
  evidence_grade: string;
  provenance: Record<string, unknown>;
};

type ToolsPayload = {
  tools: SimulationTool[];
  safety_boundary: string;
  provenance: string;
};

type JobPayload = {
  job: SimulationJob;
  warnings: string[];
  safety_boundary: string;
};

export function SimulationConnectorsPanel() {
  const [tools, setTools] = useState<SimulationTool[]>([]);
  const [selectedToolId, setSelectedToolId] = useState<number | null>(null);
  const [jobType, setJobType] = useState("gaussian_input");
  const [moleculeName, setMoleculeName] = useState("MCSOMe");
  const [lastJob, setLastJob] = useState<SimulationJob | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    apiGet<ToolsPayload>("/simulation/tools", controller.signal)
      .then((payload) => {
        setTools(payload.tools);
        setSelectedToolId((current) => current ?? payload.tools[0]?.id ?? null);
      })
      .catch((cause) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "科学计算连接器读取失败。");
        }
      });
    return () => controller.abort();
  }, []);

  const selectedTool = useMemo(
    () => tools.find((tool) => tool.id === selectedToolId) ?? tools[0] ?? null,
    [selectedToolId, tools]
  );

  async function createTemplateJob() {
    setLoading(true);
    setError(null);
    try {
      const payload = await apiPost<JobPayload>("/simulation/jobs", {
        tool_id: selectedTool?.id ?? null,
        tool_type: selectedTool?.tool_type ?? "gaussian16",
        job_type: jobType,
        molecule_name: moleculeName,
        execution_mode: "template_only",
      });
      setLastJob(payload.job);
      setWarnings(payload.warnings);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "任务模板生成失败。");
    } finally {
      setLoading(false);
    }
  }

  const toolColumns: ResourceColumn<SimulationTool>[] = [
    {
      key: "tool",
      header: "工具",
      render: (tool) => (
        <div>
          <p className="font-medium text-studio-text">{tool.display_name}</p>
          <p className="mt-1 text-xs text-studio-muted">{tool.tool_type}</p>
        </div>
      ),
    },
    {
      key: "mode",
      header: "执行模式",
      render: (tool) => (
        <div className="space-y-1">
          <StatusBadge tone={tool.can_execute ? "yellow" : "green"}>{tool.default_mode}</StatusBadge>
          <p className="text-xs text-studio-muted">can_execute = {String(tool.can_execute)}</p>
        </div>
      ),
    },
    {
      key: "status",
      header: "配置状态",
      render: (tool) => (
        <div className="space-y-1">
          <StatusBadge tone={tool.is_configured ? "blue" : "gray"}>{tool.validation_status}</StatusBadge>
          <p className="text-xs text-studio-muted">{tool.safety_level}</p>
        </div>
      ),
    },
    {
      key: "extensions",
      header: "允许文件",
      render: (tool) => <p className="max-w-[180px] text-xs leading-5 text-studio-muted">{tool.allowed_extensions.join(", ") || "无"}</p>,
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title="科学计算连接器"
        subtitle="Simulation Connectors：连接 Gaussian、cubegen、Multiwfn、GoodVibes 与只读 parser 的受控接口层。"
        meta={<><StatusBadge tone="green">默认不执行外部程序</StatusBadge><StatusBadge tone="blue">MCP-ready</StatusBadge></>}
        actions={<Button onClick={createTemplateJob} disabled={loading} icon={<FileCode2 className="h-4 w-4" />}>生成任务模板</Button>}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(380px,0.9fr)]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>工具注册表</CardTitle>
              <CardDescription>所有外部科学计算程序默认处于 template_only 或 parse_only 模式。平台不会自动探测路径，也不会执行 version command。</CardDescription>
            </div>
            <Cable className="h-5 w-5 text-studio-cyan" />
          </CardHeader>
          <ResourceTable
            rows={tools}
            columns={toolColumns}
            getRowKey={(tool) => String(tool.id)}
            selectedKey={selectedTool ? String(selectedTool.id) : undefined}
            onSelect={(tool) => setSelectedToolId(tool.id)}
            empty={<div className="rounded-xl border border-dashed border-studio-line p-6 text-sm text-studio-muted">当前未配置外部科学计算程序。默认仅生成模板和只读解析。</div>}
          />

          <div className="mt-4 rounded-xl border border-studio-green/30 bg-studio-green/10 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-studio-green">
              <ShieldCheck className="h-4 w-4" />
              外部执行默认关闭
            </div>
            <p className="mt-2 text-sm leading-6 text-studio-muted">
              默认仅生成模板和只读解析，不执行 Gaussian、cubegen、Multiwfn 或 GoodVibes。上传真实输出文件后，解析结果才可能升级为 A 级计算证据。
            </p>
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>任务构建器</CardTitle>
                <CardDescription>创建 job draft，生成命令模板和输入文本；will_execute 始终为 false。</CardDescription>
              </div>
              <StatusBadge tone="green">will_execute = false</StatusBadge>
            </CardHeader>
            <div className="grid gap-3">
              <div className="space-y-2">
                <FieldLabel>分子名称</FieldLabel>
                <Input value={moleculeName} onChange={(event) => setMoleculeName(event.target.value)} />
              </div>
              <div className="space-y-2">
                <FieldLabel>任务类型</FieldLabel>
                <select
                  value={jobType}
                  onChange={(event) => setJobType(event.target.value)}
                  className="h-11 rounded-xl border border-studio-line bg-studio-panel px-3 text-sm text-studio-text outline-none transition focus:border-studio-cyan"
                >
                  <option value="gaussian_input">Gaussian 输入模板</option>
                  <option value="insertion_ts">插入 TS 模板</option>
                  <option value="cubegen_density">cubegen density 模板</option>
                  <option value="cubegen_esp">cubegen ESP 模板</option>
                  <option value="cubegen_homo_lumo">cubegen HOMO/LUMO 模板</option>
                  <option value="multiwfn_qtaim">Multiwfn QTAIM 脚本</option>
                  <option value="multiwfn_nci">Multiwfn NCI/RDG 脚本</option>
                  <option value="goodvibes_parse">GoodVibes 解析任务</option>
                  <option value="slurm_template">SLURM 脚本模板</option>
                </select>
              </div>
              {error ? <p className="rounded-xl border border-studio-red/40 bg-studio-red/10 p-3 text-sm text-studio-red">{error}</p> : null}
            </div>
          </Card>

          <Card>
            <CardHeader>
              <div>
                <CardTitle>命令模板预览</CardTitle>
                <CardDescription>模板可复制到外部环境，但平台不会在服务器执行。</CardDescription>
              </div>
              <StatusBadge tone={lastJob ? "blue" : "gray"}>{lastJob ? lastJob.status : "待生成"}</StatusBadge>
            </CardHeader>
            <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-xl bg-studio-ink p-3 text-xs leading-5 text-studio-text">
              {lastJob?.command_template || "当前没有任务模板。"}
            </pre>
            <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap rounded-xl bg-studio-ink p-3 text-xs leading-5 text-studio-text">
              {lastJob?.generated_text || "生成 Gaussian 输入、cubegen 模板或 Multiwfn 脚本后会显示在这里。"}
            </pre>
          </Card>

          <ProvenancePanel
            title="证据与安全边界"
            source={selectedTool?.display_name ?? "当前未配置外部科学计算程序"}
            evidenceLevel={lastJob?.evidence_grade || "D"}
            quality={selectedTool?.validation_status ?? "missing"}
            paperReady="模板和 C/D 级线索不能作为论文结论；真实输出解析后仍需人工核验。"
            provenance={`will_execute=${String(lastJob?.will_execute ?? false)}；requires_user_confirmation=${String(lastJob?.requires_user_confirmation ?? true)}；输出文件预期=${lastJob?.output_files_expected?.join(", ") || "待生成"}`}
            warnings={warnings.length ? warnings : selectedTool?.warnings ?? ["当前未配置外部程序。"]}
          />
        </div>
      </div>
    </div>
  );
}
