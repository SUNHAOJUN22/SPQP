#!/usr/bin/env node

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const frontendUrl = process.env.FRONTEND_URL ?? "http://localhost:3000";
const apiUrl = process.env.API_URL ?? "http://127.0.0.1:8000";
const screenshotDir = join(process.cwd(), "docs", "test-screenshots");

const sampleLog = `
 SCF Done:  E(RB3LYP) =  -682.123456789     A.U. after   10 cycles
 Sum of electronic and thermal Free Energies=         -682.032223
 Frequencies --  -321.45   45.67   80.12
 Alpha  occ. eigenvalues --  -0.40100  -0.25000
 Alpha virt. eigenvalues --   0.03000   0.07000
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
`;

function pass(name, detail = "") {
  console.log(`[PASS] ${name}${detail ? ` - ${detail}` : ""}`);
}

function fail(name, detail) {
  throw new Error(`[FAIL] ${name}: ${detail}`);
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) fail(url, `${response.status} ${await response.text()}`);
  return response.json();
}

async function httpSmoke() {
  const health = await fetchJson(`${apiUrl}/api/health`);
  if (health.status !== "ok") fail("后端健康检查", JSON.stringify(health));
  pass("后端健康检查", `${apiUrl}/api/health`);

  const docs = await fetch(`${apiUrl}/docs`);
  if (!docs.ok) fail("OpenAPI 文档", `${docs.status}`);
  pass("OpenAPI 文档", `${apiUrl}/docs`);

  const frontend = await fetch(frontendUrl);
  const html = await frontend.text();
  if (!frontend.ok) fail("前端首页", `${frontend.status}`);
  if (!html.includes("__next") && !html.includes("SiO Catalyst")) {
    fail("前端首页", "未检测到 Next.js 页面标记");
  }
  pass("前端首页", frontendUrl);
}

