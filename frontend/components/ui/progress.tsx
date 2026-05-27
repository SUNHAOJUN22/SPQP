import { cn, clamp } from "@/lib/utils";

export function Progress({ value, className }: { value: number; className?: string }) {
  return (
    <div className={cn("h-1 overflow-hidden rounded-sm bg-studio-panel2", className)}>
      <div
        className="h-full rounded-sm bg-studio-cyan transition-all duration-700 ease-out"
        style={{ width: `${clamp(value, 0, 100)}%` }}
      />
    </div>
  );
}
