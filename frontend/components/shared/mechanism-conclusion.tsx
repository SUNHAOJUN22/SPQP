"use client";

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

export function MechanismConclusion({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription>机理解释 / Mechanistic interpretation</CardDescription>
        </div>
        <StatusBadge tone="yellow">需要真实数据验证</StatusBadge>
      </CardHeader>
      <p className="text-base leading-8 text-studio-muted">{text}</p>
    </Card>
  );
}
