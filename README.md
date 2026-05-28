# 硅氧硅碳催化量子机理平台 Pro Max Ultra

SiO-SiC Polyolefin Quantum Mechanism Studio Ultra

这是一个中文科研计算平台，用于研究 Si-O / Si-C 键、Ziegler-Natta 催化、TEA 助催化剂、Ti 活性中心毒化、C=C 插入、Si-O-Si 后反应、过氧化物自由基、PP beta-scission、长链支化、交联和降解竞争机制。

本平台不是普通分子查看器，而是一个面向聚烯烃功能化和量子化学后处理的科研工作台。它把 Gaussian 输入生成、Gaussian log 只读解析、cube 只读预览、NBO / QTAIM / NCI 文本解析、能量公式、机制判据、证据等级和中文科研报告组织在同一个可审计流程中。

本 README 已按 GitHub 阅读体验重新排版：只保留一级标题和二级标题，正文不使用加粗标记，减少行内代码和大段 API 列表。详细接口、测试矩阵和长报告放在 docs 目录中，避免 README 在中英文混排、代码块和多级标题之间出现明显字体粗细跳变。

## 项目状态

- 当前版本：V4 Integrated / Pro Max Ultra
- 界面语言：中文简体
- 前端技术：Next.js、React、TypeScript、TailwindCSS、Framer Motion、Recharts
- 后端技术：FastAPI、Pydantic、SQLAlchemy、SQLite、numpy、pandas、scipy
- 数据边界：示例数据只用于演示，不能作为真实科研结论
- 安全边界：默认不执行 Gaussian、cubegen、Multiwfn、GoodVibes 或用户上传文件
- 发布仓库：[SUNHAOJUN22/SPQP](https://github.com/SUNHAOJUN22/SPQP)

## 核心能力

- 分子库：管理 DCS、MCSOMe、DMOS、ethylene、propylene、1-hexene、TEA、PP / EPC 小模型和过氧化物示例。
- Gaussian 输入生成：生成单体、TEA 络合、Ti 配位、插入 TS、IRC、水解缩合、BDE 和自由基路径模板。
- Gaussian 输出解析：只读解析能量、热校正、频率、虚频、HOMO / LUMO、电荷、NBO E(2)、Wiberg 键级和 Counterpoise 能量。
- cube 预览：只读解析 density、ESP、HOMO、LUMO、spin density 和 difference density 的网格元数据、切片和下采样信息。
- 机制计算：统一计算 Delta Gbind、Delta Gpoison、Delta Gpi、Delta Gddagger、krel、Si-C BDE、Si-O BDE、RO-OR BDE 和自由基竞争指标。
- 机制判据：给出 Ti 毒化、TEA 预组织、Si-O 削弱、Si-C 稳定性、PP 降解、长链支化、过凝胶和氧化风险的中文解释。
- 文献知识库：只读导入 docx、PDF 文本层或 OCR 文本，并把文献线索标注为 C 级证据。
- 报告生成：输出中文科研报告，明确区分真实计算、真实实验、文献线索、用户输入和示例数据。

## 科学边界

平台中的每个科学判断都必须带有数据来源和证据等级。

- A 级证据：真实 Gaussian、Multiwfn、NBO、QTAIM 或 NCI 计算结果，且收敛、频率、TS 虚频、IRC 和 provenance 完整。
- B 级证据：真实实验数据，样品、工艺和表征条件明确。
- C 级证据：文献线索或用户输入，尚未在当前体系复现。
- D 级证据：示例数据、mock 数据或趋势假说，只能用于演示和提出问题。

没有真实 A / B 级数据时，系统必须写明：当前数据不足，不能形成可靠结论。

## 核心公式

单位常数：

```text
1 Hartree = 627.509474 kcal/mol
1 Hartree = 2625.499638 kJ/mol
1 Hartree = 27.211386245988 eV
R = 0.00198720425864083 kcal mol^-1 K^-1
Default T = 350 K
```

配位与插入：

```text
Delta Gbind = G(complex) - sum G(fragments)
Delta Gpoison = G(O-to-Ti complex) - G(C=C pi-complex)
Delta Gpi = G(pi-complex) - G(free active site + monomer)
Delta Gddagger = G(TS) - G(free active site + monomer)
Delta Gddagger_complex = G(TS) - G(pi-complex)
krel = exp[-Delta Delta Gddagger / RT]
```

键解离能与自由基竞争：

```text
BDE(Si-C) = G(R radical) + G(silyl radical fragment) - G(R-Si)
BDE(Si-O) = G(R radical) + G(O-Si radical fragment) - G(R-O-Si)
BDE(RO-OR) = G(2 RO radical) - G(RO-OR)
R_scission = k_beta [PP radical]
R_branch = k_rec [PP radical]^2 + k_g [PP radical][M] + k_c [PP radical][coagent]
S_LCB = R_branch / (R_branch + R_scission + R_oxidation)
```

## 主要页面

- 首页总览：项目资源、数据健康状态、待补充数据、候选排序和风险提醒。
- 论文与报告知识库：真实文件实例、解析质量、OCR 文本导入、证据等级和 warnings。
- 分子库：分子资源表、结构视图、功能位点和 provenance。
- Gaussian 输入生成：任务模板、参数表单、输入文件预览和下载。
- Gaussian 输出解析：日志输入、normalized JSON、解析质量和中文 warnings。
- Si-O / Si-C 键实验室：键长、频率、键级、电荷、BCP、BDE 和稳定性判据。
- TEA 助剂作用：Al-O、Al-Cl、Al-C=C 络合和过度捕获风险。
- Ti 毒化判据：C=C pi-complex 与 O-to-Ti complex 的自由能竞争。
- 插入反应能量面：Delta Gpi、Delta Gddagger、Delta Gproduct 和 krel。
- 过氧化物自由基：RO-OR 均裂、PP 抽氢、beta-scission、复合、接枝和氧化风险。
- 中文科研报告：章节大纲、报告预览、证据与数据来源面板。

## 快速启动

安装依赖：

```bash
npm install
npm --prefix frontend install
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

启动服务：

```bash
npm run dev:backend
npm run dev
```

默认地址：

- 前端页面：http://localhost:3000
- 后端 API：http://localhost:8000
- OpenAPI 文档：http://localhost:8000/docs

## 常用验证

后端测试：

```bash
npm run test:backend
```

中文乱码审计：

```bash
npm run audit:mojibake
```

数理严谨性审计：

```bash
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
```

全功能 API 烟测：

```bash
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
```

前端验证：

```bash
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

根目录质量门禁：

```bash
python scripts\quality_gate.py
```

## 安全说明

- 默认不执行 Gaussian16。
- 默认不执行 cubegen。
- 默认不执行 Multiwfn。
- 默认不执行 GoodVibes。
- 默认不执行用户上传文件。
- Gaussian、Multiwfn、cubegen 和 GoodVibes 相关页面只生成输入、命令模板或解析文本。
- 上传文件只按文本或数据解析，不执行宏、脚本或外部程序。
- 示例数据始终标注为 mock 或 example，不能作为真实科研结论。

## 文档索引

- [科学计算工作流](docs/SCIENTIFIC_COMPUTATION_WORKFLOW.md)
- [科学计算完整测试报告](docs/SCIENTIFIC_COMPUTATION_FULL_TEST_REPORT.md)
- [科学严谨性测试报告](docs/SCIENTIFIC_RIGOR_TEST_REPORT.md)
- [科学计算测试报告](docs/SCIENTIFIC_CALCULATION_TEST_REPORT.md)
- [真实文件实例测试报告](docs/REAL_INSTANCE_TEST_REPORT.md)
- [UI / UX 测试报告](docs/UI_UX_TEST_REPORT.md)
- [全功能测试报告](docs/FULL_FUNCTION_TEST_REPORT.md)
- [Pro Max Ultra 质量报告](docs/ULTRA_QUALITY_TEST_REPORT.md)
- [中文乱码清理报告](docs/MOJIBAKE_CLEANUP_REPORT.md)
- [外部量子化学工具示例说明](docs/EXTERNAL_QC_RUN_EXAMPLES.md)
- [Si-O 子项目整合报告](docs/MERGE_REPORT.md)
- [整合来源映射](docs/INTEGRATION_SOURCE_MAP.md)

## Google Workspace 式交互逻辑

前端按 Google 系列产品的交互方式组织科研任务：

- Drive 式资源管理：项目、文献、Gaussian 输出、cube 文件、实验数据和报告都作为资源管理。
- Docs 式报告工作台：左侧章节大纲，中间报告预览，右侧证据与数据来源。
- Sheets 式数据表：实验记录、能量表、候选矩阵和资源列表支持搜索、筛选和排序。
- Colab 式计算模板：Gaussian 输入生成和解析流程以任务模板、参数、输出预览组织。
- Cloud Console 式安全面板：API、任务日志、数据源状态、provenance 和安全边界集中显示。

## 后续计划

- 真实 3Dmol cube 等值面渲染。
- Multiwfn 结构化导入和 NBO 高级解析。
- GoodVibes 真实格式样本扩展。
- 批量 Gaussian 任务图与 SLURM 脚本生成。
- 构象族 Boltzmann 权重和熵校正。
- 论文全文章节级知识抽取与表格定位。
- PostgreSQL 迁移与多项目协作。

## 排版说明

GitHub 会默认使用更重的字体渲染标题、表头、链接和代码块。本 README 已尽量统一视觉重量：不使用加粗标记，不使用多级标题，不使用 Markdown 表格，正文只保留必要的命令代码块。若继续扩展说明，请优先把长接口表、长测试矩阵和长报告内容放入 docs 目录。
