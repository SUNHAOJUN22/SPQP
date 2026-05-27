"use client";
import { useMemo } from "react";
import { ArrowDownToLine, ClipboardList, Copy, Save, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FieldLabel, Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { ProvenancePanel } from "@/components/data/provenance-panel";
import { PageHeader } from "@/components/layout/page-header";
import { GaussianWorkspace } from "@/components/workflows/gaussian-workspace";
import { taskTypes } from "@/lib/studio-data";
import type { StudioMolecule } from "@/types/studio";

function gaussianTemplate(molecule: StudioMolecule, task: string): string {
  const name = molecule.key;
  if (task.includes("TEA")) return `%NProcShared=32\n%Mem=96GB\n%Chk=${name}_TEA_CP.chk\n#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ Counterpoise=2\n   SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm\n\n${name} TEA 助催化剂络合。片段 1 = 单体，片段 2 = TEA。\n\n0 1 0 1 0 1\n{fragment_coordinates}`;
  if (task.includes("插入过渡态")) return `%NProcShared=32\n%Mem=128GB\n%Chk=${name}_insert_TS.chk\n#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512)\n   Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm\n\n${name} 插入过渡态\n\n0 2\n{coordinates}`;
  if (task.includes("IRC")) return `%NProcShared=32\n%Mem=128GB\n%OldChk=${name}_insert_TS.chk\n%Chk=${name}_IRC.chk\n#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512)\n   Geom=Check Guess=Read IRC=(CalcFC,MaxPoints=100,Stepsize=8,Forward,Reverse) NoSymm\n\n${name} 插入过渡态 IRC 本征反应坐标\n\n0 2`;
  if (task.includes("Ti") || task.includes("π")) return `%NProcShared=32\n%Mem=128GB\n%Chk=${name}_${task.includes("毒化") ? "O_Ti_complex" : "pi_complex"}.chk\n#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512)\n   Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm\n\n${name} ${task}\n\n0 2\n{coordinates}`;
  return `%NProcShared=16\n%Mem=48GB\n%Chk=${name}_opt.chk\n#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512)\n   Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm\n\n${name} 孤立单体 opt/freq/NBO\n\n0 1\n{coordinates}`;
}

export function GaussianBuilderPanel({ selected, task, setTask }: { selected: StudioMolecule; task: string; setTask: (t: string) => void }) {
  const generatedInput = useMemo(() => gaussianTemplate(selected, task), [selected, task]);
  const method = task.includes("Ti") || task.includes("过渡态") ? "UPBE1PBE / Def2SVP" : "B3LYP / Def2SVP";
  const multiplicity = task.includes("Ti") || task.includes("过渡态") ? "2" : "1";
  const memory = task.includes("Ti") || task.includes("过渡态") ? "128GB" : "48GB";
  const nproc = task.includes("Ti") || task.includes("过渡态") ? "32" : "16";

  return (
    <div className="space-y-4">
      <PageHeader
        title="Gaussian 输入生成"
        subtitle="采用 Google Colab / Docs 式三栏工作台：左侧任务模板，中间参数表单，右侧输入文件预览。平台只生成文件，不执行 Gaussian。"
        meta={<><StatusBadge tone="green">不执行 Gaussian，仅生成输入文件</StatusBadge><StatusBadge tone="gray">仅读取项目数据</StatusBadge></>}
        actions={<><Button variant="secondary" icon={<Copy className="h-4 w-4" />} onClick={() => navigator.clipboard?.writeText(generatedInput)}>复制模板</Button><Button icon={<ArrowDownToLine className="h-4 w-4" />}>下载 .gjf</Button></>}
      />
      <GaussianWorkspace
        templates={
          <div className="space-y-4">
            <div>
              <p className="text-base font-medium">任务模板</p>
              <p className="mt-1 text-sm leading-6 text-studio-muted">按研究问题选择模板；高风险任务会自动切换到开壳层 Ti 片段设置。</p>
            </div>
            <div className="space-y-2">
              {taskTypes.map((item) => (
                <button
                  key={item}
                  onClick={() => setTask(item)}
                  className={`focus-ring w-full rounded-xl border px-3 py-2 text-left text-sm transition ${task === item ? "border-studio-cyan bg-studio-cyan/10 text-studio-text" : "border-studio-line bg-studio-panel2/60 text-studio-muted hover:bg-studio-panel2"}`}
                >
                  <span className="font-medium">{item}</span>
                </button>
              ))}
            </div>
          </div>
        }
        editor={
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-base font-medium">参数表单</p>
                <p className="mt-1 text-sm leading-6 text-studio-muted">所有默认参数均为可编辑草稿，真实计算需用户自行审查坐标、电荷、自旋与模型边界。</p>
              </div>
              <StatusBadge tone="blue"><ClipboardList className="mr-1 h-3.5 w-3.5" />{selected.key}</StatusBadge>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div><FieldLabel>研究对象</FieldLabel><Input className="mt-2" readOnly value={selected.key} /></div>
              <div><FieldLabel>计算任务</FieldLabel><Select className="mt-2" value={task} onChange={(event) => setTask(event.target.value)}>{taskTypes.map((item) => <option key={item}>{item}</option>)}</Select></div>
              <div><FieldLabel>方法 / 基组</FieldLabel><Input className="mt-2" readOnly value={method} /></div>
              <div><FieldLabel>电荷 / 自旋多重度</FieldLabel><Input className="mt-2" readOnly value={`0 / ${multiplicity}`} /></div>
              <div><FieldLabel>内存</FieldLabel><Input className="mt-2" readOnly value={memory} /></div>
              <div><FieldLabel>并行核数</FieldLabel><Input className="mt-2" readOnly value={nproc} /></div>
            </div>
            <div className="rounded-xl border border-studio-line bg-studio-panel2/60 p-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-studio-green" />
                <p className="text-sm font-medium">安全边界</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-studio-muted">
                当前页面不会调用 Gaussian、cubegen、Multiwfn 或任意 shell；Gaussian 路径必须在系统设置中显式配置并二次确认后才可用于未来任务队列。
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" icon={<Save className="h-4 w-4" />}>保存到项目</Button>
              <Button variant="secondary" icon={<Copy className="h-4 w-4" />} onClick={() => navigator.clipboard?.writeText(generatedInput)}>复制模板</Button>
              <Button icon={<ArrowDownToLine className="h-4 w-4" />}>生成输入文件</Button>
            </div>
          </div>
        }
        preview={
          <div className="space-y-4">
            <div>
              <p className="text-base font-medium">输入文件预览</p>
              <p className="mt-1 text-sm leading-6 text-studio-muted">生成内容以 Gaussian16 草稿格式展示；坐标占位符不会被伪造。</p>
            </div>
            <div className="overflow-hidden rounded-xl border border-studio-line bg-studio-ink text-studio-text">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-studio-line/40 px-4 py-3">
                <span className="max-w-full truncate font-mono text-xs text-studio-muted">{selected.key}_{task}.gjf</span>
                <StatusBadge tone="gray" className="h-7 px-2">draft</StatusBadge>
              </div>
              <pre className="max-h-[560px] max-w-full overflow-auto p-5 font-mono text-sm leading-6">{generatedInput}</pre>
            </div>
          </div>
        }
        details={
          <div className="mt-4">
            <ProvenancePanel
              source={`${selected.key} / ${selected.source}`}
              evidenceLevel="D"
              quality="template"
              provenance="Gaussian 输入生成器只生成模板；没有真实输出文件时，不产生 A/B 级科学结论。"
              paperReady="否，输入模板不是计算结果"
              warnings={["坐标占位符 {coordinates} 必须由用户提供真实结构或构象生成结果。"]}
            />
          </div>
        }
      />
    </div>
  );
}
