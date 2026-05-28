# 硅氧键催化量子研究平台

英文副名：SiO Catalyst Quantum Studio Pro

本平台不是普通分子查看器，而是一个面向 Si–O / Si–C 键、Ziegler–Natta 配位插入、TEA 助催化剂、过氧化物自由基、PP 长链支化-交联-降解竞争机制的中文量子化学科研操作系统。

这是一个面向中文科研用户的全栈量子化学工作流应用，用于研究 Ziegler–Natta 催化剂中功能 α-烯烃、Si–O / Si–Cl 电子结构、TEA 助催化剂相互作用、Ti 活性中心毒化、插入反应自由能面以及水解缩合后反应。

当前版本为 V4 Integrated：在中文可视化 MVP、论文驱动 V2 和 V3 合并工作台基础上，新增“自由基后反应与硅碳键机理”研究线，用于分析过氧化物诱导聚丙烯降解/交联/长链支化、Si–C 键稳定性、含羰基过氧化物、乙烯引入、等规度和停留时间窗口。

本仓库已拆解原独立 `Si-O` 子项目，并将其前端、后端、脚本、文档、部署文件和资产归入根项目 `integrated/origin-*` 分类资产库。当前默认首页为“整合总控台”，用于展示 V3 整合状态、Gaussian 任务宇宙、拆解资产分布和统一工作流。

## 当前 UI 工作台方向

2026-05-26 版本继续按 Google 系列产品逻辑优化：

- “整合总控台”改为 Google Cloud Console 式项目入口，集中展示项目资源、Gaussian 任务模板、运行边界和 provenance。
- “总览驾驶舱”改为任务优先的科研首页，使用待处理任务表、候选资源表和右侧数据可靠性面板，减少堆叠卡片。
- “合并工作台”已清理历史乱码，保留四轴判据示例、后反应动力学、贝叶斯 TS 搜索和 VMC 预览，并明确示例数据边界。
- “电子云密度 / ESP / Fukui / 差分电子密度”统一中文化 cube 上传、真实标量场、剖切预览、色标和缺失数据提示。
- TEA 助剂、Ti 毒化、插入反应能量面、水解缩合和 NBO 页面已改为中文机制叙述、图表标题和公式说明。
- “科学计算工作流”新增 36 任务矩阵、能量公式工作台、BDE 计算与证据等级边界，用于把机制问题转化为可审计计算任务和报告章节。
- 新增中文乱码审计：`npm run audit:mojibake` 会扫描活动源码、脚本、测试和当前文档；`integrated/origin-*` 历史来源目录只记录在报告中，不参与生产构建修复。

## 中文乱码审计

运行：

```bash
npm run audit:mojibake
```

审计报告输出到：

```text
docs/MOJIBAKE_CLEANUP_REPORT.md
```

当前活动文件疑似乱码行数为 0。若后续新增中文文本或从外部文档复制内容，应先运行该命令，再运行完整质量门禁。

## 科学计算验证工作流

新增“科学计算工作流”模块，用于把 Si–O / Si–C / TEA / Ti 毒化 / 插入 / 过氧化物自由基问题转化为可执行计算任务、可解析数据结构、可证伪判据和中文报告输出。

核心 API：

```text
GET  /api/scientific-computation/task-matrix
POST /api/scientific-computation/energy-workbench
POST /api/analysis/bde
POST /api/analysis/radical-kinetics
```

该模块支持：

- 36 个 Gaussian / 后处理任务模板矩阵，只生成文本，不执行外部软件。
- ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔGproduct、krel 统一计算。
- Si–C、Si–O、Si–Cl、RO–OR BDE 计算，单位包括 Hartree、kcal/mol 和 eV。
- 缺少 Gibbs、π-complex、O→Ti complex 或 TS 时返回中文 warnings。
- 所有结果保留 evidence grade、source、is_mock 和 provenance。

详细文档：

```text
docs/SCIENTIFIC_COMPUTATION_WORKFLOW.md
docs/SCIENTIFIC_CALCULATION_TEST_REPORT.md
```

## 科学背景

项目围绕博士论文主题：

