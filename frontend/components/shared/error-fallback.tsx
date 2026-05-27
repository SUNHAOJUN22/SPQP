"use client";

import { AlertTriangle, RefreshCcw, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ErrorFallbackProps {
  moduleName?: string;
  error?: Error | null;
  onRetry?: () => void;
}

export function ErrorFallback({ moduleName, error, onRetry }: ErrorFallbackProps) {
  const copyError = () => {
    if (error?.stack) {
      navigator.clipboard.writeText(error.stack).catch(() => {});
    }
  };

  return (
    <Card className="mx-auto max-w-lg p-8 text-center" role="alert" aria-live="assertive">
      <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-studio-orange/15">
        <AlertTriangle className="h-8 w-8 text-studio-orange" />
      </div>
      <h3 className="mt-4 text-xl font-medium">模块加载异常</h3>
      <p className="mt-2 text-sm text-studio-muted">
        {moduleName ? `「${moduleName}」` : "当前模块"}渲染时发生错误。请尝试重新加载或联系开发者。
      </p>
      {error && (
        <p className="mt-3 break-all rounded-lg border border-studio-red/30 bg-studio-red/5 p-3 font-mono text-xs text-studio-red">
          {error.message}
        </p>
      )}
      <div className="mt-6 flex justify-center gap-2">
        {onRetry && (
          <Button icon={<RefreshCcw className="h-4 w-4" />} onClick={onRetry} aria-label="重试加载模块">
            重试加载
          </Button>
        )}
        {error?.stack && (
          <Button variant="secondary" icon={<Copy className="h-4 w-4" />} onClick={copyError} aria-label="复制错误信息">
            复制错误
          </Button>
        )}
      </div>
    </Card>
  );
}
