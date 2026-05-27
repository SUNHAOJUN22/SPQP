import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <section className={cn("bg-studio-ink border border-studio-line/60 rounded-xl min-w-0 p-5 transition-[colors,box-shadow] duration-150 hover:shadow-elevation-2", className)} {...props} />;
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-4 flex min-w-0 flex-wrap items-start justify-between gap-4", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={cn("min-w-0 text-sm font-medium tracking-normal text-studio-text", className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("mt-1 min-w-0 text-xs leading-6 text-studio-muted", className)} {...props} />;
}