“基于 Ziegler-Natta 催化剂的乙烯、丙烯与功能 α-烯烃单体配位共聚合反应的空间位阻与电子效应研究”。

软件将论文中的研究线索结构化为：

- 单体族：ω-烯烃基三甲基硅烷、ω-烯烃基甲基二氯硅烷、甲氧基硅烷衍生物。
- 链长：3-butenyl、5-hexenyl、7-octenyl。
- 共聚单体：乙烯、丙烯、1-己烯。
- 催化剂模型：MgCl2/TiCl4/Et、MgCl2/BMMF/TiCl4/iBU、TEA 助催化剂。
- 判据：ΔGbind、ΔGpoison、ΔGπ、ΔG‡、krel、NBO E(2)、QTAIM/NCI、实验插入率与聚合活性。
- V4 后反应变量：RO–OR BDE、Si–C BDE、过氧化物半衰期、停留时间、PP β-scission、自由基复合/接枝、氧化风险、乙烯含量、等规度与结晶度。

示例/mock 数据只用于界面演示，不能作为真实量子化学结论。

## 安装

前端：

```bash
npm --prefix frontend install
```

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

建议使用 Python 3.11+。RDKit 用于分子描述符和构象生成；若本机 RDKit 不可用，后端会退化为明确标注的近似描述符。

## 启动

前端：

```bash
npm run dev
```

后端：

```bash
npm run dev:backend
```

默认地址：

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- OpenAPI：http://localhost:8000/docs

## 论文知识库

导入博士论文 docx：

```http
POST /api/literature/import-thesis
```

默认路径：

```text
C:\Users\resj6\Desktop\pri\博士学位论文.docx
```

后端仅读取 docx 文本，不执行宏、不执行外部命令。抽取结果包括论文主题、单体族、链长、催化剂模型、助催化剂、DFT 模型和关键机制线索。

查看实体：

```http
GET /api/literature/entities
GET /api/catalyst-models
```

## 分子库

内置分子包括：

- DCS / MCSOMe / DMOS
- 3-butenyltrimethylsilane、5-hexenyltrimethylsilane、7-octenyltrimethylsilane
- 3-butenyl-methyl-dichlorosilane、5-hexenyl-methyl-dichlorosilane、7-octenyl-methyl-dichlorosilane
- ethylene、propylene、1-hexene、TEA

新增分子：

```http
POST /api/molecules
```

导出 RDKit 生成的初始 XYZ：

```http
GET /api/molecules/{id}/xyz
GET /api/molecules/{id}/graph
```

注意：RDKit XYZ 和 SMILES 分子图不是 Gaussian 优化构型。`/graph` 会返回原子/键和功能位点识别结果，并保留“不能替代真实量子化学几何”的 provenance。

## Gaussian 输入生成

```http
POST /api/gaussian/generate-input
```

支持任务：

- 孤立单体 opt/freq/NBO
- TEA 络合 Counterpoise
- 生产性 C=C π-络合物
- 非生产性 O→Ti 毒化络合物
- 插入过渡态
- IRC 本征反应坐标
- 水解/缩合过渡态
- 片段变形能单点

服务器只生成输入文件，不调用 Gaussian16。

## Gaussian 输出解析

```http
POST /api/gaussian/upload-log
POST /api/parse/gaussian-log
```

前端 Gaussian 输出解析页包含两级解析：

- Web Worker 本地预览：用于粘贴大 `.log/.out` 文本时保持界面输入和页面切换流畅。
- 后端正式解析：调用只读 API，输出带单位的 normalized JSON。

解析字段包括：

- 正常终止标记
- SCF 能量
- ZPE、热校正、吉布斯自由能
- 频率、虚频数、最低频率
- HOMO、LUMO、HOMO-LUMO gap
- 偶极矩
- Mulliken / NPA 电荷
- Wiberg 键级片段
- NBO 二阶微扰 E(2)
- Counterpoise corrected energy

解析不到的数据为 `null`，不会补造。

## cube 只读预览导入

