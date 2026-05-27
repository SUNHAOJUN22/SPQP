"use client";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { Download, Filter, Rotate3D, Save, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FieldLabel, Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { ResourceTable, type ResourceColumn } from "@/components/data/resource-table";
import { PageHeader } from "@/components/layout/page-header";
import { MoleculeResourceView } from "@/components/workflows/molecule-resource-view";
import { moleculeLibrary, statusChinese } from "@/lib/studio-data";
import type { StudioMolecule } from "@/types/studio";
const MoleculeViewer = dynamic(() => import("@/components/molecule-viewer").then((m) => m.MoleculeViewer), { ssr: false });

export function MoleculeLibraryPanel({ selected, onSelect }: { selected: StudioMolecule; onSelect: (key: string) => void }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return moleculeLibrary;
    return moleculeLibrary.filter((mol) =>
      [mol.key, mol.name, mol.smiles, mol.family, mol.chainLength, mol.role, ...(mol.functionalSites ?? [])]
        .filter(Boolean)
        .some((item) => String(item).toLowerCase().includes(keyword))
    );
  }, [query]);

  const columns: ResourceColumn<StudioMolecule>[] = [
    {
      key: "name",
      header: "分子资源",
      render: (mol) => (
        <div>
          <p className="font-medium text-studio-text">{mol.key}</p>
          <p className="mt-1 max-w-[260px] truncate font-mono text-xs text-studio-muted">{mol.smiles}</p>
        </div>
      ),
    },
    {
      key: "family",
      header: "家族 / 链长",
      render: (mol) => (
        <div className="space-y-1">
          <p className="text-sm text-studio-text">{mol.family ?? "未归类"}</p>
          <p className="text-xs text-studio-muted">{mol.chainLength ?? "链长待标注"}</p>
        </div>
      ),
    },
    {
      key: "sites",
      header: "功能位点",
      render: (mol) => (
        <div className="flex max-w-[260px] flex-wrap gap-1.5">
          {(mol.functionalSites ?? ["C=C"]).slice(0, 3).map((site) => (
            <StatusBadge key={site} tone={site.includes("O") ? "violet" : site.includes("Cl") ? "green" : site.includes("Al") ? "blue" : "gray"} className="h-7 px-2">
              {site}
            </StatusBadge>
          ))}
        </div>
      ),
    },
    {
      key: "evidence",
      header: "证据 / 状态",
      render: (mol) => (
        <div className="flex flex-wrap gap-2">
          <EvidenceBadge level={mol.source.includes("MOCK") ? "D" : mol.source.includes("论文") ? "C" : "B"} compact />
          <StatusBadge tone={mol.source.includes("MOCK") ? "gray" : "blue"} className="h-7 px-2">
            {mol.source.includes("MOCK") ? "示例数据" : "真实数据"}
          </StatusBadge>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title="分子结构与资源库"
        subtitle="像 Google Drive 管理科研资源一样管理单体、助催化剂、过氧化物与模型片段；示例结构只用于工作流演示，不能替代真实优化构型。"
        meta={<><StatusBadge tone="blue">资源驱动</StatusBadge><StatusBadge tone="gray">示例数据需显式标注</StatusBadge></>}
        actions={<><Button variant="secondary" icon={<Filter className="h-4 w-4" />}>筛选</Button><Button icon={<Save className="h-4 w-4" />}>导入分子</Button></>}
      />
      <MoleculeResourceView
        list={
          <div className="space-y-4">
            <div>
              <p className="text-base font-medium">分子资源表</p>
              <p className="mt-1 text-sm leading-6 text-studio-muted">支持搜索、筛选、行点击打开右侧分子详情。</p>
            </div>
            <div className="flex gap-2">
              <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索分子 / SMILES / 功能位点" />
              <Button variant="secondary" size="icon" icon={<Search className="h-4 w-4" />} aria-label="搜索" />
            </div>
            <ResourceTable
              rows={filtered}
              columns={columns}
              getRowKey={(mol) => mol.key}
              selectedKey={selected.key}
              onSelect={(mol) => onSelect(mol.key)}
            />
            <div className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <FieldLabel>导入 SMILES</FieldLabel>
              <Input className="mt-2" placeholder="C=CCCCC[Si](C)(OC)Cl" />
              <Button className="mt-3 w-full" variant="secondary" icon={<Save className="h-4 w-4" />}>保存为项目分子</Button>
            </div>
          </div>
        }
        viewer={
          <div className="space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-base font-medium">结构视图</p>
                <p className="mt-1 text-sm leading-6 text-studio-muted">2D 功能位点与 3D 模型联动展示；真实构象需由 RDKit/Gaussian 文件提供。</p>
              </div>
              <StatusBadge tone="gray">{statusChinese.example}</StatusBadge>
            </div>
            <Structure2D molecule={selected} />
            <MoleculeViewer molecule={selected} highlight={selected.descriptors.oCount > 0 ? "Si–O / OMe 高亮" : "Si–Cl 基准结构"} />
          </div>
        }
        details={
          <div className="space-y-4">
            <div>
              <p className="text-base font-medium">分子详情</p>
              <p className="mt-1 text-sm text-studio-muted">{selected.name}</p>
              <p className="mt-2 break-all font-mono text-xs text-studio-muted">{selected.smiles}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <EvidenceBadge level={selected.source.includes("MOCK") ? "D" : selected.source.includes("论文") ? "C" : "B"} />
                <StatusBadge tone={selected.stericLevel === "高" ? "red" : selected.stericLevel === "中" ? "yellow" : "green"}>位阻：{selected.stericLevel ?? "待评估"}</StatusBadge>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[["分子量", selected.descriptors.molecularWeight ?? "待计算"],["原子总数", selected.descriptors.atomCount],["重原子", selected.descriptors.heavyAtomCount],["可旋转键", selected.descriptors.rotatableBonds],["vdW 体积", `${selected.descriptors.vdwVolume} Å³`],["Si 半径", `${selected.descriptors.siRadius} Å`],["O 原子数", selected.descriptors.oCount],["Cl 原子数", selected.descriptors.clCount]].map(([label, value]) => (
                <div key={String(label)} className="rounded-xl border border-studio-line bg-studio-panel2/60 p-3">
                  <p className="text-xs text-studio-muted">{label}</p>
                  <p className="mt-1 text-lg font-medium">{value}</p>
                </div>
              ))}
            </div>
            <div className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <p className="font-medium">功能位点</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(selected.functionalSites ?? ["C=C"]).map((site) => (
                  <StatusBadge key={site} tone={site.includes("O") ? "violet" : site.includes("Cl") ? "green" : site.includes("Al") ? "blue" : "gray"}>
                    {site}
                  </StatusBadge>
                ))}
              </div>
              <p className="mt-3 text-sm leading-6 text-studio-muted">{selected.electronicEffect ?? "当前文件未提供电子效应说明。"}</p>
            </div>
            <div className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <p className="font-medium">论文关联结论</p>
              <p className="mt-2 text-sm leading-6 text-studio-muted">{selected.thesisConclusion ?? "当前分子未绑定论文结论。示例数据不能作为真实科学结论。"}</p>
            </div>
            <ProvenancePanel
              source={selected.source}
              evidenceLevel={selected.source.includes("MOCK") ? "D" : selected.source.includes("论文") ? "C" : "B"}
              quality={selected.source.includes("MOCK") ? "example" : "readable"}
              provenance="分子库资源保留 source 与证据等级；示例结构不能作为真实 Gaussian 优化结果。"
              paperReady={selected.source.includes("MOCK") ? "否，示例数据不能作为论文结论" : "需要补充验证"}
            />
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" icon={<Rotate3D className="h-4 w-4" />}>生成构象</Button>
              <Button variant="secondary" icon={<Download className="h-4 w-4" />}>导出数据</Button>
            </div>
          </div>
        }
      />
    </div>
  );
}

