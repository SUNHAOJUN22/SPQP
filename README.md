# 硅氧硅碳催化量子机理平台 Pro Max Ultra

SiO-SiC Polyolefin Quantum Mechanism Studio Ultra

[简体中文](README.md) | [English](README.en.md)

中文科研计算平台，用于聚烯烃功能化、Ziegler-Natta 催化、Si-O / Si-C 键物理化学属性、Gaussian 后处理、过氧化物自由基反应和 PP 长链支化-交联-降解竞争机制研究。

## Overview

本项目是一个全栈科研软件原型，面向中文科研用户提供“数据导入、计算模板、只读解析、机制判据、证据分级、报告生成”的一体化工作流。

平台关注以下研究线：

- 功能 alpha-烯烃单体：DCS、MCSOMe、DMOS 及相关 Si-Cl、Si-OMe、Si-O、Si-C 结构。
- 配位插入机理：Ziegler-Natta 活性中心、TEA 助催化剂、Al-O / Al-Cl / Al-C=C 相互作用、Ti 毒化、C=C 插入过渡态。
- 后反应机理：Si-Cl / Si-OMe 水解、Si-O-Si 缩合、Si-C 连接稳定性。
- 自由基后改性：过氧化物 RO-OR 均裂、PP 叔碳抽氢、beta-scission、自由基复合、接枝、轻度交联、过凝胶和氧化羰基副反应。
- 实验闭环：GPC、MFR、gel、SAOS、FTIR、NMR、DSC、介电谱等实验结果与 DFT 描述符对照。

本项目默认不执行任何外部量子化学或波函数分析程序。Gaussian、cubegen、Multiwfn、GoodVibes 相关能力均以“输入生成、命令模板、文本解析、报告草稿”为边界。

## Product Scope

平台当前覆盖以下产品能力。

- 中文科研工作台：Google Workspace / Google Cloud 风格的信息架构，包含分组导航、全局搜索、资源表格、右侧详情面板和报告预览。
- 分子与结构管理：内置 DCS、MCSOMe、DMOS、ethylene、propylene、1-hexene、TEA、PP / EPC 小模型和过氧化物示例。
- Gaussian 输入生成：生成 opt/freq/NBO、TEA complex、Ti pi-complex、O-to-Ti poison complex、insertion TS、IRC、hydrolysis、condensation、BDE 和自由基反应模板。
- Gaussian 输出解析：只读解析 log/out 文本中的 SCF、Gibbs、ZPE、频率、虚频、HOMO / LUMO、偶极矩、电荷、Wiberg、NBO E(2)、Counterpoise 等字段。
- cube 文件解析：只读解析 density、ESP、HOMO、LUMO、spin density 和 difference density 的网格元数据、切片和下采样预览。
- 科学计算核心：统一实现能量换算、Delta G 公式、BDE、相对速率、自由基竞争和 Boltzmann 权重。
- 机制判据引擎：输出 Ti 毒化、TEA 预组织、Si-O 削弱、Si-C 风险、PP 降解、LCB、过凝胶和氧化风险解释。
- 文献与报告知识库：只读导入 docx、PDF 文本层或 OCR 文本，抽取报告线索并固定标注为 C 级证据。
- 中文科研报告：生成带数据来源、证据等级、缺失数据声明和 mock 数据边界的报告。

## Architecture

项目采用前后端分离架构。

```text
frontend/        Next.js, React, TypeScript, TailwindCSS
backend/         FastAPI, Pydantic, SQLAlchemy, SQLite
scripts/         quality gates, smoke tests, parser audits
docs/            scientific workflow, test reports, integration reports
examples/        controlled examples and non-executed external QC templates
integrated/      archived source assets from earlier Si-O subproject integration
```

核心分层原则：

- scientific core：集中保存单位常数、能量公式、BDE、动力学和判据，避免公式散落。
- parsers：只读解析 Gaussian、cube、NBO、QTAIM、NCI、GoodVibes 等文本输出，不执行外部文件。
- API：通过 FastAPI 提供分子、Gaussian、cube、analysis、literature、reports、MCP 安全工作流接口。
- UI：以资源表、工作台、详情面板和报告预览组织科研操作。
- reports：把计算、文献、实验、示例数据分别标注来源和可信度。