```http
POST /api/cube/upload
GET /api/cube/{id}/metadata
POST /api/cubes/upload
GET /api/cubes/{id}/metadata
GET /api/cubes/{id}/isosurface
GET /api/cubes/{id}/slice
POST /api/cubes/difference-density
```

支持 `.cube` / `.cub` 文件头、网格、标量场下采样和剖切预览：

- electron density cube
- ESP cube
- HOMO cube
- LUMO cube
- spin density cube
- difference density cube

当前后端只读解析 cube 文本，不执行 cubegen / Multiwfn。`isosurface` 返回下采样体素点和相位统计，`slice` 返回剖切矩阵，`difference-density` 对两个同网格 cube 做逐点差分预览。完整 marching-cubes 三维等值面重建仍是后续阶段。未上传真实 cube 时，前端显示“未上传真实 cube 文件，当前仅显示示例等值面。”

只读高级解析接口：

```http
POST /api/parse/goodvibes
POST /api/parse/qtaim
POST /api/parse/nci
```

这三个接口只解析文本型 GoodVibes 热化学表、QTAIM BCP 行和 NCI/RDG 区域行。它们不会执行 GoodVibes、Multiwfn、AIMAll 或任何外部程序；面对外部程序输出格式变体时，未识别字段返回缺失提示而不是补造数据。

## Gaussian / cubegen / Multiwfn 示例

项目内置受控外部工具示例：

```text
examples/external-qc/
docs/EXTERNAL_QC_RUN_EXAMPLES.md
scripts/run_external_qc_examples.py
```

只检查示例文件，不执行外部程序：

```bash
npm run examples:external-qc
```

真实运行需要显式传入工具路径和执行开关：

```bash
backend\.venv\Scripts\python.exe scripts\run_external_qc_examples.py --execute-external-tools --gaussian "C:\G16W\g16.exe" --formchk "C:\G16W\formchk.exe" --cubegen "C:\G16W\cubegen.exe" --multiwfn "D:\Multiwfn\Multiwfn.exe"
```

当前环境未检测到这些外部程序，因此本仓库默认不会尝试执行它们。示例输出只用于链路烟测，不能作为真实科研结论。

## 实验-DFT 对照

导入 CSV：

```http
POST /api/experiments/import-csv
GET /api/experiments
```

前端“实验-DFT 对照”页也提供 CSV 粘贴导入控件，会直接调用上述 API。导入记录标注为“用户输入，待核验”。

支持字段：

- 单体 / monomer
- 催化剂体系 / catalyst_system
- 聚合体系 / polymerization
- 聚合温度 / temperature_c
- Al/Ti 比 / al_ti_ratio
- 活性 / activity
- 插入率 / insertion_ratio
- 1-己烯含量 / hexene_content
- 序列长度 / sequence_length
- 熔点、结晶度、透明性

计算相关性：

```http
POST /api/analysis/dft-experiment-correlation
```

系统会给出中文解释，但不会把相关性自动解释为因果结论。

## 可证伪机制模型

```http
POST /api/analysis/mechanism-hypotheses
```

内置假说：

- 位阻主导模型
- 电子效应导向模型
- TEA 预组织模型
- O→Ti 毒化模型
- 链长窗口效应模型
- 乙烯/丙烯差异插入模型

每个模型包含支持证据、反证条件、所需数据、当前数据状态和可信度评分。

## 合并工作台

“合并工作台”用于承载从 `Si-O` 子项目迁入的高级科学计算扩展。合并方式为非破坏式吸收，不覆盖当前中文 V2 主应用。

新增 API：

```http
GET /api/merged/ultra-inventory
POST /api/merged/four-axis-decision
POST /api/merged/radical-kinetics
POST /api/merged/boltzmann-weights
POST /api/merged/wigner-rate
```

已合并能力：

- Wigner 隧穿修正相对速率。
- Boltzmann 构象权重。
- Si–C、Si–O、RO–OR 键离解能公式。
- 四轴机制判据：单体本征、催化剂兼容、后反应加工、微相性能。
- 自由基后反应 RK4 动力学扩展。
- 贝叶斯 TS 搜索指导：GPR 与 Expected Improvement 示例。
- VMC 采样与 block average 统计预览。

