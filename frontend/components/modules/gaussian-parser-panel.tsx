"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { FileJson, Play, Save, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { ProvenancePanel } from "@/components/data/provenance-panel";

type PreviewResult = {
  file: string;
  normal_termination: boolean | null;
  scf_hartree: number | null;
  gibbs_hartree: number | null;
  n_imag: number | null;
  lowest_freq_cm_1: number | null;
  homo_hartree: number | null;
  lumo_hartree: number | null;
  gap_ev: number | null;
  counterpoise_corrected_energy_hartree: number | null;
  npa_detected: boolean;
  wiberg_detected: boolean;
  nbo_e2_detected: boolean;
  quality: "待计算" | "complete" | "partial" | "failed";
  chinese_warnings: string[];
  provenance: string;
};

const emptyPreview: PreviewResult = {
  file: "本地预览.log",
  normal_termination: null,
  scf_hartree: null,
  gibbs_hartree: null,
  n_imag: null,
  lowest_freq_cm_1: null,
  homo_hartree: null,
  lumo_hartree: null,
  gap_ev: null,
  counterpoise_corrected_energy_hartree: null,
  npa_detected: false,
  wiberg_detected: false,
  nbo_e2_detected: false,
  quality: "待计算",
  chinese_warnings: ["请粘贴 Gaussian 输出文本，或上传 .log / .out 文件。"],
  provenance: "等待输入。"
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export function GaussianParserPanel({ parserText, setParserText }: { parserText: string; setParserText: (value: string) => void }) {
  const workerRef = useRef<Worker | null>(null);
  const [preview, setPreview] = useState<PreviewResult>(emptyPreview);
  const [serverResult, setServerResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const hasText = parserText.trim().length > 0;

  useEffect(() => {
    if (typeof window === "undefined") return;
    const worker = new Worker("/gaussian-preview-worker.js");
    workerRef.current = worker;
    worker.onmessage = (event: MessageEvent<PreviewResult>) => {
      startTransition(() => setPreview(event.data));
    };
    return () => {
      worker.terminate();
      workerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (!hasText) {
        setPreview(emptyPreview);
        return;
      }
      workerRef.current?.postMessage({ text: parserText, fileName: "本地预览.log" });
    }, 140);
    return () => window.clearTimeout(timer);
  }, [hasText, parserText]);

  async function parseWithBackend() {
    if (!hasText) {
      setError("当前没有可解析的 Gaussian 文本。");
      return;
    }
    setError(null);
    setServerResult(null);
    try {
      const response = await fetch(`${apiBase}/parse/gaussian-log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_name: "frontend-paste.log", text: parserText })
      });
      if (!response.ok) {
        throw new Error(`后端解析失败：HTTP ${response.status}`);
      }
      setServerResult(await response.json());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "后端解析失败。");
    }
  }

  async function readLocalFile(file: File | undefined) {
    if (!file) return;
    if (!/\.(log|out)$/i.test(file.name)) {
      setError("该接口仅接受 .log 和 .out 文件。");
      return;
    }
    setError(null);
    setParserText(await file.text());
  }

  const normalized = serverResult ?? preview;
  return (
    <div className="space-y-4">
      <PageHeader
        title="Gaussian 输出解析"
        subtitle="Google Cloud Log Viewer 风格：左侧日志文本，中间 normalized JSON，右侧解析质量与数据来源。仅读取，不执行 Gaussian。"
        meta={<StatusBadge tone="green">仅读取，不执行 Gaussian</StatusBadge>}
      />
      <div className="grid min-w-0 gap-4 xl:grid-cols-[minmax(340px,0.9fr)_minmax(0,1fr)_340px]">
        <Card className="min-w-0">
        <CardHeader>
          <div>
            <CardTitle>Gaussian 输出解析</CardTitle>
            <CardDescription>本地预览运行在 Web Worker 中；正式解析调用后端只读 API，仅读取，不执行 Gaussian。</CardDescription>
          </div>
          <StatusBadge tone="green">只读解析</StatusBadge>
        </CardHeader>
        <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-studio-line bg-studio-panel/60 p-8 text-center transition hover:border-studio-cyan/60">
          <UploadCloud className="h-10 w-10 text-studio-cyan" />
          <span className="mt-3 text-sm font-medium">上传 Gaussian 输出</span>
          <span className="mt-1 text-xs text-studio-muted">允许 .log / .out；cube 文件用于电子云模块。</span>
          <input type="file" className="hidden" accept=".log,.out" onChange={(event) => void readLocalFile(event.target.files?.[0])} />
        </label>
        <Textarea className="mt-4 min-h-[330px]" value={parserText} onChange={(event) => setParserText(event.target.value)} placeholder="粘贴 Gaussian 输出文本进行本地 Worker 预览" />
        <div className="mt-4 flex flex-wrap gap-2">
          <Button icon={<Play className="h-4 w-4" />} onClick={() => void parseWithBackend()} disabled={!hasText}>
            解析文件
          </Button>
          <Button variant="secondary" icon={<Save className="h-4 w-4" />}>
            保存到项目
          </Button>
          <Button variant="ghost" icon={<FileJson className="h-4 w-4" />} disabled>
            Worker 预览
          </Button>
        </div>
        {error ? <p className="mt-3 rounded-xl border border-studio-red/30 bg-studio-red/10 px-4 py-3 text-sm text-studio-red">{error}</p> : null}
        </Card>
        <Card className="min-w-0">
        <CardHeader>
          <div>
            <CardTitle>解析质量与 normalized JSON</CardTitle>
            <CardDescription>字段包含单位；缺失数据明确标记为 null。Worker 预览不替代后端正式解析。</CardDescription>
          </div>
          <StatusBadge tone={preview.quality === "complete" ? "green" : hasText ? "yellow" : "gray"}>
            {isPending ? "后台预览中" : hasText ? "需要检查" : "待计算"}
          </StatusBadge>
        </CardHeader>
        <div className="mb-3 flex flex-wrap gap-2">
          {preview.chinese_warnings.map((warning) => (
            <StatusBadge key={warning} tone={warning.includes("未检测") || warning.includes("未找到") ? "yellow" : "gray"}>
              {warning}
            </StatusBadge>
          ))}
        </div>
        <pre className="min-w-0 max-w-full max-h-[620px] overflow-auto rounded-xl border border-studio-line bg-studio-ink p-5 font-mono text-sm leading-6 text-studio-text">
          {JSON.stringify(normalized, null, 2)}
        </pre>
        </Card>
        <ProvenancePanel
          title="解析质量"
          source={preview.file}
          evidenceLevel="A"
          quality={preview.quality === "complete" ? "readable" : preview.quality === "failed" ? "failed" : "missing"}
          warnings={preview.chinese_warnings}
          provenance={preview.provenance}
          paperReady={preview.quality === "complete" ? "可作为上传文件解析结果；仍需检查方法、基组、频率和 provenance。" : "当前数据不足，不能形成可靠结论。"}
        />
      </div>
      {/* 快速解析提示 */}
      <div className="col-span-full grid gap-3 md:grid-cols-3 xl:col-span-2">
        {[
          { title: "能量值", desc: "SCF, Gibbs, Enthalpy, ZPE", icon: "⚡" },
          { title: "频率分析", desc: "虚频检测, 最低频率, IR 强度", icon: "📊" },
          { title: "NBO 分析", desc: "二阶微扰 E(2), 给体-受体对", icon: "🔬" },
          { title: "电荷分析", desc: "Mulliken, NPA, ESP 电荷", icon: "🔋" },
          { title: "几何参数", desc: "键长, 键角, 二面角", icon: "📐" },
          { title: "轨道能级", desc: "HOMO, LUMO, 带隙 (eV)", icon: "🌈" },
        ].map((item) => (
          <div key={item.title} className="rounded-xl border border-studio-line bg-studio-panel/70 p-4">
            <div className="flex items-center gap-2">
              <span className="text-lg">{item.icon}</span>
              <p className="font-medium text-sm">{item.title}</p>
            </div>
            <p className="mt-2 text-xs text-studio-muted">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