function Structure2D({ molecule }: { molecule: StudioMolecule }) {
  return (
    <div className="space-y-3">
      <div>
        <p className="font-medium">2D 分子结构图</p>
        <p className="mt-1 text-sm text-studio-muted">Si 紫色，O 红色，Cl 绿色，C=C 蓝色，Al 青色，Ti 橙色。</p>
      </div>
      <div className="relative h-64 overflow-hidden rounded-xl border border-studio-line bg-studio-panel molecule-grid">
        <svg viewBox="0 0 620 240" className="h-full w-full">
          <line x1="70" y1="120" x2="150" y2="90" stroke="hsl(var(--studio-blue))" strokeWidth="5" /><line x1="70" y1="132" x2="150" y2="102" stroke="hsl(var(--studio-blue))" strokeWidth="3" />
          <line x1="150" y1="96" x2="230" y2="120" stroke="hsl(var(--studio-line))" strokeWidth="4" /><line x1="230" y1="120" x2="310" y2="92" stroke="hsl(var(--studio-line))" strokeWidth="4" />
          <line x1="310" y1="92" x2="390" y2="118" stroke="hsl(var(--studio-line))" strokeWidth="4" /><line x1="390" y1="118" x2="470" y2="118" stroke="hsl(var(--studio-line))" strokeWidth="4" />
          <circle cx="470" cy="118" r="24" fill="hsl(var(--studio-violet))" /><text x="470" y="124" textAnchor="middle" fill="white" fontWeight="700">Si</text>
          {molecule.descriptors.oCount > 0 ? (<><line x1="490" y1="104" x2="548" y2="70" stroke="hsl(var(--studio-line))" strokeWidth="4" /><circle cx="560" cy="62" r="20" fill="hsl(var(--studio-red))" /><text x="560" y="68" textAnchor="middle" fill="white" fontWeight="700">O</text></>) : null}
          {molecule.descriptors.clCount > 0 ? (<><line x1="488" y1="134" x2="550" y2="172" stroke="hsl(var(--studio-line))" strokeWidth="4" /><circle cx="565" cy="182" r="20" fill="hsl(var(--studio-green))" /><text x="565" y="188" textAnchor="middle" fill="white" fontWeight="700">Cl</text></>) : null}
          {["C","C","C","C","C"].map((a, i) => (<g key={i}><circle cx={70+i*80} cy={i%2?96:120} r="16" fill="hsl(var(--studio-panel-2))" stroke="hsl(var(--studio-line))" /><text x={70+i*80} y={(i%2?96:120)+5} textAnchor="middle" fill="hsl(var(--studio-text))" fontSize="12">{a}</text></g>))}
        </svg>
      </div>
    </div>
  );
}
