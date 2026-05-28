# Pro Max Ultra 自动化质量审计报告

- 测试时间：2026-05-28 09:51:49
- 测试环境：Windows / PowerShell / FastAPI TestClient / 本地 SQLite / Next.js 项目静态检查
- 通过数量：14
- 失败数量：0
- 未完成/跳过数量：1
- 安全边界：审计过程中未执行 Gaussian、cubegen、Multiwfn，也未执行用户上传文件。

## 测试总览

| 类别 | 项目 | 状态 | 耗时(ms) | 说明 |
| --- | --- | --- | ---: | --- |
| 科学常数 | Hartree/kcal/eV/R/T 常数 | PASS | 0.0 | 单位常数与默认温度匹配要求。 |
| 科学公式 | 自由能、速率与温度边界 | PASS | 0.0 | ΔGbind/ΔGpoison/ΔGπ/ΔG‡/krel 边界正确。 |
| 科学公式 | Si-C/Si-O/RO-OR BDE | PASS | 0.0 | BDE 单位转换与键类型标注可复现。 |
| 科学判据 | Ti 毒化、Si-C 稳定与 ΦLCB 边界 | PASS | 0.0 | Ti 毒化、自由基竞争和 mock 边界返回中文机制判断。 |
| Parser | Gaussian 完整/失败解析 | PASS | 1.8 | Gaussian parser 覆盖正常终止、Gibbs、虚频、HOMO/LUMO、NBO 与失败中文提示。 |
| Parser | cube 元数据、数值范围和错误路径 | PASS | 0.1 | cube 头、grid、atom、数值范围、下采样体素、剖切和差分预览可审计。 |
| 文献输入 | V4 DOCX 只读抽取可用性 | PASS | 0.6 | 未找到本机报告 DOCX，已验证内置 C 级报告方向线索与缺失文件边界：C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx |
| API | 核心量子化学与自由基接口 | PASS | 61.0 | 核心 API、科学计算任务矩阵、能量工作台与 BDE 入口正常响应且保持中文 provenance/mock 边界。 |
| API | 错误路径与中文提示 | PASS | 7.5 | 缺失能量、空 log、非法 cube 均返回中文错误或 failed 质量评分。 |
| API | GoodVibes/QTAIM/NCI/MCP 安全扩展 | PASS | 26.0 | 只读 parser 与 MCP 白名单工作流可追踪、可测试。 |
| 数据库 | 已实现表与提示要求表覆盖 | PASS | 0.3 | 数据库表覆盖完整。 |
| 安全 | 上传路径与文件类型边界 | PASS | 8.0 | 上传白名单、路径穿越和仅读取边界通过。 |
| 性能 | 1000 点 cube 快速元数据审计 | PASS | 0.4 | 1000 点 cube 元数据解析 0.000s。 |
| MCP/外部工具 | 外部化学软件执行边界 | PASS | 0.3 | README 与 API provenance 均声明不执行外部化学软件。 |
| 剩余矩阵 | 真实三维等值面重建 | SKIP | 0.0 | 当前已实现真实 cube 下采样点、剖切矩阵和差分预览；marching-cubes/Three.js 完整等值面重建仍未实现，本审计不把它标记为通过。 |

## 修复内容

- 新增报告 docx 只读抽取闭环：`POST /api/literature/import-report-docx` 与 `GET /api/literature/report-knowledge`，报告线索统一标注为 C 级证据。
- 顶尖科学家协议增加“报告驱动闭环扩展槽位”，把 Si–C 稳定性、PP β-scission、羰基三分法、乙烯/等规度/结晶度窗口映射到 API、UI、报告和测试。
- 中文报告新增“报告知识映射”“Si–C 连接稳定性”“羰基三分法”“乙烯/等规度/结晶度影响”“软件化执行接口”等章节，并自动合并最新导入报告知识。
- 前端“论文知识库”新增报告驱动知识映射、可编辑报告 docx 路径、C 级证据卡片和机制模型/反证条件展示；“MCP 自动化工作流”新增报告证据闭环展示。
- 新增 OCR 文本导入和真实文件实例摘要：`POST /api/literature/import-ocr-text`、`GET /api/literature/source-quality`、`GET /api/literature/real-instance-summary`，PDF 乱码统一标记为 encoded-garbled。
- 中文报告新增“真实文件实例测试”章节，自动写入 C 级文献线索、PDF 文本层乱码 warning、OCR 文本边界和 A/B 级结论禁止条件。
- UI 重构为 Google Workspace 式科研工作台：分组导航、顶部全局搜索、资源表格、右侧详情面板、Drive 风格分子库/数据管理、Sheets 风格实验-DFT 对照、Colab/Docs 风格 Gaussian 输入生成、Docs 风格报告页、Cloud Log Viewer 风格 Gaussian 解析页、Cloud Console 风格 MCP 工具页和表格优先的量子判据引擎。
- 新增科学计算验证机制工作流：`GET /api/scientific-computation/task-matrix`、`POST /api/scientific-computation/energy-workbench`、`POST /api/analysis/bde` 和“科学计算工作流”前端页面，把任务模板、自由能公式、BDE、证据等级和报告边界串成闭环。
- 新增 `scripts/mojibake_audit.py` 和根目录 `npm run audit:mojibake`，用于扫描活动文件中的中文乱码；当前活动文件疑似乱码行数为 0，归档来源目录仅记录不参与构建。
- 修复“前线轨道”和“电荷布居”面板历史乱码，移除未引用的旧 `frontend/fix.js`。
- 收紧上传文件名校验，拒绝路径穿越、绝对路径、过长文件名和非法扩展名。
- cube parser 增加 expected_value_count、value_count_status 和等值面元数据，便于前端和测试判断真实数据缺失。
- 增加 GoodVibes、QTAIM、NCI 只读解析器、MCP 安全白名单 API 和对应回归测试。
- 补齐 atom/bond/orbital/QTAIM/NCI/实验表征/MCP/audit 数据表与别名 API。
- 增加根目录 npm 覆盖率和 E2E 入口，使 lint/typecheck/test/e2e/build 可按统一命令执行。

