import type { StatusTone } from "@/types/studio";

export function toneSurface(tone: StatusTone) {
  return {
    green: "border-studio-green/40 bg-studio-green/10 text-studio-green",
    yellow: "border-studio-yellow/40 bg-studio-yellow/10 text-studio-yellow",
    red: "border-studio-red/40 bg-studio-red/10 text-studio-red",
    blue: "border-studio-blue/40 bg-studio-blue/10 text-studio-blue",
    gray: "border-studio-line bg-studio-panel/70 text-studio-muted",
    violet: "border-studio-violet/40 bg-studio-violet/10 text-studio-violet",
    orange: "border-studio-orange/40 bg-studio-orange/10 text-studio-orange",
  }[tone];
}

export function poisonTone(value: number | null): StatusTone {
  if (value === null) return "gray";
  if (value > 5) return "green";
  if (value >= 0) return "yellow";
  return "red";
}

export function poisonLabel(value: number | null): string {
  if (value === null) return "数据缺失";
  if (value > 5) return "生产性 C=C 插入占优";
  if (value >= 0) return "O→Ti 与 C=C 配位竞争";
  return "Ti 活性中心存在甲氧基毒化风险";
}

export function rateText(value: number | null): string {
  if (value === null) return "待计算";
  if (value === 1) return "1.0";
  if (value < 0.001) return value.toExponential(1);
  return value.toPrecision(2);
}

export const chartColors = [
  "hsl(var(--studio-cyan))",
  "hsl(var(--studio-violet))",
  "hsl(var(--studio-orange))",
  "hsl(var(--studio-green))",
];
