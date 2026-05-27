import { FileIcon } from "lucide-react";

export function EmptyState({ message }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-studio-muted">
      <FileIcon className="h-8 w-8 mb-2 opacity-50" />
      <p className="text-sm">{message || "No data available"}</p>
    </div>
  );
}