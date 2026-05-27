import { ShieldCheck } from "lucide-react";
import { EvidenceBadge } from "@/components/data/evidence-badge";
import { SourceQualityBadge } from "@/components/data/source-quality-badge";

export function ProvenancePanel({
  title = "证据与数据来源",
  source,
  evidenceLevel = "C",
  quality,
  warnings = [],
  provenance,
  paperReady = "需要补充验证",
}: {
  title?: string;
  source?: string;
  evidenceLevel?: string;
  quality?: string;
  warnings?: string[];
  provenance?: string;
  paperReady?: string;
}) {
  return (
    <aside className="rounded-xl border border-studio-line bg-studio-panel/80 p-4">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-4 w-4 text-studio-green" />
        <p className="text-sm font-medium text-studio-text">{title}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <EvidenceBadge level={evidenceLevel} />
        {quality ? <SourceQualityBadge quality={quality} /> : null}
      </div>
      <dl className="mt-4 space-y-3 text-sm">
        <div>
          <dt className="text-xs font-medium uppercase tracking-[0.14em] text-studio-muted">
            数据来源
          </dt>
          <dd className="mt-1 break-all text-studio-text">
            {source || "当前文件未提供"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-[0.14em] text-studio-muted">
            论文结论边界
          </dt>
          <dd className="mt-1 text-studio-text">{paperReady}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-[0.14em] text-studio-muted">
            provenance
          </dt>
          <dd className="mt-1 leading-6 text-studio-muted">
            {provenance ||
              "示例数据或 C 级文献线索不能作为真实科学结论。"}
          </dd>
        </div>
      </dl>
      {warnings.length ? (
        <div className="mt-4 rounded-xl border border-studio-orange/30 bg-studio-orange/10 p-3">
          <p className="text-xs font-medium text-studio-orange">warnings</p>
          <ul className="mt-2 space-y-1 text-xs leading-5 text-studio-muted">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </aside>
  );
}