已拆解但不直接作为活动页面运行的内容：

- 原 `Si-O/frontend/src` 中的 Three.js、ReactFlow、Yjs 等重型页面已进入 `integrated/origin-frontend`，不会作为第二个 Next 应用运行；后续按页面逐个重构进当前主应用。
- 子项目中的 Ultra / SiC / 自由基主题作为后反应扩展保留，不改写当前 Ziegler–Natta 主机制结论。

合并文档位于：

```text
docs/merged-from-si-o/
docs/MERGE_REPORT.md
docs/INTEGRATION_SOURCE_MAP.md
integrated/origin-frontend/
integrated/origin-backend/
integrated/origin-scripts/
```

拆解整合后的新增根目录 API：

```http
GET /api/integration/source-map
GET /api/integration/gaussian-task-groups
POST /api/integration/build-gaussian-task
POST /api/integration/molecule-intelligence
POST /api/integration/reaction-profile
```

这些接口来自 `Si-O` 子项目拆解后的根目录实现，用于 36 类 Gaussian 模板、分子位点识别和反应能量剖面分析。所有 utility command 只作为文本生成，不会在服务器执行。

## V4 自由基后反应与 Si–C 机理

新增中文页面：

- 自由基后反应
- 过氧化物结构库
- Si–C 键稳定性
- 降解-交联竞争图
- 停留时间窗口
- 乙烯/等规度影响

新增 API：

```http
POST /api/literature/import-polypropylene-radical-review
GET /api/analysis/peroxide-library
POST /api/analysis/peroxide-profile
POST /api/analysis/radical-branching-vs-scission
POST /api/analysis/sic-stability
POST /api/analysis/residence-time-window
POST /api/analysis/unified-lcb-framework
GET /api/analysis/carbonyl-taxonomy
GET /api/analysis/peroxide-experimental-design
```

核心机制链：

```text
RO–OR 均裂 → RO• 抽氢 → PP 大分子自由基 → β-scission 降解 / 自由基复合交联 / 共剂接枝 / 长链支化
```

判据边界：

- 聚丙烯三级 C–H 易抽氢，PP 大分子自由基可发生 β-scission，但平台不会默认判定“必然降解”。
- 共剂、双官能单体、硅烷水解缩合位点和链段接近概率会提高交联/长链支化通道权重。
- 含羰基过氧化物只作为独立机制变量建模；羰基可能影响 O–O BDE、自由基类型、脱羧/氧化副反应和抽氢选择性，但不能直接推出更易交联或更易降解。
- 乙烯引入、等规度和结晶度通过三级 C–H 位点、链段运动和固态扩散共同影响自由基路径。
- 统一有效长链支化效率采用可证伪框架：

```text
ΦLCB = f(χinsert, χhydrolysis, χcondensation, χradical_recombination)
     − f(χβ-scission, χoxidation, χTi_poison, χover-gel)
```

- 羰基必须三分：过氧化物羰基影响自由基类型和分解动力学；接枝单体羰基影响接枝/极性/界面；氧化副产物羰基反映热氧副反应和长期稳定性风险。

文献导入为只读：

```http
POST /api/literature/import-polypropylene-radical-review
```

支持 `.docx`、`.pdf`、`.txt`、`.md`。PDF 解析使用 PyMuPDF 读取页面文本；若是扫描型 PDF 且无可搜索文本，系统返回中文提示，不猜测内容、不执行外部程序。

## 能量公式

- ΔGbind = G(络合物) − ΣG(片段)
- ΔGpoison = G(O→Ti 毒化络合物) − G(C=C π-络合物)
- ΔGπ = G(π-络合物) − G(游离活性中心 + 单体)
- ΔG‡ = G(TS) − G(游离活性中心 + 单体)
- ΔG‡complex = G(TS) − G(π-络合物)
- krel = exp[−ΔΔG‡ / RT]

常数：

- Hartree to kcal/mol = 627.509474
- Hartree to eV = 27.211386245988
- R = 0.00198720425864083 kcal mol-1 K-1
- 默认 T = 350 K

## 报告生成

