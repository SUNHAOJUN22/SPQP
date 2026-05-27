"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface Props {
  children: ReactNode;
  fallbackModule?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`[${this.props.fallbackModule ?? "Module"}] Error:`, error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="mx-auto max-w-lg p-8 text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-studio-orange" />
          <h3 className="mt-4 text-xl font-medium">模块加载异常</h3>
          <p className="mt-2 text-sm text-studio-muted">
            {this.props.fallbackModule
              ? `「${this.props.fallbackModule}」`
              : "当前模块"}
            渲染时发生错误。请尝试重新加载。
          </p>
          <p className="mt-2 break-all font-mono text-xs text-studio-red">
            {this.state.error?.message}
          </p>
          <Button
            className="mt-6"
            icon={<RefreshCcw className="h-4 w-4" />}
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            重试加载
          </Button>
        </Card>
      );
    }
    return this.props.children;
  }
}
