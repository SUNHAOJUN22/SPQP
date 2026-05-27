"use client";

import {
  CheckCircle2,
  Circle,
  Download,
  FileJson,
  FileText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { cn } from "@/lib/utils";

export type ReportSectionRow = {
  name: string;
  est: number;
  source?: string;
  evidence?: string;
};

export function ReportDocsWorkspace({
  sections,
  selected,
  format,
  preview,
  onToggleAll,
  onToggleOne,
  onSelectFormat,
}: {
  sections: ReportSectionRow[];
  selected: Set<string>;
  format: string;
  preview: string;
  onToggleAll: () => void;
  onToggleOne: (name: string) => void;
  onSelectFormat: (format: string) => void;
}) {
  const formats = ["Markdown", "HTML", "JSON", "CSV"] as const;
  return (
    <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_340px]">
      <aside className="rounded-xl border border-studio-line bg-studio-panel/82 p-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-sm font-medium">章节大纲</p>
            <p className="mt-1 text-xs text-studio-muted">
              已选择 {selected.size}/{sections.length} 个章节
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onToggleAll}>
            {selected.size === sections.length ? "全部取消" : "全选"}
          </Button>
        </div>
        <div className="mt-4 space-y-1.5">
          {sections.map((section) => {
            const checked = selected.has(section.name);
            return (
              <button
                key={section.name}
                onClick={() => onToggleOne(section.name)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm transition",
                  checked
                    ? "bg-studio-cyan/10 text-studio-text"
                    : "text-studio-muted hover:bg-studio-panel2",
                )}
              >
                {checked ? (
                  <CheckCircle2 className="h-4 w-4 text-studio-green" />
                ) : (
                  <Circle className="h-4 w-4" />
                )}
                <span className="min-w-0 flex-1 truncate">{section.name}</span>
              </button>
            );
          })}
        </div>
      </aside>
      <section className="min-w-0 rounded-xl border border-studio-line bg-studio-panel/82 p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-sm font-medium">报告预览</p>
            <p className="mt-1 text-xs text-studio-muted">
              类似于 Google Docs 的章节预览；缺失数据必须明写
            </p>
          </div>
          <StatusBadge tone="green">中文报告 · {format}</StatusBadge>
        </div>
        <pre className="max-h-[720px] max-w-full overflow-auto rounded-xl border border-studio-line bg-studio-ink p-5 font-mono text-sm leading-7 text-studio-text">
          {preview}
        </pre>
      </section>
      <aside className="rounded-xl border border-studio-line bg-studio-panel/82 p-4">
        <p className="text-sm font-medium">证据与数据来源</p>
        <p className="mt-1 text-xs leading-5 text-studio-muted">
          每个章节必须携带数据来源、证据等级、缺失数据和 mock 警告
        </p>
        <div className="mt-4 space-y-3">
          <div className="rounded-xl bg-studio-panel2/70 p-3">
            <p className="text-xs font-medium text-studio-muted">格式</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {formats.map((item) => (
                <button
                  key={item}
                  onClick={() => onSelectFormat(item)}
                  className={cn(
                    "rounded-lg px-3 py-1 text-xs font-medium",
                    format === item
                      ? "bg-gm-primary-container text-studio-cyan"
                      : "bg-studio-panel text-studio-muted",
                  )}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-studio-yellow/30 bg-studio-yellow/10 p-3 text-xs leading-5 text-studio-muted">
            当前仅有 C 级文献线索或示例数据时，不能生成 A/B 级论文结论。
          </div>
          <div className="space-y-2">
            {sections.slice(0, 7).map((section) => (
              <div
                key={section.name}
                className="rounded-xl border border-studio-line p-3"
              >
                <p className="text-xs font-medium text-studio-text">
                  {section.name}
                </p>
                <p className="mt-1 text-xs text-studio-muted">
                  {section.source ?? "示例 / 报告线索"} ·{" "}
                  {section.evidence ?? "C级证据"}
                </p>
              </div>
            ))}
          </div>
          <div className="flex flex-col gap-2">
            <Button icon={<FileText className="h-4 w-4" />}>
              生成报告
            </Button>
            <Button variant="secondary" icon={<FileJson className="h-4 w-4" />}>
              导出数据
            </Button>
            <Button variant="secondary" icon={<Download className="h-4 w-4" />}>
              下载图表
            </Button>
          </div>
        </div>
      </aside>
    </div>
  );
}