```http
POST /api/reports/generate
```

支持：

- Markdown
- JSON
- CSV
- Word-compatible HTML
- PDF placeholder

报告章节包括：

- 项目概述
- 论文知识映射
- 分子结构与研究对象
- Si–O 键本征属性
- 电子云密度与静电势分析
- 前线轨道分析
- 电荷布居与电荷转移
- NBO / QTAIM / NCI
- TEA 助催化剂作用
- Ti 活性中心毒化判据
- 插入反应自由能面
- 水解缩合后反应
- 过氧化物自由基机理
- PP β-scission 与交联竞争
- Si–C / Si–O / Si–Cl 后反应差异
- 乙烯引入、等规度与固态反应窗口
- 实验-DFT 对照
- 可证伪机制模型
- 链长效应与电子效应分解
- 文献证据等级与未验证假说
- 数据可靠性说明

## 数据可信度说明

系统明确区分：

- 论文抽取信息：来自 docx 文本，属于文献线索。
- 上传 Gaussian 数据：真实文件解析结果，但仍需检查计算设置和收敛质量。
- 用户手动输入数据：需要用户自行保证来源。
- 示例/mock 数据：仅用于演示，不能作为真实结论。

没有真实数据时，报告会写“当前文件未提供”或“当前仅有示例数据，不能生成真实科学结论”。

## 测试与验证

后端测试：

```bash
npm run test:backend
```

根目录统一命令：

```bash
npm run lint
npm run typecheck
npm test
npm run test:e2e
pytest
pytest --cov
npm run test:coverage
npm run build
```

根目录提供 `pytest.ini` 与 `conftest.py` 兼容入口。从 `D:\codex2_cataSi-O` 直接执行 `pytest` 或 `pytest --cov` 时，会自动使用 `backend/.venv` 中的后端测试环境，避免因为未手动 `cd backend` 或未激活虚拟环境造成 `app` 导入失败。

当前测试覆盖 Gaussian 核心字段、NPA 电荷、Wiberg 片段、NBO E(2)、V2 API、实验 CSV、cube 元数据和机制假说接口。
合并扩展测试覆盖 Ultra 公式、四轴模型、后反应动力学和新增 merged API。
第二轮合并还覆盖自旋多重度、Mulliken 自旋密度、结构化 Wiberg 矩阵和 cube 数据范围预览。
V4 测试覆盖过氧化物半衰期窗口、RO–OR/Si–C BDE 边界、PP β-scission 与支化竞争、含羰基过氧化物解释边界和新增 API。
Pro Max Ultra 扩展测试还覆盖 GoodVibes/QTAIM/NCI 只读 parser、MCP 安全白名单工作流、实验表征导入占位接口和数据库扩展表。

前端类型检查：

```bash
npm run typecheck:frontend
```

前端 lint：

```bash
npm --prefix frontend run lint
```

前端构建：

```bash
npm --prefix frontend run build
```

根目录质量门禁：

```bash
python scripts/quality_gate.py
```

全功能 API 烟测：

```bash
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
```

数理严谨性审计：

```bash
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
```

该脚本自动检查单位常数、自由能公式、ΔGpoison 判据、krel 温度行为、Gaussian parser、中文错误路径、mock/example 数据边界，并生成：

```text
docs/SCIENTIFIC_RIGOR_TEST_REPORT.md
```

Pro Max Ultra 总审计：

```bash
npm run test:ultra
```

该脚本自动检查科学公式、Gaussian/cube/GoodVibes/QTAIM/NCI parser、V4 DOCX 只读抽取、核心 API、MCP 安全工作流、中文错误提示、数据库表、安全边界和性能哨兵；真实大体数据渲染与更大外部输出格式适配仍在报告中列为风险。报告输出到：

```text
TEST_REPORT.md
docs/ULTRA_QUALITY_TEST_REPORT.md
```

UI smoke 检查需要先启动前端和后端：

```bash
npm run dev:backend
npm run dev
npm run test:ui-smoke
```

