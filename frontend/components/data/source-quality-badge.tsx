import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/types/studio";

const qualityTone: Record<string, StatusTone> = {
  readable: "green",
  "encoded-garbled": "orange",
  "scanned-needs-ocr": "yellow",
  failed: "red",
  missing: "gray",
};

const qualityLabel: Record<string, string> = {
  readable: "可读文本",
  "encoded-garbled": "编码异常",
  "scanned-needs-ocr": "需 OCR",
  failed: "解析失败",
  missing: "未导入",
};

export function SourceQualityBadge({ quality = "missing" }: { quality?: string }) {
  return (
    <StatusBadge tone={qualityTone[quality] ?? "gray"}>
      解析质量：{qualityLabel[quality] ?? quality}
    </StatusBadge>
  );
}