async function browserSmokeWithPlaywright() {
  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.log("[SKIP] 未安装 playwright，已执行 HTTP UI smoke；真实浏览器巡检请使用 Codex Browser 或安装 playwright。");
    return;
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  for (const groupLabel of ["首页", "知识库", "分子与结构", "量子计算", "机理分析", "报告", "自动化"]) {
    await page.getByText(groupLabel, { exact: true }).first().waitFor({ timeout: 15000 });
  }
  await page.getByPlaceholder("搜索分子、任务、报告、证据…").first().waitFor({ timeout: 15000 });
  const navigationLabels = [
    "整合总控台",
    "总览驾驶舱",
    "分子库",
    "科学计算工作流",
    "Gaussian 输入生成",
    "Gaussian 输出解析",
    "Si–O / Si–C 键实验室",
    "过氧化物自由基",
    "自由基动力学",
    "电子云密度",
    "ESP 静电势",
    "Fukui 局部反应性",
    "差分电子密度",
    "前线轨道",
    "NBO 相互作用",
    "QTAIM / NCI 分析",
    "中文报告生成",
    "MCP 自动化工作流",
  ];
  for (const label of navigationLabels) {
    await page.getByRole("button", { name: new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")) }).click();
    await page.waitForTimeout(80);
  }

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /^整合总控台$/ }).click();
  await page.getByText("整合总控台").first().waitFor();
  await page.getByText(/项目资源总览/).first().waitFor({ timeout: 15000 });
  await page.getByText(/Gaussian 任务模板宇宙/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /论文知识库/ }).click();
  await page.getByText(/报告驱动知识映射/).first().waitFor({ timeout: 15000 });
  await page.getByText(/C 级|C级|内置线索|报告已导入/).first().waitFor({ timeout: 15000 });
  await page.getByText(/真实文件实例/).first().waitFor({ timeout: 15000 });
  await page.getByText(/解析质量/).first().waitFor({ timeout: 15000 });
  await page.getByText(/PDF 文本层疑似字体编码异常/).first().waitFor({ timeout: 15000 });
  await page.getByText(/导入 OCR 文本/).first().waitFor({ timeout: 15000 });
  await page.getByText(/C级证据/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /分子库/ }).click();
  await page.getByText(/分子资源表/).first().waitFor({ timeout: 15000 });
  await page.getByText(/结构视图/).first().waitFor({ timeout: 15000 });
  await page.getByText(/分子详情/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /科学计算工作流/ }).click();
  await page.getByText(/计算任务矩阵/).first().waitFor({ timeout: 15000 });
  await page.getByText(/能量公式工作台/).first().waitFor({ timeout: 15000 });
  await page.getByText(/BDE 计算/).first().waitFor({ timeout: 15000 });
  await page.getByRole("button", { name: /计算自由能差/ }).first().click();
  await page.getByText(/ΔGbind|ΔGpoison/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /Gaussian 输入生成/ }).click();
  await page.getByText(/任务模板/).first().waitFor({ timeout: 15000 });
  await page.getByText(/输入文件预览/).first().waitFor({ timeout: 15000 });
  await page.getByText(/不执行 Gaussian，仅生成输入文件/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /Gaussian 输出解析/ }).click();
  await page.getByText(/仅读取，不执行 Gaussian/).first().waitFor({ timeout: 15000 });
  await page.getByPlaceholder("粘贴 Gaussian 输出文本进行本地 Worker 预览").fill(sampleLog);
  await page.getByRole("button", { name: /解析文件/ }).waitFor({ state: "visible", timeout: 15000 });
  await page.getByRole("button", { name: /解析文件/ }).click();
  await page.getByText(/normalized JSON|normal_termination|解析质量/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /中文报告生成/ }).click();
  await page.getByText(/章节大纲/).first().waitFor({ timeout: 15000 });
  await page.getByText(/报告预览/).first().waitFor({ timeout: 15000 });
  await page.getByText(/证据与数据来源/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /数据管理/ }).click();
  await page.getByText(/数据来源与可靠性/).first().waitFor({ timeout: 15000 });
  await page.getByText(/资源表/).first().waitFor({ timeout: 15000 });
  await page.getByText(/provenance 审计/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /实验数据闭环/ }).click();
  await page.getByText(/实验-DFT 对照/).first().waitFor({ timeout: 15000 });
  await page.getByText(/实验数据记录/).first().waitFor({ timeout: 15000 });
  await page.getByText(/实验记录来源/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /量子判据引擎/ }).click();
  await page.getByText(/判据资源表/).first().waitFor({ timeout: 15000 });
  await page.getByText(/证据与结论边界/).first().waitFor({ timeout: 15000 });
  await page.getByText(/中文论文式结论模板/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /合并工作台/ }).click();
  await page.getByRole("button", { name: /运行四轴判据示例/ }).click();
  await page.getByRole("button", { name: /运行后反应动力学/ }).click();
  await page.getByText(/四轴判据|后反应动力学|RK4/).first().waitFor({ timeout: 15000 });

  await page.getByRole("button", { name: /电子云密度/ }).click();
  mkdirSync(screenshotDir, { recursive: true });
  const cubePath = join(screenshotDir, "ui-smoke-density.cube");
  writeFileSync(
    cubePath,
    [
      "density smoke",
      "small cube",
      " 1 0.0 0.0 0.0",
      " 2 1.0 0.0 0.0",
      " 2 0.0 1.0 0.0",
      " 2 0.0 0.0 1.0",
      " 8 0.0 0.0 0.0 0.0",
      " -0.4 -0.2 0.1 0.3 0.5 0.7 -0.1 0.0",
      "",
    ].join("\n"),
    "utf8"
  );
  await page.getByLabel("上传 cube 文件").setInputFiles(cubePath);
  await page.getByText(/真实 cube 预览|已读取标量场/).first().waitFor({ timeout: 15000 });
  await page.screenshot({ path: join(screenshotDir, "electron-density-cube-preview.png"), fullPage: true });

  await page.getByRole("button", { name: /MCP 自动化工作流/ }).click();
  await page.getByText(/工具列表/).first().waitFor({ timeout: 15000 });
  await page.getByText(/工具详情/).first().waitFor({ timeout: 15000 });
  await page.getByText(/输入 schema/).first().waitFor({ timeout: 15000 });
  await page.getByText(/运行结果/).first().waitFor({ timeout: 15000 });
  await page.getByText(/安全边界/).first().waitFor({ timeout: 15000 });
  await page.getByText(/顶尖科学家进化协议/).first().waitFor({ timeout: 15000 });
  await page.getByText(/报告证据闭环/).first().waitFor({ timeout: 15000 });
  await page.getByText(/A级证据/).first().waitFor({ timeout: 15000 });
  await page.getByText(/量子化学任务矩阵/).first().waitFor({ timeout: 15000 });
  await page.getByText(/实验表征映射/).first().waitFor({ timeout: 15000 });
  await page.getByRole("button", { name: /生成顶尖科学家 Prompt/ }).click();
  await page.getByText(/安全边界/).first().waitFor({ timeout: 15000 });
  await page.getByText(/证据等级/).first().waitFor({ timeout: 15000 });
  await page.getByRole("button", { name: /运行安全示例/ }).click();
  await page.getByText(/allowed/).first().waitFor({ timeout: 15000 });

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  if (overflow) fail("页面横向溢出检查", "documentElement.scrollWidth 超出视口");

  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /总览驾驶舱/ }).click();
  await page.getByText(/待处理任务/).first().waitFor({ timeout: 15000 });
  const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  if (mobileOverflow) fail("390px 移动端横向溢出检查", "documentElement.scrollWidth 超出视口");
  await page.screenshot({ path: join(screenshotDir, "mobile-dashboard-390.png"), fullPage: true });

  if (consoleErrors.length) fail("控制台 error 检查", consoleErrors.join("\n"));
  await browser.close();
  pass("Playwright 浏览器 UI smoke", "全导航抽样、Gaussian 解析、cube 预览、合并工作台、MCP 工作流和 390px 移动端通过");
}

await httpSmoke();
await browserSmokeWithPlaywright();
