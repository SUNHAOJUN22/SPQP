# CHANGELOG

## [Pro Max Ultra] - 2026-05-13

### 🚀 自动化重构与质量总控 (Massive QA Refactor)
- **API 路由器修复**: 自动修复了 `analysis.py` 中错误的类导入，安全接管至 `DecisionEngineUltra` 核心。
- **自动化测试扩容**: 单元测试从 92 项扩编至 101 项，并补齐了针对 API 接口防御机制（防注入、异常值处理）的断言。
- **Playwright E2E 集成**: 前端新增了浏览器引擎全链路驱动测试，验证了关键路径 (Settings, UI Layout)。
- **NPM Package 修复**: `package.json` 加入了官方测试流指令 `npm run test:e2e` 与 `typecheck`，方便 CI 自动化拉取。

### 🚀 核心架构突破 (Core Architecture Breakthroughs)
- **四轴机制模型完全成型**: 系统正式上线单体、催化剂、自由基、微相四大科学评估轴。
- **MCP 自动化工作流引擎集成**: 新增 `/mcp/workflow` 面板，支持 17 项量子计算与数据提取工具，完美对接 Claude/Cursor Agent。
- **实验与量子闭环验证**: 新增 `/experimental/loop` 闭环中心，整合 GPC / MFR / FTIR 等 9 类实验数据的自动决策矩阵关联。

### 🔬 科学核心增强 (Scientific Engine Enhancements)
- **过氧化物库支持**: 在 `conversions.py` 与动力学矩阵中实现了真实的 `BDE(RO-OR)` 过氧化物均裂能与 β-scission / branching 速率比自动测算。
- **Gaussian 任务流全家桶**: `GaussianBuilder` 的预设支持扩展到 36 项核心模板（覆盖组 A 单体 到组 F 自由基）。
- **毒化判据校准**: 精确测算了 $\Delta G_{poison}$，将 MCSOMe 与 DMOS 的 O→Ti 毒化竞争机制与 C=C 配位插入机制正式量化。

### 💻 界面与工程化 (UI & Engineering)
- **全面完成测试用例**: 后端测试规模突破 92 项，并达成 100% 通过率。
- **高级量子 UI 界面**: `/orbital/[slug]` 实现深度迭代，搭载 $\rho(r)$ 与 $V(r)$ 物理公式与占位符级态警告。
- **自动化修缮与重构**: 前端所有 `lucide-react` 图标属性修正 (如移除 `title` 属性)，TypeScript 类型全量修正通过。

### 🛡️ 安全与稳定性 (Security & Stability)
- 实现了无 cube 数据上传时的前置拦截验证。
- 后端计算隔离框架跑通，严谨划分测试用例的 Mock 数据与计算日志层。
- 前端 `Next.js 14` 成功进行生产打包与优化，路由性能增强。