## Scientific Rules

所有科学输出必须保留数据来源、单位、温度、方法、基组、provenance、evidence grade 和 is_mock 字段。

证据等级：

- A 级：真实 Gaussian、Multiwfn、NBO、QTAIM 或 NCI 计算结果，且收敛、频率、TS 虚频、IRC 和 provenance 完整。
- B 级：真实实验数据，样品、工艺和表征条件明确。
- C 级：文献线索或用户输入，尚未在当前体系复现。
- D 级：示例数据、mock 数据或趋势假说，不能作为真实科研结论。

没有 A / B 级数据时，报告必须写明当前数据不足，不能形成可靠结论。

## Scientific Formulas

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
Delta Gddagger_insert = G(insertion TS) - G(free active site + monomer)
Delta Gddagger_complex = G(insertion TS) - G(pi-complex)
Delta Delta Gddagger = Delta Gddagger_candidate - Delta Gddagger_reference
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

## Requirements

推荐环境：

- Node.js 20 或更高版本
- Python 3.11 或更高版本
- Windows PowerShell、Git Bash、macOS shell 或 Linux shell
- SQLite 用于 MVP 本地数据

可选依赖：

- RDKit：用于分子描述符和构象生成。如果不可用，平台会使用明确标注的降级描述符。
- PyMuPDF / python-docx：用于只读文献抽取。
- Gaussian、cubegen、Multiwfn、GoodVibes：默认不执行，仅在用户显式配置并单独确认的外部流程中作为模板对象。

## Installation

安装根目录和前端依赖：

```bash
npm install
npm --prefix frontend install
```

创建后端虚拟环境并安装依赖：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

返回项目根目录：

```bash
cd ..
```

## Run

启动后端：

```bash
npm run dev:backend
```

启动前端：

```bash
npm run dev
```

默认访问地址：

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs

## Validation

后端测试：

```bash
npm run test:backend
```

前端类型检查、lint 和构建：

```bash
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

中文乱码审计：

```bash
npm run audit:mojibake
```

数理严谨性审计：

```bash
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
```

全功能 API smoke test：

```bash
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
```

根目录质量门禁：

```bash
python scripts\quality_gate.py
```

UI smoke test 需要先启动前端和后端：

```bash
npm run dev:backend
npm run dev
npm run test:e2e
```

## Security Boundary

默认禁止：

- 执行 Gaussian16。
- 执行 cubegen。
- 执行 Multiwfn。
- 执行 GoodVibes。
- 执行用户上传文件。
- 将示例数据、mock 数据、文献线索自动升级为真实科研结论。

默认允许：

- 生成 Gaussian 输入文件。
- 生成 cubegen、Multiwfn、GoodVibes 命令模板，并标注未执行。
- 只读解析 Gaussian log/out、cube、NBO、QTAIM、NCI、GoodVibes 文本输出。
- 生成中文报告草稿。
- 对用户输入数据进行公式计算和机制判据评估。

## Documentation

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

## Repository Status

当前仓库为研究软件工程版本，适合用于本地开发、科研演示、机制判据验证和后续工程化迭代。

生产部署前建议补充：

- 正式 LICENSE 文件。
- 环境变量模板。
- 数据库迁移策略。
- 用户权限与项目隔离策略。
- 更大规模真实 Gaussian、cube、NBO、QTAIM、NCI 输出样本的兼容性测试。
- 持续集成工作流。

## Roadmap

- 真实 3Dmol / vtk.js cube 等值面渲染。
- Multiwfn 结构化导入和 NBO 高级解析。
- GoodVibes 真实格式样本扩展。
- 批量 Gaussian 任务图、SLURM 脚本和任务队列。
- 构象族 Boltzmann 权重、熵校正和 GoodVibes 汇总。
- 论文全文章节级知识抽取与表格定位。
- PostgreSQL 多项目协作版本。

## Citation and Use

本仓库面向科研软件开发和机制建模验证。由示例数据得到的趋势仅用于验证软件逻辑，不能作为论文结论、专利结论或工程决策依据。真实科学结论必须来自可追溯的 A 级计算数据或 B 级实验数据，并经过人工审查。