`scripts\ui_smoke_check.mjs` 会检查前端首页、后端健康接口和 OpenAPI 文档；根目录已固定 Playwright，随后自动执行浏览器流程：全导航抽样、Gaussian 输出解析、粘贴 sample Gaussian log、点击解析文件、上传 cube 并检查真实下采样预览、切换到合并工作台运行四轴判据与后反应动力学按钮、巡检 MCP 安全工作流，并在 390px 宽度检查移动端横向溢出。

本轮全方位测试报告：

```text
docs/FULL_FUNCTION_TEST_REPORT.md
docs/UI_UX_TEST_REPORT.md
docs/test-screenshots/
```

MCP 安全工作流：

```http
GET /api/mcp/tools
GET /api/mcp/resources
POST /api/mcp/generate-prompt
POST /api/mcp/run-tool
GET /api/research/top-scientist-protocol
POST /api/research/top-scientist-prompt
POST /api/literature/import-report-docx
GET /api/literature/report-knowledge
```

前端左侧导航提供“MCP 自动化工作流”页面。`run-tool` 仅允许平台内置白名单工具，例如 Gaussian 输入模板文本生成、Gaussian 文本解析、cube 文本解析、ΔGbind/ΔGpoison/Si–C BDE 计算、文件名安全校验、过氧化物画像、中文科研 prompt 生成和“顶尖科学家能力进化 Prompt”生成；不提供 shell 命令执行入口。

“顶尖科学家能力进化协议”已内置为受控研究协议，包含：

- 研究总对象：DCS、MCSOMe、DMOS、Ziegler–Natta/TEA 催化体系、PP/iPP/PPR/IPC/EPC/LCB-IPC 和 DCP/BPO/TBPB/L-101/TBPEH 自由基体系。
- 四轴机制模型：单体轴、催化剂轴、自由基轴、微相轴。
- A/B/C/D 证据等级系统：真实计算、真实实验、文献/用户输入、示例/推断分层。
- 20 类量子化学任务：opt/freq/NBO、29Si GIAO、TEA counterpoise、Ti π-complex、O→Ti、TS/IRC、BDE、自由基反应、cube/Multiwfn 脚本。
- 波函数与电子结构分析要求：ρ(r)、HOMO/LUMO、ESP、NBO、QTAIM、NCI/RDG。
- 过氧化物羰基三分法和 DCP/BPO/TBPB/L-101/TBPEH/DTBP 比较维度。
- GPC/MFR、gel、SAOS、FTIR、NMR、DSC/XRD、TEM/SEM/AFM、介电谱的实验表征映射。
- 最小可证伪任务模板：最小 Gaussian 任务、最小实验任务、最小软件任务。
- 软件化执行映射：API、normalized JSON、decision-engine、实验数据表、中文报告章节。
- 报告驱动闭环扩展：`SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿` 类 docx 只读导入后，抽取 Si–O/Si–C、TEA/Ti、过氧化物、PP β-scission、LCB、羰基三分法、乙烯/等规度/结晶度等 C 级报告线索，并映射到 UI、API、测试与报告章节。

报告生成新增“证据等级系统”“最小可证伪任务”“软件化执行映射”“软件化执行接口”“研究对象与四轴机制协议”“Si–C 连接稳定性”“羰基三分法”“乙烯/等规度/结晶度影响”“量子化学任务设计要求”“波函数与电子结构分析要求”“过氧化物比较维度”“实验表征逻辑”“顶尖 PI 工作标准”等章节；没有真实数据时仍按 C/D 级假说处理，不能输出确定性论文结论。

### 报告 docx 知识导入

```http
POST /api/literature/import-report-docx
GET /api/literature/report-knowledge
```

`import-report-docx` 默认面向：

```text
C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx
```

导入流程只读取 docx XML 文本，不执行宏、脚本、Gaussian、cubegen 或 Multiwfn。抽取结果统一标注：

- `evidence_level = C`
- `data_source = 报告线索`
- `paper_ready = 需要补充验证`
- `provenance = 报告 docx 只读抽取`

前端“论文知识库”会显示报告驱动知识映射和 C 级证据卡片；“MCP 自动化工作流”会显示报告证据闭环和对应软件接口。

