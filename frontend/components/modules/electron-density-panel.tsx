"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Eye, Layers3, ScanLine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { CubeUploadNotice, type CubeUploadRecord } from "@/components/modules/cube-upload-notice";
import { PageIntro } from "@/components/shared/page-intro";
import { apiGet } from "@/lib/api-client";
import { cn } from "@/lib/utils";

type CubeVolumePreview = {
  cube_id: number;
  cube_type: string;
  grid_dimensions: { x: number; y: number; z: number };
  expected_value_count: number;
  observed_value_count: number;
  sample_count: number;
  phase_counts: { positive: number; negative: number; zero: number };
  samples: Array<{ x: number; y: number; z: number; value: number }>;
  warning: string;
  provenance: string;
};

type CubeSlicePreview = {
  cube_id: number;
  axis: string;
  plane_index: number;
  shape: { width: number; height: number };
  values: Array<Array<number | null>>;
  min: number | null;
  max: number | null;
  warning: string;
  provenance: string;
};

export function OrbitalCanvas({ mode, title, preview }: { mode: "density" | "homo" | "lumo" | "esp"; title: string; preview?: CubeVolumePreview | null }) {
  const colors = mode === "lumo" ? ["bg-studio-blue", "bg-studio-orange"] : mode === "homo" ? ["bg-studio-violet", "bg-studio-green"] : ["bg-studio-cyan", "bg-studio-red"];
  const sampleCloud = preview?.samples.slice(0, 120) ?? [];
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{preview ? "真实 cube" : "示例等值面"}</CardDescription>
        </div>
      </CardHeader>
      <div className="relative h-80 overflow-hidden rounded-b-xl border-t border-studio-line bg-studio-ink">
        {preview ? (
          <div className="absolute inset-0">
            {sampleCloud.map((point, index) => {
              const x = ((point.x + 10) / 20) * 100;
              const y = ((point.y + 10) / 20) * 100;
              const size = Math.max(2, (Math.abs(point.value) / 0.1) * 12);
              const tone = point.value >= 0 ? "rgba(53,208,186,0.75)" : "rgba(255,107,107,0.75)";
              return (
                <span
                  key={`${point.x}-${point.y}-${point.z}-${index}`}
                  className="absolute rounded-full blur-[1px]"
                  style={{ left: `${x}%`, top: `${y}%`, width: size, height: size, background: tone }}
                />
              );
            })}
          </div>
        ) : (
          <>
            <motion.div className={cn("absolute left-[23%] top-[28%] h-48 w-64 rounded-full opacity-50 blur-2xl", colors[0])} animate={{ scale: [1, 1.12, 1], rotate: [0, 8, 0] }} transition={{ duration: 5, repeat: Infinity }} />
            <motion.div className={cn("absolute right-[18%] top-[38%] h-44 w-56 rounded-full opacity-45 blur-2xl", colors[1])} animate={{ scale: [1.1, 0.95, 1.1], rotate: [0, -10, 0] }} transition={{ duration: 5.4, repeat: Infinity }} />
          </>
        )}
        <div className="absolute left-1/2 top-1/2 grid h-20 w-20 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full bg-studio-violet text-white shadow-elevation-2">Si</div>
        <div className="absolute left-[61%] top-[37%] grid h-14 w-14 place-items-center rounded-full bg-studio-red text-white shadow-elevation-2">O</div>
        <div className="absolute bottom-4 left-4 right-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-studio-line/20 bg-studio-ink/60 p-4">
          <span className="text-sm text-studio-muted">色标：青色 = 正值 / 电子聚集，红色 = 负值 / 电子耗散或负相位</span>
          <StatusBadge tone={preview ? "green" : "gray"}>{preview ? "真实 cube" : "示意图"}</StatusBadge>
        </div>
      </div>
    </Card>
  );
}

