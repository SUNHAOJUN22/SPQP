"use client";

import { Tooltip } from "recharts";

export function ChartTooltip() {
  return (
    <Tooltip
      contentStyle={{
        background: "hsl(var(--studio-panel))",
        border: "1px solid hsl(var(--studio-line))",
        borderRadius: 18,
        color: "hsl(var(--studio-text))",
      }}
      labelStyle={{ color: "hsl(var(--studio-text))" }}
    />
  );
}