### OCR 文本与真实文件实例

```http
POST /api/literature/import-ocr-text
GET /api/literature/source-quality
GET /api/literature/real-instance-summary
```

`import-ocr-text` 只接收用户粘贴或上传得到的 OCR 文本，服务器不执行 OCR 程序。OCR 文本按用户输入处理，证据等级固定为 C，用于修复 PDF 文本层乱码导致的关键词统计失真。

PDF 解析质量使用四类标签：

- `readable`：文本层可读，但仍只是 C 级文献线索。
- `encoded-garbled`：PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；建议提供 OCR 文本或可复制文本版 PDF。
- `scanned-needs-ocr`：扫描型 PDF 或无可搜索文本，需要用户提供 OCR 文本。
- `failed`：解析失败，不能抽取实体或关键词。

`real-instance-summary` 汇总当前真实文件实例：博士论文 docx、张志箭 PDF、PP 自由基综述 PDF 和 SiO/SiC/PP 报告 docx，并在中文报告“真实文件实例测试”章节中说明解析质量、warnings、关键词统计、C 级证据边界和是否可写入论文结论。

## 安全边界

- 默认不执行任意 shell 命令。
- 默认不调用、不执行 Gaussian16。
- 默认不执行 cubegen。
- 默认不执行 Multiwfn。
- Gaussian16 路径必须由用户在系统设置中显式配置。
- 上传文件只按文本或数据解析。
- 解析器只读文件，不执行文件。
- 示例数据始终标注 MOCK / EXAMPLE。

## Google Workspace 式 UI 逻辑

前端已按 Google 系列产品的交互逻辑重组：

- 左侧导航按“首页 / 知识库 / 分子与结构 / 量子计算 / 机理分析 / 实验闭环 / 报告 / 自动化”分组，可折叠并保留当前模块高亮。
- 顶部栏提供当前项目/模块、全局搜索入口，搜索框占位为“搜索分子、任务、报告、证据…”，右侧显示数据源状态、当前分子选择、主题与设置入口。
- 文献知识库采用 Google Drive 风格资源表格：真实文件实例、解析质量、C级证据、warnings 和 OCR 文本导入集中显示，右侧详情面板解释 provenance 与论文结论边界。
- 分子库采用 Drive + scientific viewer 三栏结构：左侧“分子资源表”，中间“结构视图”，右侧“分子详情 / provenance”，方便按资源行查看功能位点、证据等级和示例数据边界。
- Gaussian 输入生成采用 Colab/Docs 风格工作台：左侧任务模板，中间参数表单，右侧输入文件预览，并始终提示“不执行 Gaussian，仅生成输入文件”。
- Gaussian 输出解析采用 Cloud Log Viewer 风格：日志输入、normalized JSON、解析质量/证据来源三栏组织，并明确“仅读取，不执行 Gaussian”。
- 报告页采用 Google Docs 风格：左侧章节大纲，中间报告预览，右侧“证据与数据来源”面板，导出中心统一显示格式与数据可靠性提醒。
- MCP 自动化工作流采用 Cloud Console 工具页：工具列表、工具详情、输入 schema、运行结果、安全边界和 Prompt 生成器在同一工作区内完成。
- 数据管理页采用 Drive 资源管理逻辑：上传区、资源表、数据源详情和 provenance 审计分区显示，所有解析入口都明确“仅读取，不执行文件”。
- 实验-DFT 对照页采用 Sheets 风格：实验记录资源表、实验记录来源面板、活性-势垒散点图、链长趋势图和电子/位阻二维机制图统一呈现。
- 量子判据引擎页清除了历史乱码，改为判据资源表、候选热图、证据与结论边界和中文论文式结论模板。

## 后续计划

- 真实 3Dmol cube 等值面渲染。
- Multiwfn 结构化导入、GoodVibes 真实格式样本扩展和 NBO 高级导入。
- 批量 Gaussian 任务图与 SLURM 脚本生成。
- 构象族 Boltzmann 权重和熵校正。
- 论文全文章节级知识抽取与表格定位。
- PostgreSQL 迁移与多项目协作。
