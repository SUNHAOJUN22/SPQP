"use client";

import { FileText } from "lucide-react";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { EmptyState } from "@/components/data/empty-state";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { SourceQualityBadge } from "@/components/data/source-quality-badge";

export type LiteratureResource = {
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

const columns: ResourceColumn<LiteratureResource>[] = [
  {
    key: "name",
    header: "资源名称",
    render: (row) => (
      <div>
        <p className="font-medium text-studio-text">{row.label}</p>
        <p className="mt-1 max-w-[320px] truncate text-xs text-studio-muted">{row.path}</p>
      </div>
    ),
  },
  {
    key: "type",
    header: "类型",
    render: (row) => <span className="rounded-pill bg-studio-panel2 px-3 py-1 text-xs text-studio-muted">{row.source_type}</span>,
  },
  {
    key: "quality",
    header: "解析质量",
    render: (row) => <SourceQualityBadge quality={row.parse_quality} />,
  },
  {
    key: "evidence",
    header: "证据",
    render: (row) => <EvidenceBadge level={row.evidence_level} compact />,
  },
  {
    key: "length",
    header: "文本长度",
    render: (row) => <span className="text-studio-muted">{row.text_length.toLocaleString("zh-CN")}</span>,
  },
  {
    key: "status",
    header: "状态",
    render: (row) => <span className={row.exists ? "text-studio-green" : "text-studio-muted"}>{row.exists ? "文件存在" : "未检测到"}</span>,
  },
];

export function LiteratureDriveView({
  resources,
  selectedKey,
  onSelect,
}: {
  resources: LiteratureResource[];
  selectedKey?: string;
  onSelect: (resource: LiteratureResource) => void;
}) {
  return (
    <ResourceTable
      rows={resources}
      columns={columns}
      getRowKey={(row) => row.label}
      selectedKey={selectedKey}
      onSelect={onSelect}
      empty={<EmptyState icon={<FileText className="h-5 w-5" />} title="当前没有真实文件实例" description="导入 DOCX、PDF 或 OCR 文本后，这里会像 Google Drive 一样显示资源、解析质量和证据等级。" />}
    />
  );
}
