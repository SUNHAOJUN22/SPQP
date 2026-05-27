"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  CheckCircle2,
  CloudCog,
  Database,
  FileCode2,
  FolderTree,
  GitMerge,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { useStudio } from "@/lib/store";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type SourceMap = {
  status: string;
  strategy: string;
  backend_integrated: string[];
  frontend_integrated: string[];
  docs_integrated: string[];
  dismantled_source_locations: Record<string, string>;
  active_rule: string;
};

type TaskGroups = {
  groups: Record<string, { id: string; title: string }[]>;
  total_tasks: number;
  provenance: string;
};

const quickEntrances = [
  { title: "论文与报告知识库", detail: "导入 DOCX/PDF/OCR 文本，建立 C 级文献线索。", icon: Database, tone: "yellow" },
  { title: "Gaussian 输入生成", detail: "只生成输入文件，不执行 Gaussian。", icon: FileCode2, tone: "blue" },
  { title: "Gaussian 输出解析", detail: "只读解析 log/out，输出 normalized JSON。", icon: CloudCog, tone: "green" },
  { title: "量子判据引擎", detail: "集中查看 ΔGpoison、BDE、LCB 和证据边界。", icon: Activity, tone: "violet" },
] as const;

const assetRows = [
  { key: "frontend", name: "前端来源资产", type: "integrated/origin-frontend", state: "已归档", owner: "前端 UI", evidence: "工程来源" },
  { key: "backend", name: "后端来源资产", type: "integrated/origin-backend", state: "已归档", owner: "FastAPI", evidence: "工程来源" },
  { key: "docs", name: "文档与报告资产", type: "integrated/origin-docs", state: "已归档", owner: "报告系统", evidence: "C 级线索" },
  { key: "active", name: "当前活动工作目录", type: "D:\\codex2_cataSi-O", state: "唯一活动", owner: "当前项目", evidence: "工程事实" },
];

const assetColumns: ResourceColumn<(typeof assetRows)[number]>[] = [
  { key: "name", header: "资源", render: (row) => <span className="font-medium text-studio-text">{row.name}</span> },
  { key: "type", header: "位置 / 类型", render: (row) => <span className="break-all">{row.type}</span> },
  { key: "state", header: "状态", render: (row) => <StatusBadge tone={row.state === "唯一活动" ? "green" : "blue"}>{row.state}</StatusBadge> },
  { key: "owner", header: "所属模块", render: (row) => row.owner },
  { key: "evidence", header: "证据属性", render: (row) => <StatusBadge tone={row.evidence.includes("C") ? "yellow" : "gray"}>{row.evidence}</StatusBadge> },
];

