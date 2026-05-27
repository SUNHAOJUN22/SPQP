# Si-O 子项目合并报告

## 合并目标

本次合并在现有根项目 `D:\codex2_cataSi-O` 基础上进行。第三轮已把原独立 `Si-O` 子目录拆解为根项目 `integrated/origin-*` 分类资产，并移除独立 `Si-O` 文件夹。合并策略是“拆解后吸收”：把子项目中可复用的科学计算核心、判据模型、动力学扩展、文档资产和源代码库存纳入根项目，同时避免把不兼容的页面树直接作为第二个应用运行。

## 已合并内容

### 后端科学核心

新增 `backend/app/services/ultra_science.py`，吸收并适配以下能力：

- Hartree / kcal/mol / eV 换算。
- ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔGproduct 公式。
- Wigner 隧穿修正相对速率。
- Boltzmann 构象权重。
- Si–C、Si–O、RO–OR 键离解能扩展公式。
- 四轴机制判据：单体本征、催化剂兼容、后反应加工、微相性能。
- 自由基后反应 RK4 动力学扩展。

第二轮拆解后新增：

- `backend/app/services/advanced_gaussian_builder.py`：36 类 Gaussian / utility 任务模板。
- `backend/app/services/integrated_science.py`：反应能量剖面、Boltzmann 权重和势垒识别。
- `backend/app/services/molecule_intelligence.py`：RDKit 分子位点识别、分子图和 XYZ 输出。

### API

新增接口：

- `GET /api/merged/ultra-inventory`
- `POST /api/merged/four-axis-decision`
- `POST /api/merged/radical-kinetics`
- `POST /api/merged/boltzmann-weights`
- `POST /api/merged/wigner-rate`

这些接口均不执行 Gaussian，不执行任意 shell 命令，只基于用户传入数值或示例输入计算。

### 前端

新增中文页面“合并工作台”，入口位于左侧导航栏。该页面提供：

- 合并资产清单。
- 四轴机制雷达图。
- 后反应动力学曲线。
- 贝叶斯 TS 搜索指导预览。
- VMC 采样与 block average 统计预览。
- 合并边界与未直接合并项说明。
- 数据可靠性提示。

新增 `frontend/lib/advanced-science.ts`，吸收并中文化子项目中不依赖重型 UI 包的 TypeScript 科学工具，包括 Eyring 速率、选择性、GPR/Expected Improvement 和 VMC 统计预览。

第三轮新增“整合总控台”，作为默认首页展示 V3 整合状态、拆解资产分布、Gaussian 任务宇宙和根目录活动规则。

### 文件解析增强

根项目 Gaussian parser 已补充：

- 自旋多重度。
- Mulliken 原子自旋密度。
- 结构化 Wiberg bond index matrix。

cube 元数据解析已补充：

- 原子行列表。
- 体数据数值范围快速预览，包括 min、max、mean 和采样数量。

### 文档

已将子项目文档复制到 `docs/merged-from-si-o/`：

- `PHYSICAL_MODELS.md`
- `FUNCTION_MATRIX.md`
- `OPTIMIZATION_ROADMAP.md`
- `TESTING_STRATEGY.md`
- `UNIT_SYSTEM.md`
- `LEGACY_TEST_REPORT.md`
- `LEGACY_CHANGELOG.md`
- `assets/SiO_Catalyst_Software_Copyright_Details.pdf`
- `assets/success.png`
- `deployment/Dockerfile.legacy`
- `deployment/nginx.legacy.conf`

新增 `docs/INTEGRATION_SOURCE_MAP.md` 作为拆解迁移索引。

原 `Si-O` 目录已拆解到：

- `integrated/origin-frontend`
- `integrated/origin-backend`
- `integrated/origin-docs`
- `integrated/origin-scripts`
- `integrated/origin-deployment`
- `integrated/origin-assets`

## 未直接合并内容

原前端页面树已进入 `integrated/origin-frontend`，不再作为独立应用运行。Three.js、ReactFlow、Yjs、Playwright 等较重依赖会在后续逐页重构时适配到当前 Next.js 16 / React 19 主应用，避免破坏生产构建。

子项目中部分 Ultra / SiC / 自由基后反应内容属于扩展研究线，不改写当前平台的 Ziegler–Natta / TEA / Ti 毒化主机制结论。

## 后续建议

1. 将子项目的 Three.js 分子与轨道等值面视图拆成独立适配包，逐个迁入根项目。
2. 把 Bayesian / QMC / WebGPU 原型转为独立“高级计算扩展”模块，避免影响主线构建。
3. 为四轴模型增加真实上传数据绑定，禁止仅凭示例输入生成确定性排序。
4. 为动力学扩展增加参数来源记录，区分实验拟合、文献引用和用户假设。
5. 将 `docs/merged-from-si-o` 中的单位体系和物理模型整理进中文用户手册。
