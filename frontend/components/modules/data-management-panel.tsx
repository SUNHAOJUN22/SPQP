"use client";

import { useCallback, useMemo, useState } from "react";
import { Download, FileUp, ShieldCheck, Trash2, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { DetailPanel } from "@/components/layout/detail-panel";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { cn } from "@/lib/utils";
import type { StatusTone } from "@/types/studio";

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  status: "待解析" | "已加入队列";
}

type DataSourceRow = {
  name: string;
  type: string;
  state: string;
  evidence: string;
  tone: StatusTone;
  source: string;
  warning: string;
};

const sourceRows: DataSourceRow[] = [
  { name: "Gaussian log", type: "量子化学输出", state: "未上传真实文件", evidence: "A", tone: "gray", source: "用户上传 .log/.out", warning: "当前未上传真实 Gaussian 输出。" },
  { name: "cube 文件", type: "电子云 / ESP / MO", state: "未上传真实 cube", evidence: "A", tone: "gray", source: "用户上传 .cube", warning: "当前只有 Gaussian log 时无法显示真实电子云。" },
  { name: "NBO / QTAIM / NCI", type: "波函数后处理", state: "当前文件未提供", evidence: "A", tone: "gray", source: "用户上传只读文本", warning: "未找到对应后处理文件，不能输出确定性相互作用结论。" },
  { name: "实验 CSV", type: "GPC / MFR / gel / 流变", state: "待导入", evidence: "B", tone: "blue", source: "用户实验数据", warning: "实验条件缺失时只作为趋势表格。" },
  { name: "文献 / 报告抽取", type: "DOCX / PDF / OCR 文本", state: "C级线索", evidence: "C", tone: "yellow", source: "只读解析", warning: "文献线索不能自动升级为 A/B 级结论。" },
  { name: "示例数据", type: "MOCK / EXAMPLE", state: "可清除", evidence: "D", tone: "orange", source: "内置演示", warning: "示例数据不能作为真实科学结论。" },
];

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DataManagementPanel() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedSource, setSelectedSource] = useState<DataSourceRow>(sourceRows[0]);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setDragActive(false);
    const dropped = Array.from(event.dataTransfer.files).map((file) => ({ name: file.name, size: file.size, type: file.type || "unknown", status: "待解析" as const }));
    setFiles((prev) => [...prev, ...dropped]);
  }, []);

  const handleFileInput = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    const selected = Array.from(event.target.files).map((file) => ({ name: file.name, size: file.size, type: file.type || "unknown", status: "待解析" as const }));
    setFiles((prev) => [...prev, ...selected]);
  }, []);

  const columns: ResourceColumn<DataSourceRow>[] = useMemo(() => [
    {
      key: "source",
      header: "数据资源",
      render: (row) => (
        <div>
          <p className="font-medium text-studio-text">{row.name}</p>
          <p className="mt-1 text-xs text-studio-muted">{row.type}</p>
        </div>
      ),
    },
    {
      key: "state",
      header: "状态",
      render: (row) => <StatusBadge tone={row.tone} className="h-7 px-2">{row.state}</StatusBadge>,
    },
    {
      key: "evidence",
      header: "证据等级",
      render: (row) => <EvidenceBadge level={row.evidence} compact />,
    },
    {
      key: "warning",
      header: "结论边界",
      render: (row) => <p className="max-w-[360px] text-sm leading-6 text-studio-muted">{row.warning}</p>,
    },
  ], []);

  return (
    <div className="space-y-4">
      <PageHeader
        title="数据来源与可靠性"
        subtitle="像 Google Drive 管理科研资源一样管理 Gaussian 输出、cube、实验 CSV、文献 OCR 和示例数据；所有结论必须保留 provenance。"
        meta={<><StatusBadge tone="blue">数据来源审计</StatusBadge><StatusBadge tone="gray">仅读取，不执行文件</StatusBadge></>}
        actions={<><Button variant="secondary" icon={<Download className="h-4 w-4" />}>导出数据</Button><Button variant="danger" icon={<Trash2 className="h-4 w-4" />}>清除示例数据</Button></>}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>文件上传</CardTitle>
                <CardDescription>允许 .log / .out / .gjf / .com / .xyz / .csv / .json / .cube / .fchk；解析器只读，不执行上传文件。</CardDescription>
              </div>
              <StatusBadge tone="blue">拖放上传</StatusBadge>
            </CardHeader>
            <div
              className={cn("drop-zone cursor-pointer", dragActive && "drop-zone-active")}
              onDragOver={(event) => { event.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById("data-file-input")?.click()}
            >
              <UploadCloud className={cn("mx-auto h-12 w-12 transition", dragActive ? "text-studio-cyan" : "text-studio-muted")} />
              <p className="mt-4 font-medium">{dragActive ? "松开以上传文件" : "拖放文件到此处，或点击选择"}</p>
              <p className="mt-2 text-sm text-studio-muted">真实文件只进入只读解析流程；不会调用 Gaussian、cubegen、Multiwfn 或任意 shell。</p>
              <input id="data-file-input" type="file" className="hidden" multiple accept=".log,.out,.gjf,.com,.xyz,.csv,.json,.cube,.fchk" onChange={handleFileInput} />
            </div>
          </Card>

          <Card>
            <CardHeader>
              <div>
                <CardTitle>资源表</CardTitle>
                <CardDescription>按 A/B/C/D 证据等级管理不同数据来源，行点击后在右侧显示详情。</CardDescription>
              </div>
              <StatusBadge tone="gray">Google Drive 式资源管理</StatusBadge>
            </CardHeader>
            <ResourceTable
              rows={sourceRows}
              columns={columns}
              getRowKey={(row) => row.name}
              selectedKey={selectedSource.name}
              onSelect={setSelectedSource}
            />
          </Card>

          {files.length > 0 ? (
            <Card>
              <CardHeader>
                <div>
                  <CardTitle>本次上传队列</CardTitle>
                  <CardDescription>队列仅记录浏览器侧选择结果；正式解析仍需调用对应 API。</CardDescription>
                </div>
              </CardHeader>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={`${file.name}-${index}`} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-studio-line bg-studio-panel/70 px-4 py-3">
                    <div className="flex min-w-0 items-center gap-3">
                      <FileUp className="h-4 w-4 shrink-0 text-studio-cyan" />
                      <span className="truncate text-sm font-medium">{file.name}</span>
                      <span className="text-xs text-studio-muted">{formatSize(file.size)}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="secondary" size="sm">开始只读解析</Button>
                      <Button variant="secondary" size="sm" icon={<Trash2 className="h-3 w-3" />} onClick={() => setFiles((prev) => prev.filter((_, itemIndex) => itemIndex !== index))} aria-label="移除" />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ) : null}
        </div>

        <div className="space-y-4">
          <DetailPanel title="数据源详情" subtitle={selectedSource.name}>
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <EvidenceBadge level={selectedSource.evidence} />
                <StatusBadge tone={selectedSource.tone}>{selectedSource.state}</StatusBadge>
              </div>
              <p className="text-sm leading-6 text-studio-muted">{selectedSource.warning}</p>
              <ProvenancePanel
                title="provenance 审计"
                source={selectedSource.source}
                evidenceLevel={selectedSource.evidence}
                quality={selectedSource.state}
                warnings={[selectedSource.warning]}
                provenance="所有数据进入报告前必须保留 source_file、unit、method/basis、temperature、is_mock 与 provenance 字段。"
                paperReady={selectedSource.evidence === "A" || selectedSource.evidence === "B" ? "需要检查完整元数据后可作为候选结论" : "否，不能直接作为论文结论"}
              />
            </div>
          </DetailPanel>
          <Card>
            <CardHeader>
              <div>
                <CardTitle>安全边界</CardTitle>
                <CardDescription>外部程序默认禁用，数据管理只做资源登记和只读解析入口。</CardDescription>
              </div>
              <ShieldCheck className="h-5 w-5 text-studio-green" />
            </CardHeader>
            <ul className="space-y-2 text-sm leading-6 text-studio-muted">
              <li>不执行 Gaussian、cubegen、Multiwfn 或用户上传文件。</li>
              <li>PDF/OCR 文本属于 C 级文献线索。</li>
              <li>mock/example 数据永久标注 D 级，报告中不得写成真实结论。</li>
              <li>缺少 Gibbs、TS、π-complex 或 O→Ti 自由能时必须返回中文错误。</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
