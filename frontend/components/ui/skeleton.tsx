import { cn } from "@/lib/utils";

export function Skeleton({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-studio-panel2",
        className
      )}
      style={style}
    />
  );
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-studio-ink border border-studio-line/60 rounded-xl p-6 space-y-4",
        className
      )}
    >
      <Skeleton className="h-5 w-40" />
      <Skeleton className="h-3 w-64" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

export function SkeletonChart({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-studio-ink border border-studio-line/60 rounded-xl p-6 space-y-4",
        className
      )}
    >
      <div className="flex justify-between">
        <Skeleton className="h-5 w-36" />
        <Skeleton className="h-5 w-20 rounded-lg" />
      </div>
      <div className="flex items-end gap-2 h-56 pt-4">
        <Skeleton className="h-3/4 flex-1 rounded-lg" />
        <Skeleton className="h-1/2 flex-1 rounded-lg" />
        <Skeleton className="h-5/6 flex-1 rounded-lg" />
        <Skeleton className="h-2/5 flex-1 rounded-lg" />
        <Skeleton className="h-3/5 flex-1 rounded-lg" />
        <Skeleton className="h-4/5 flex-1 rounded-lg" />
      </div>
    </div>
  );
}

export function SkeletonTable({
  rows = 5,
  className,
}: {
  rows?: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-studio-ink border border-studio-line/60 rounded-xl p-6 space-y-3",
        className
      )}
    >
      <div className="flex gap-4 mb-4">
        {[80, 120, 100, 90, 60].map((w, i) => (
          <Skeleton key={i} className="h-4 rounded" style={{ width: w }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {[80, 120, 100, 90, 60].map((w, j) => (
            <Skeleton
              key={j}
              className="h-10 rounded-lg"
              style={{ width: w }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonText({
  lines = 3,
  className,
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className="h-3 rounded"
          style={{ width: `${85 - i * 10}%` }}
        />
      ))}
    </div>
  );
}