## 科学公式测试结果

- Hartree、kcal/mol、eV、R、默认 350 K 常数已自动核查。
- ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔΔG‡、krel 的边界和温度行为已自动核查。
- Si–C、Si–O、Si–Cl、RO–OR BDE 公式已自动核查，单位为 Hartree、kcal/mol 和 eV。

## Parser 测试结果

- Gaussian parser 覆盖正常终止、SCF、Gibbs、频率/虚频、HOMO/LUMO、Mulliken、NPA、Wiberg、NBO E(2)、Counterpoise 和空文件失败路径。
- cube parser 覆盖 grid、origin、atom、scalar field 计数、数值范围和错误 cube 中文提示。
- GoodVibes、QTAIM、NCI 轻量文本 parser 已自动验证；不同外部程序的大型变体输出仍需样本驱动扩展。

## UI 测试结果

- UI 的构建、lint、typecheck 由质量门禁和 root npm scripts 执行。
- Playwright 已固定为根依赖，浏览器 UI smoke 已覆盖全导航抽样、Gaussian 输出解析、cube 上传预览、合并工作台、MCP 安全工作流和 390px 移动端。
- Playwright UI smoke 已新增检查“报告驱动知识映射”和“MCP 报告证据闭环”。
- Playwright UI smoke 已新增检查“真实文件实例”“PDF 文本层疑似字体编码异常”“导入 OCR 文本”和“C级证据”。
- Playwright UI smoke 已新增检查 Google 式分组导航、顶部搜索框、报告页“章节大纲/报告预览/证据与数据来源”和 Gaussian 页“仅读取，不执行 Gaussian”。
- Playwright UI smoke 已新增检查分子库“分子资源表/结构视图/分子详情”、Gaussian Builder“任务模板/输入文件预览/不执行 Gaussian”和 MCP“工具列表/工具详情/输入 schema/运行结果/安全边界”。
- Playwright UI smoke 已新增检查数据管理“资源表/provenance 审计”、实验-DFT 对照“实验记录来源”和量子判据引擎“判据资源表/证据与结论边界”。
- Playwright UI smoke 已新增检查“科学计算工作流”“计算任务矩阵”“能量公式工作台”和“BDE 计算”。
- 中文乱码审计已接入质量门禁，保证活动 UI 文案、脚本和当前文档不会再次出现常见 UTF-8/GBK 误解码痕迹。

## API 测试结果

- 核心 molecule、Gaussian input、Gaussian parse、energy、Ti poisoning、peroxide、ΦLCB、report 接口已审计。
- 科学计算 API 已覆盖 36 任务矩阵、能量公式工作台、BDE 计算和自由基动力学分析别名。
- `/api/mcp/*` 已提供安全白名单工作流：工具列表、资源索引、prompt 生成和受控 tool run。
- 文献 API 已覆盖报告 docx、OCR 文本、解析质量列表和真实文件实例摘要；乱码 PDF 不会把关键词为 0 解释为无相关机理。

## E2E 测试结果

- `npm run test:e2e` 映射到 `scripts/ui_smoke_check.mjs`，检查前后端可达性并执行 Playwright 交互烟测。
- E2E 需要本地后端 `http://127.0.0.1:8000` 和前端 `http://localhost:3000` 可访问。
- 完整报告导出截图矩阵和 marching-cubes 三维等值面重建仍建议作为下一阶段补齐。

## 安全测试结果

- 上传扩展名白名单和路径穿越已测试。
- 真实外部化学软件执行默认禁止，仅保留文本生成和只读解析。

## 性能测试结果

- 1000 点 cube 元数据解析通过快速审计。
- 大表格虚拟滚动、真实大 cube marching-cubes 等值面渲染和大型 Gaussian log Web Worker 压测仍建议继续扩展。

## 剩余风险

- 剩余矩阵 / 真实三维等值面重建：当前已实现真实 cube 下采样点、剖切矩阵和差分预览；marching-cubes/Three.js 完整等值面重建仍未实现，本审计不把它标记为通过。

## 下一步建议

- 以真实 GoodVibes、QTAIM、NCI 大文件样本扩充 parser 适配矩阵，并把稳定 JSON schema 接到 UI 图层。
- 扩展 Playwright 为报告导出、真实大 cube 性能和全页面截图矩阵。
- 引入迁移工具后，把当前扩展表纳入正式 PostgreSQL migration。
