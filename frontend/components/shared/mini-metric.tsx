"use client";

import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/types/studio";

export function MiniMetric({
  title,
  value,
  unit,
  tone,
}: {
  title: string;
  value: string;
  unit: string;
  tone: StatusTone;
}) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-studio-muted">{title}</p>
          <p className="mt-3 text-3xl font-medium">{value}</p>
          <p className="text-xs text-studio-muted">{unit}</p>
        </div>
        <StatusBadge tone={tone}>
          {tone === "green"
            ? "有利插入"
            : tone === "red"
              ? "Ti 毒化"
              : "需要检查"}
        </StatusBadge>
      </div>
    </Card>
  );
}

export function InteractionLine({
  x1,
  y1,
  x2,
  y2,
  color,
  width,
  label,
}: {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  width: number;
  label: string;
}) {
  return (
    <g>
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        opacity="0.72"
      />
      <text
        x={(x1 + x2) / 2}
        y={(y1 + y2) / 2 - 8}
        textAnchor="middle"
        fill="hsl(var(--studio-text))"
        fontSize="12"
        fontWeight="700"
      >
        {label}
      </text>
    </g>
  );
}
