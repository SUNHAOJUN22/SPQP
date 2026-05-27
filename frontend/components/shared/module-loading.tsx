"use client";

import { Card } from "@/components/ui/card";

export function ModuleLoading({ label }: { label: string }) {
  return (
    <Card className="stable-panel min-h-[320px]">
      <div className="flex h-full min-h-[260px] flex-col items-center justify-center gap-4 text-center">
        <div className="h-12 w-12 animate-pulse rounded-xl bg-studio-cyan/25" />
        <div>
          <p className="font-medium text-studio-text">正在加载{label}</p>
          <p className="mt-1 text-sm text-studio-muted">
            图表与三维视图按需加载，保持驾驶舱切换流畅。
          </p>
        </div>
      </div>
    </Card>
  );
}
