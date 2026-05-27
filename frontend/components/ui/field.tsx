import * as React from "react";
import { cn } from "@/lib/utils";

export function FieldLabel({ className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={cn("text-xs font-medium text-studio-muted", className)} {...props} />;
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "h-10 w-full min-w-0 rounded-lg border border-studio-line bg-transparent px-4 text-sm text-studio-text placeholder:text-studio-muted/70 transition duration-150 focus:outline-none focus:ring-2 focus:ring-studio-cyan",
        props.className
      )}
    />
  );
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={cn(
        "min-h-32 w-full min-w-0 rounded-lg border border-studio-line bg-transparent px-4 py-3 font-mono text-sm leading-6 text-studio-text placeholder:text-studio-muted/70 transition duration-150 focus:outline-none focus:ring-2 focus:ring-studio-cyan",
        props.className
      )}
    />
  );
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={cn("h-10 w-full min-w-0 rounded-lg border border-studio-line bg-transparent px-4 text-sm text-studio-text transition duration-150 focus:outline-none focus:ring-2 focus:ring-studio-cyan", props.className)}
    />
  );
}
