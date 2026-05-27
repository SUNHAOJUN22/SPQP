import type React from "react";
import { cn } from "@/lib/utils";

export type ResourceColumn<T> = {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => React.ReactNode;
};

export function ResourceTable<T>({
  rows,
  columns,
  getRowKey,
  selectedKey,
  onSelect,
  empty,
}: {
  rows: T[];
  columns: ResourceColumn<T>[];
  getRowKey: (row: T) => string;
  selectedKey?: string;
  onSelect?: (row: T) => void;
  empty?: React.ReactNode;
}) {
  if (!rows.length) {
    return <>{empty ?? <div className="rounded-xl border border-dashed border-studio-line p-6 text-sm text-studio-muted">当前没有可显示资源。</div>}</>;
  }
  return (
    <div className="overflow-hidden rounded-xl border border-studio-line bg-studio-panel/75">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-left text-sm">
          <thead className="bg-studio-panel2/70 text-xs uppercase tracking-[0.12em] text-studio-muted">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className={cn("border-b border-studio-line px-4 py-3 font-medium", column.className)}>{column.header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const key = getRowKey(row);
              const active = selectedKey === key;
              return (
                <tr
                  key={key}
                  onClick={() => onSelect?.(row)}
                  className={cn(
                    "border-b border-studio-line/70 transition last:border-b-0",
                    onSelect && "cursor-pointer hover:bg-studio-panel2/70",
                    active && "bg-studio-cyan/10"
                  )}
                >
                  {columns.map((column) => (
                    <td key={column.key} className={cn("px-4 py-3 align-top", column.className)}>{column.render(row)}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
