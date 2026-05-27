"use client";
import { useState } from "react";
import { FileText } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { ReportDocsWorkspace, type ReportSectionRow } from "@/components/workflows/report-docs-workspace";

const sections: ReportSectionRow[] = [
  { name: "项目概述", est: 200 },
  { name: "报告知识映射", est: 500, source: "报告 docx / 文献线索", evidence: "C级证据" },
  { name: "真实文件实例测试", est: 450, source: "真实 DOCX/PDF/OCR 摘要", evidence: "C级证据" },
  { name: "分子结构与研究对象", est: 500 },
  { name: "Si–O 键本征属性", est: 800 },
  { name: "Si–C 连接稳定性", est: 500 },
  { name: "电子云密度与静电势分析", est: 600 },
  { name: "前线轨道分析", est: 500 },
  { name: "电荷布居与电荷转移", est: 400 },
  { name: "NBO 给体-受体相互作用", est: 700 },
  { name: "QTAIM / NCI 弱相互作用分析", est: 600 },
  { name: "TEA 助催化剂作用", est: 500 },
  { name: "Ti 活性中心毒化判据", est: 400 },
  { name: "插入反应自由能面", est: 500 },
  { name: "水解缩合后反应", est: 400 },
  { name: "PP β-scission 与交联竞争", est: 650 },
  { name: "羰基三分法", est: 480 },
  { name: "乙烯/等规度/结晶度影响", est: 480 },
  { name: "可证伪机制模型", est: 700 },
  { name: "软件化执行接口", est: 420 },
  { name: "DCS / MCSOMe / DMOS 最终排序", est: 300 },
  { name: "数据可靠性说明", est: 200 },
  { name: "Gaussian 输入文件附录", est: 300 },
];

const formats = ["Markdown", "HTML", "JSON", "CSV"] as const;

export function ReportsPanel() {
  const [selected, setSelected] = useState<Set<string>>(() => new Set(sections.map((s) => s.name)));
  const [format, setFormat] = useState<(typeof formats)[number]>("Markdown");

  function toggleAll() {
    if (selected.size === sections.length) setSelected(new Set());
    else setSelected(new Set(sections.map((s) => s.name)));
  }

  function toggleOne(name: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }

  const totalWords = sections.filter((s) => selected.has(s.name)).reduce((sum, s) => sum + s.est, 0);
  const preview = `# 硅氧硅碳催化量子机理平台报告

> 数据可靠性说明
> 示例数据、C 级文献线索、用户输入和真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 或实验数据必须分开标注。
> 当前仅有 C 级文献线索时，不能生成 A/B 级论文结论。

## 已选章节 (${selected.size}/${sections.length})
${sections.filter((s) => selected.has(s.name)).map((s) => `- ${s.name}`).join("\n")}

## 真实文件实例测试
博士论文 docx、张志箭 PDF、PP 自由基综述 PDF 和报告 docx 的解析质量、warnings、关键词统计和 C 级证据边界会自动写入本节。

## 证据与数据来源
每个章节需要写明数据来源、证据等级、缺失数据、mock 警告和是否可写入论文结论。

## 导出格式：${format}

当前报告预览采用 Google Docs 式工作区：左侧章节大纲，中间报告预览，右侧证据与数据来源。`;

  return (
    <div className="space-y-4">
      <PageHeader
        title="中文科研报告"
        subtitle={`Google Docs 风格报告工作台：章节大纲、报告预览、证据与数据来源三栏组织 · 约 ${totalWords} 字`}
        meta={<StatusBadge tone="yellow">C级证据边界始终可见</StatusBadge>}
      />
      <ReportDocsWorkspace
        sections={sections}
        selected={selected}
        format={format}
        preview={preview}
        onToggleAll={toggleAll}
        onToggleOne={toggleOne}
        onSelectFormat={(next) => setFormat(next as (typeof formats)[number])}
      />
      <Card className="min-w-0">
        <CardHeader>
          <div>
            <CardTitle>导出中心</CardTitle>
            <CardDescription>正式导出由后端 `/api/reports/generate` 生成，前端此处保持章节与证据结构预览。</CardDescription>
          </div>
          <StatusBadge tone="green">报告预览已更新</StatusBadge>
        </CardHeader>
        <div className="flex flex-wrap gap-2 p-5 pt-0">
          <StatusBadge tone="gray"><FileText className="mr-1 h-3.5 w-3.5" />Markdown / HTML / JSON / CSV</StatusBadge>
          <StatusBadge tone="yellow">缺失数据：当前文件未提供</StatusBadge>
          <StatusBadge tone="orange">示例数据不能作为真实结论</StatusBadge>
        </div>
      </Card>
    </div>
  );
}
