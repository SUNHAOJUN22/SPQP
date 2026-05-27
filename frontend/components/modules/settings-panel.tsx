"use client";
import { useState } from "react";
import { Activity, CheckCircle2, Info, ShieldCheck, Wifi, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FieldLabel, Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { useStudio } from "@/lib/store";

export function SettingsPanel() {
  const { theme, toggleTheme } = useStudio();
  const [connStatus, setConnStatus] = useState<"idle" | "testing" | "ok" | "fail">("idle");
  const [connTime, setConnTime] = useState(0);

  async function testConnection() {
    setConnStatus("testing");
    const start = Date.now();
    try {
      const res = await fetch("http://localhost:8000/api/health", { signal: AbortSignal.timeout(5000) });
      setConnTime(Date.now() - start);
      setConnStatus(res.ok ? "ok" : "fail");
    } catch {
      setConnTime(Date.now() - start);
      setConnStatus("fail");
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
      <div className="space-y-4">
        {/* 系统配置 */}
        <Card>
          <CardHeader>
            <div><CardTitle>系统设置</CardTitle><CardDescription>Gaussian16 路径必须显式配置；默认不执行外部程序。</CardDescription></div>
            <StatusBadge tone="green">安全默认</StatusBadge>
          </CardHeader>
          <div className="grid gap-4 md:grid-cols-2">
            <div><FieldLabel>Gaussian16 路径</FieldLabel><Input className="mt-2" placeholder="未配置" /></div>
            <div><FieldLabel>默认温度</FieldLabel><Input className="mt-2" defaultValue="350 K" /></div>
            <div><FieldLabel>主题</FieldLabel><Select className="mt-2" value={theme} onChange={() => toggleTheme()}><option value="dark">深色主题</option><option value="light">浅色主题</option></Select></div>
            <div><FieldLabel>数据库</FieldLabel><Input className="mt-2" readOnly value="SQLite MVP / 已预留 PostgreSQL 结构" /></div>
          </div>
        </Card>

        {/* 连接测试 */}
        <Card>
          <CardHeader>
            <div><CardTitle>后端连接测试</CardTitle><CardDescription>测试前端到 FastAPI 后端的连接状态</CardDescription></div>
            <Button
              variant={connStatus === "ok" ? "primary" : "secondary"}
              icon={<Wifi className="h-4 w-4" />}
              onClick={testConnection}
              disabled={connStatus === "testing"}
            >
              {connStatus === "testing" ? "测试中…" : "测试连接"}
            </Button>
          </CardHeader>
          {connStatus !== "idle" && (
            <div className="flex items-center gap-3 rounded-xl border border-studio-line bg-studio-panel/70 p-4">
              {connStatus === "testing" && <Activity className="h-5 w-5 animate-spin text-studio-cyan" />}
              {connStatus === "ok" && <CheckCircle2 className="h-5 w-5 text-studio-green" />}
              {connStatus === "fail" && <XCircle className="h-5 w-5 text-studio-red" />}
              <div>
                <p className="font-medium">
                  {connStatus === "testing" && "正在测试连接…"}
                  {connStatus === "ok" && "连接成功 ✅"}
                  {connStatus === "fail" && "连接失败 ❌"}
                </p>
                {connStatus !== "testing" && (
                  <p className="text-xs text-studio-muted">
                    响应时间：{connTime} ms · 端点：http://localhost:8000/api/health
                  </p>
                )}
              </div>
            </div>
          )}
        </Card>

        {/* 版本信息 */}
        <Card>
          <CardHeader><div><CardTitle>版本信息</CardTitle><CardDescription>System version details</CardDescription></div><Info className="h-5 w-5 text-studio-muted" /></CardHeader>
          <div className="grid gap-3 md:grid-cols-4">
            {[
              ["前端版本", "0.1.0"],
              ["Next.js", "16.2.4"],
              ["React", "19.x"],
              ["后端", "FastAPI 0.115+"],
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-xl border border-studio-line bg-studio-panel/70 p-4">
                <p className="text-xs text-studio-muted">{label}</p>
                <p className="mt-1 font-mono text-lg font-medium">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 错误提示规范 */}
      <Card>
        <CardHeader>
          <div><CardTitle>中文错误提示规范</CardTitle><CardDescription>Error messages</CardDescription></div>
          <ShieldCheck className="h-5 w-5 text-studio-green" />
        </CardHeader>
        {[
          "未检测到 Gaussian 正常终止标记。",
          "当前文件中未找到吉布斯自由能。",
          "当前文件中未找到 NBO 二阶微扰分析结果。",
          "未上传 electron density cube 文件，无法显示真实电子云密度。",
          "SMILES 解析失败，请检查输入格式。",
          "上传文件超过大小限制（最大 50 MB）。",
        ].map((item) => (
          <p key={item} className="mb-3 rounded-xl border border-studio-line bg-studio-panel/70 p-4 text-sm text-studio-muted data-mock">
            {item}
          </p>
        ))}
      </Card>
    </div>
  );
}