export function ElectronDensityPanel() {
  const [cube, setCube] = useState<CubeUploadRecord | null>(null);
  const [preview, setPreview] = useState<CubeVolumePreview | null>(null);
  const [slice, setSlice] = useState<CubeSlicePreview | null>(null);
  const [axis, setAxis] = useState("z");
  const [error, setError] = useState("");

  async function loadCube(record: CubeUploadRecord) {
    if (!record.id) return;
    setCube(record);
    setError("");
    try {
      const [volume, sliced] = await Promise.all([
        apiGet<CubeVolumePreview>(`/cubes/${record.id}/isosurface`),
        apiGet<CubeSlicePreview>(`/cubes/${record.id}/slice?axis=${axis}`)
      ]);
      setPreview(volume);
      setSlice(sliced);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "cube 预览读取失败。");
    }
  }

  async function changeAxis(nextAxis: string) {
    setAxis(nextAxis);
    if (!cube?.id) return;
    try {
      setSlice(await apiGet<CubeSlicePreview>(`/cubes/${cube.id}/slice?axis=${nextAxis}`));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "cube 剖切读取失败。");
    }
  }

  return (
    <div className="space-y-4">
      <PageIntro
        title="电子云密度 ρ(r)、静电势 ESP 与差分电子密度 Δρ"
        subtitle="Electron Density / ESP / Difference Density"
        note="电子云密度 ρ(r) 描述电子在空间中的分布概率密度。差分电子密度 Δρ = ρ_complex − ρ_fragments 可用于观察络合前后电子转移方向。"
      />
      <CubeUploadNotice onUploaded={loadCube} />
      {error ? <div className="rounded-xl border border-studio-red/30 bg-studio-red/10 p-4 text-sm text-studio-red">{error}</div> : null}
      <div className="grid gap-4 xl:grid-cols-[1fr_410px]">
        <OrbitalCanvas mode="density" title="透明电子云与 cube 下采样预览" preview={preview} />
        <CubeControls cube={cube} preview={preview} slice={slice} axis={axis} onAxis={changeAxis} />
      </div>
      <div className="grid gap-4 md:grid-cols-4">{["总电子密度 ρ(r)", "自旋密度", "静电势 ESP", "差分电子密度 Δρ"].map((title) => <DensityModeCard key={title} title={title} active={Boolean(preview)} />)}</div>
    </div>
  );
}

export function ESPPanel() {
  return (
    <DensityDerivedPanel
      title="ESP 静电势"
      subtitle="Electrostatic Potential"
      formula="V(r) = Σ_A Z_A / |r − R_A| − ∫ρ(r′)/|r − r′|dr′"
      note="ESP 可用于识别 OMe 氧周围的负静电势区域、Al←O 捕获倾向和潜在 Ti 毒化位点。未上传 ESP cube 时只显示方法说明。"
      mode="esp"
    />
  );
}

export function FukuiPanel() {
  return (
    <DensityDerivedPanel
      title="Fukui 局部反应性"
      subtitle="Fukui Local Reactivity"
      formula="f+(r) ≈ ρN+1(r) − ρN(r),  f−(r) ≈ ρN(r) − ρN−1(r)"
      note="Fukui 函数用于定位亲核/亲电反应敏感区域。当前只提供 cube 工作流占位；真实 f+/f− 需要 N、N+1、N−1 态的可比电子密度。"
      mode="density"
    />
  );
}

export function DifferenceDensityPanel() {
  return (
    <DensityDerivedPanel
      title="差分电子密度"
      subtitle="Difference Electron Density"
      formula="Δρ(r) = ρ_complex(r) − ρ_fragments(r)"
      note="差分电子密度可用于观察 TEA 络合或 O→Ti 配位前后的电子转移方向。两个 cube 必须同网格、同取向、同相位定义。"
      mode="density"
    />
  );
}

function DensityDerivedPanel({ title, subtitle, formula, note, mode }: { title: string; subtitle: string; formula: string; note: string; mode: "density" | "esp" }) {
  const [preview, setPreview] = useState<CubeVolumePreview | null>(null);
  return (
    <div className="space-y-4">
      <PageIntro title={title} subtitle={subtitle} note={note} />
      <CubeUploadNotice onUploaded={async (record) => record.id ? setPreview(await apiGet<CubeVolumePreview>(`/cubes/${record.id}/isosurface`)) : undefined} />
      <Card className="p-5">
        <p className="rounded-xl border border-studio-line bg-studio-panel2/70 p-4 font-mono text-sm text-studio-muted">{formula}</p>
      </Card>
      <OrbitalCanvas mode={mode} title={`${title} cube 预览`} preview={preview} />
    </div>
  );
}

