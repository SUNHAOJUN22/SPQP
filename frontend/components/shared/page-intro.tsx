"use client";

import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

export function PageIntro({
  title,
  subtitle,
  note,
}: {
  title: string;
  subtitle: string;
  note?: string;
}) {
  return (
    <Card className="mb-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <StatusBadge tone="gray">{subtitle}</StatusBadge>
          <h2 className="mt-4 text-3xl font-medium tracking-normal md:text-5xl">
            {title}
          </h2>
          {note ? (
            <p className="mt-4 max-w-4xl text-sm leading-7 text-studio-muted">
              {note}
            </p>
          ) : null}
        </div>
        <StatusBadge tone="orange">示例数据，不能作为真实结论</StatusBadge>
      </div>
    </Card>
  );
}
