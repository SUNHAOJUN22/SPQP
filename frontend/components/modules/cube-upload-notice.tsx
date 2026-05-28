"use client";

import { useRef, useState } from "react";
import { FlaskConical, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiUpload } from "@/lib/api-client";

export interface CubeUploadRecord {
  id: number;
  file_name: string;
  cube_type: string;
  atom_count: number | null;
  grid: {
    axes?: Array<{ points: number }>;
    total_points?: number;
  } | null;
  metadata: Record<string, unknown>;
  warning?: string | null;
  provenance: string;
}

export function CubeUploadNotice({ onUploaded }: { onUploaded?: (cube: CubeUploadRecord) => Promise<void> | void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [uploaded, setUploaded] = useState<CubeUploadRecord | null>(null);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const record = await apiUpload<CubeUploadRecord>("/cube/upload", file);
      setUploaded(record);
      await onUploaded?.(record);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "cube 上传失败，请检查文件格式。");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="rounded-expressive border border-studio-line bg-studio-panel-strong p-4 text-sm text-studio-muted">
      未上传真实 cube 文件时仅显示示例等值面。支持 electron density、ESP、HOMO、LUMO、spin density cube 导入；服务器只读解析元数据、下采样标量场和剖切预览，不执行文件。
      <div className="mt-3 flex flex-wrap gap-2">
        <input
          ref={inputRef}
          className="hidden"
          type="file"
          accept=".cube,.cub"
          aria-label="上传 cube 文件"
          onChange={(event) => void handleFile(event.target.files?.[0])}
        />
        <Button
          variant="secondary"
          size="sm"
          icon={<UploadCloud className="h-4 w-4" />}
          disabled={busy}
          onClick={() => inputRef.current?.click()}
        >
          {busy ? "读取 cube 中" : "上传 cube 文件"}
        </Button>
        <StatusBadge tone="blue">仅读取，不执行</StatusBadge>
        <StatusBadge tone="gray">允许 .cube / .cub</StatusBadge>
      </div>
      {uploaded ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 rounded-xl border border-studio-line bg-studio-panel2/70 p-3">
          <FlaskConical className="h-4 w-4 text-studio-cyan" />
          <span className="font-medium text-studio-text">{uploaded.cube_type}</span>
          <span>{uploaded.file_name}</span>
          <StatusBadge tone="green">真实上传</StatusBadge>
          <span>网格点 {uploaded.grid?.total_points ?? "待检查"}</span>
        </div>
      ) : null}
      {error ? <p className="mt-3 rounded-xl border border-studio-red/30 bg-studio-red/10 p-3 text-studio-red">{error}</p> : null}
    </div>
  );
}