function CubeControls({ cube, preview, slice, axis, onAxis }: { cube: CubeUploadRecord | null; preview: CubeVolumePreview | null; slice: CubeSlicePreview | null; axis: string; onAxis: (axis: string) => Promise<void> }) {
  const completeness = preview ? Math.min(100, (preview.observed_value_count / Math.max(1, preview.expected_value_count)) * 100) : 0;
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>cube 数据面板</CardTitle>
          <CardDescription>{preview ? "真实 cube 数据面板" : "当前只有 Gaussian log 或示例图，无法显示真实电子云。"}</CardDescription>
        </div>
        <StatusBadge tone={preview ? "green" : "gray"}>{preview ? "已读取标量场" : "未上传 cube"}</StatusBadge>
      </CardHeader>
      <div className="space-y-4">
        <div>
          <div className="mb-2 flex justify-between text-sm text-studio-muted"><span>标量场完整度</span><b>{completeness.toFixed(1)}%</b></div>
          <Progress value={completeness} />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <Metric label="网格点" value={preview?.expected_value_count} />
          <Metric label="采样点" value={preview?.sample_count} />
          <Metric label="正值点" value={preview?.phase_counts.positive} />
          <Metric label="负值点" value={preview?.phase_counts.negative} />
        </div>
        <div className="grid grid-cols-3 gap-2">
          {["x", "y", "z"].map((item) => (
            <Button key={item} variant={axis === item ? "primary" : "secondary"} size="sm" onClick={() => void onAxis(item)}>
              {item.toUpperCase()} 剖切面
            </Button>
          ))}
        </div>
        <SliceHeatmap slice={slice} />
        <div className="rounded-xl border border-studio-orange/30 bg-studio-orange/10 p-3 text-xs leading-5 text-studio-orange">
          {preview?.warning ?? "未上传真实 cube 文件，当前仅显示示例等值面。请上传 cube/fchk 或使用 cubegen 生成后再导入。"}
        </div>
      </div>
    </Card>
  );
}

function SliceHeatmap({ slice }: { slice: CubeSlicePreview | null }) {
  const values = slice?.values ?? [];
  const flattened = values.flat().filter((value): value is number => value !== null);
  const maxAbs = Math.max(1e-12, ...flattened.map((value) => Math.abs(value)));
  return (
    <div>
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-studio-muted"><ScanLine className="h-4 w-4" /> 剖切预览 {slice ? `${slice.axis.toUpperCase()}=${slice.plane_index}` : "待上传"}</div>
      <div className="grid max-h-64 gap-0.5 overflow-auto rounded-xl border border-studio-line bg-studio-ink p-2" style={{ gridTemplateColumns: `repeat(${Math.max(1, slice?.shape.width ?? 8)}, minmax(8px, 1fr))` }}>
        {(values.length ? values : Array.from({ length: 64 }, () => [null])).flat().map((value, index) => {
          const alpha = value === null ? 0.08 : Math.min(0.95, Math.abs(value) / maxAbs);
          const color = value === null ? "rgba(148,163,184,0.12)" : value >= 0 ? `rgba(53,208,186,${alpha})` : `rgba(255,107,107,${alpha})`;
          return <span key={index} className="aspect-square min-h-2 rounded-xl" style={{ background: color }} title={value === null ? "数据缺失" : value.toExponential(3)} />;
        })}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number | string | undefined }) {
  return <div className="rounded-xl border border-studio-line bg-studio-panel2/70 p-3"><p className="text-xs text-studio-muted">{label}</p><p className="mt-1 font-medium text-studio-text">{value ?? "数据缺失"}</p></div>;
}

function DensityModeCard({ title, active }: { title: string; active: boolean }) {
  return (<Card className="p-4"><div className="h-24 rounded-xl bg-studio-panel-strong" /><p className="mt-3 font-medium">{title}</p><p className="mt-2 text-xs leading-5 text-studio-muted">{active ? "已接入真实 cube" : "未上传真实 cube 时仅显示示例，不生成真实科学结论"}</p></Card>);
}
