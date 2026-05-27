# 科学计算验证测试报告

## 测试时间

2026-05-27

## 测试环境

- 工作目录：`D:\codex2_cataSi-O`
- 后端：FastAPI / Python 3.11+
- 前端：Next.js / React / TypeScript
- 安全边界：本轮未执行 Gaussian、cubegen、Multiwfn、GoodVibes 或用户上传文件。

## 本轮新增能力

- 新增 `GET /api/scientific-computation/task-matrix`，显式输出 36 个 Gaussian / 后处理任务模板、关键输出、可靠性判据和安全边界。
- 新增 `POST /api/scientific-computation/energy-workbench`，统一计算 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔGproduct、krel，并返回中文缺失数据提示。
- 新增 `POST /api/analysis/bde`，支持 Si-C、Si-O、Si-Cl、RO-OR BDE 计算，并保留 evidence_grade、source、is_mock 和 provenance。
- 新增 `POST /api/analysis/radical-kinetics`，作为自由基动力学 ODE 工作流的分析入口。
- 新增前端页面“科学计算工作流”，包含任务矩阵、能量公式工作台、BDE 计算和报告边界说明。

## 数理公式核查

已覆盖：

- Hartree 到 kcal/mol、eV 的换算。
- ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、krel。
- BDE = ΣG(fragments) - G(parent)。
- 自由基动力学入口保留 `R_branch` 与 `S_LCB` 公式说明。

## 判据边界核查

已覆盖：

- ΔGpoison 三段式判据。
- Si-C BDE 高/低风险判据。
- 示例数据不能作为真实结论。
- 缺少 Gibbs、π-complex、O->Ti complex 或 TS 时返回中文 warnings。

## Parser 边界

本轮未改变 Gaussian/cube/NBO/QTAIM/NCI parser 的只读原则。所有新增接口仅消费用户输入或已解析数据，不执行外部程序。

## API 测试

新增后端测试文件：

- `backend/tests/test_scientific_computation_workflow.py`

覆盖：

- BDE core 单位与判据。
- 36 任务矩阵与安全边界。
- 能量公式工作台正常路径与缺失路径。
- BDE API 的 evidence/mock 边界。
- 自由基动力学分析别名。

## UI 测试

已扩展 `scripts/ui_smoke_check.mjs`：

- 检查导航中存在“科学计算工作流”。
- 检查页面包含“计算任务矩阵”、“能量公式工作台”、“BDE 计算”。
- 点击“计算自由能差”并检查 ΔGbind/ΔGpoison 输出。

## 剩余风险

- BDE 阈值用于工作流提示，不能替代真实高精度计算或实验验证。
- 过氧化物半衰期、自由基扩散、氧化副反应和 coagent 捕获仍需真实实验或文献参数。
- TS 合格性仍需真实频率和 IRC，不得由本平台模板自动判定。
- 前端 3D/cube 真实渲染依赖用户上传 cube 文件；无 cube 时只能显示缺失数据提示。

## 结论

本轮将“通过科学计算验证机制”的要求从说明性文档推进为可调用 API、可运行测试、可见 UI 和可审计报告边界。所有新增功能保持“只生成、只解析、不执行外部化学软件”的安全原则。
