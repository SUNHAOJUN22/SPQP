import { cn } from "@/lib/utils";
import type { StatusTone } from "@/types/studio";

const toneClasses: Record<StatusTone, string> = {
  green: "border-studio-green/40 bg-studio-green/10 text-studio-green",
  yellow: "border-studio-yellow/40 bg-studio-yellow/10 text-studio-yellow",
  red: "border-studio-red/40 bg-studio-red/10 text-studio-red",
  blue: "border-studio-blue/40 bg-studio-blue/10 text-studio-blue",
  gray: "border-studio-line bg-studio-panel2 text-studio-muted",
  violet: "border-studio-violet/40 bg-studio-violet/10 text-studio-violet",
  orange: "border-studio-orange/40 bg-studio-orange/10 text-studio-orange"
};

export function StatusBadge({ children, tone = "gray", className, pulse }: { children: React.ReactNode; tone?: StatusTone; className?: string; pulse?: boolean }) {
  return (
    <span className={cn("inline-flex h-7 items-center rounded-lg border px-3 text-xs font-medium", toneClasses[tone], pulse && "animate-pulse", className)}>
      {children}
    </span>
  );
}