export function IntegratedHomePanel() {
  const { backendStatus } = useStudio();
  const [sourceMap, setSourceMap] = useState<SourceMap | null>(null);
  const [taskGroups, setTaskGroups] = useState<TaskGroups | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void refresh();
  }, []);

  const taskGroupRows = useMemo(() => {
    if (!taskGroups) return fallbackTaskGroups();
    return Object.entries(taskGroups.groups).map(([group, items]) => ({
      id: group,
      group,
      count: items.length,
      title: groupTitle(group),
      provenance: taskGroups.provenance,
    }));
  }, [taskGroups]);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const [sourceResponse, taskResponse] = await Promise.all([
        fetch(`${API_BASE}/integration/source-map`),
        fetch(`${API_BASE}/integration/gaussian-task-groups`),
      ]);
      if (!sourceResponse.ok || !taskResponse.ok) {
        throw new Error("整合状态 API 读取失败。");
      }
      setSourceMap((await sourceResponse.json()) as SourceMap);
      setTaskGroups((await taskResponse.json()) as TaskGroups);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "整合状态读取失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="整合总控台"
        subtitle="Google Console 式项目入口：把来源资产、当前活动目录、后端健康、Gaussian 模板和数据边界集中到一个可恢复的工作台。"
        meta={
          <>
            <StatusBadge tone={backendStatus === "connected" ? "green" : backendStatus === "checking" ? "yellow" : "red"}>
              {backendStatus === "connected" ? "后端在线" : backendStatus === "checking" ? "正在检查后端" : "后端离线"}
            </StatusBadge>
            <StatusBadge tone="blue">当前活动目录：D:\codex2_cataSi-O</StatusBadge>
          </>
        }
        actions={
          <Button onClick={refresh} disabled={loading} icon={<GitMerge className="h-4 w-4" />}>
            {loading ? "正在刷新" : "刷新整合状态"}
          </Button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-4">
        {quickEntrances.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.title} className="p-4">
              <div className="flex items-start justify-between gap-3">
                <Icon className="h-5 w-5 text-studio-cyan" />
                <StatusBadge tone={item.tone}>{item.tone === "yellow" ? "C 级线索" : "可用"}</StatusBadge>
              </div>
              <p className="mt-4 text-base font-medium text-studio-text">{item.title}</p>
              <p className="mt-2 text-sm leading-6 text-studio-muted">{item.detail}</p>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>项目资源总览</CardTitle>
              <CardDescription>原 Si-O 子项目已拆解为来源资产；当前唯一活动工作目录仍是项目根目录。</CardDescription>
            </div>
            <FolderTree className="h-5 w-5 text-studio-cyan" />
          </CardHeader>
          <ResourceTable rows={assetRows} columns={assetColumns} getRowKey={(row) => row.key} />
          {error ? <p className="mt-4 text-sm font-medium text-studio-red">{error}</p> : null}
        </Card>
        <ProvenancePanel
          title="整合边界"
          source={sourceMap?.status ?? "整合状态 API / 本地项目结构"}
          evidenceLevel="C"
          quality={sourceMap ? "readable" : "missing"}
          paperReady="否。工程整合信息不能替代真实量子化学或实验结论。"
          provenance={sourceMap?.strategy ?? "来源资产只用于工程追溯，不自动参与科学结论。"}
          warnings={["integrated/origin-* 来源资产不得被前端生产 bundle 直接引用。", "当前平台不执行 Gaussian、cubegen、Multiwfn 或用户上传文件。"]}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_0.85fr]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Gaussian 任务模板宇宙</CardTitle>
              <CardDescription>模板按任务族组织，像 Google Cloud 工具列表一样可扫描、可追溯。</CardDescription>
            </div>
            <StatusBadge tone="violet">{taskGroups?.total_tasks ?? 36} 个任务</StatusBadge>
          </CardHeader>
          <div className="grid gap-3 md:grid-cols-2">
            {taskGroupRows.map((row) => (
              <div key={row.id} className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-studio-text">{row.title}</p>
                  <StatusBadge tone="blue">{row.count}</StatusBadge>
                </div>
                <p className="mt-2 text-xs text-studio-muted">Group {row.group}</p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm leading-7 text-studio-muted">
            {taskGroups?.provenance ?? "这些模板只生成 Gaussian / utility 文本，不执行 Gaussian、cubegen 或 Multiwfn。"}
          </p>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>运行边界</CardTitle>
              <CardDescription>所有真实结论必须保留 provenance、证据等级、单位和解析质量。</CardDescription>
            </div>
            <ShieldCheck className="h-5 w-5 text-studio-green" />
          </CardHeader>
          <div className="space-y-3">
            {[
              ["不执行外部程序", "Gaussian、cubegen、Multiwfn 均默认禁用。"],
              ["只读解析", "上传文件只解析文本/网格，不执行文件。"],
              ["示例数据边界", "MOCK / example 不能写成真实科学结论。"],
              ["证据等级", "文献线索为 C 级，示例趋势为 D 级。"],
            ].map(([title, detail]) => (
              <div key={title} className="rounded-xl border border-studio-line bg-studio-panel2/60 p-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-studio-green" />
                  <p className="text-sm font-medium text-studio-text">{title}</p>
                </div>
                <p className="mt-1 text-xs leading-5 text-studio-muted">{detail}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function groupTitle(group: string) {
  const titles: Record<string, string> = {
    monomer: "单体与本征键",
    catalyst: "催化剂与助剂",
    insertion: "插入反应路径",
    post: "水解缩合后反应",
    radical: "自由基后处理",
    utility: "可视化与工具文本",
  };
  return titles[group] ?? group;
}

function fallbackTaskGroups() {
  return [
    { id: "monomer", group: "monomer", count: 7, title: "单体与本征键", provenance: "fallback" },
    { id: "catalyst", group: "catalyst", count: 7, title: "催化剂与助剂", provenance: "fallback" },
    { id: "insertion", group: "insertion", count: 6, title: "插入反应路径", provenance: "fallback" },
    { id: "post", group: "post", count: 4, title: "水解缩合后反应", provenance: "fallback" },
    { id: "radical", group: "radical", count: 7, title: "自由基后处理", provenance: "fallback" },
    { id: "utility", group: "utility", count: 5, title: "可视化与工具文本", provenance: "fallback" },
  ];
}
