# 根工作目录整合源图

## 当前规则

后续开发、启动、测试和构建都在根目录 `D:\codex2_cataSi-O` 下进行。独立 `Si-O` 子目录已拆解并移除，不再作为运行入口。

## 已拆解并迁入根项目

### 后端

| 来源 | 迁入位置 | 用途 |
| --- | --- | --- |
| `Si-O/backend/app/core/builder.py` | `backend/app/services/advanced_gaussian_builder.py` | 36 类 Gaussian / utility 模板，只生成文本，不执行命令 |
| `Si-O/backend/app/core/energy_engine.py` | `backend/app/services/integrated_science.py` | 反应能量剖面、Boltzmann 权重、势垒提取 |
| `Si-O/backend/app/core/molecule_intel.py` | `backend/app/services/molecule_intelligence.py` | RDKit 分子位点识别与分子图 |
| `Si-O/backend/app/core/conversions.py`、`decision.py`、`kinetics.py` | `backend/app/services/ultra_science.py` | Ultra 公式、四轴判据、后反应动力学 |

新增 API：

- `GET /api/integration/source-map`
- `GET /api/integration/gaussian-task-groups`
- `POST /api/integration/build-gaussian-task`
- `POST /api/integration/molecule-intelligence`
- `POST /api/integration/reaction-profile`
- `GET /api/merged/ultra-inventory`
- `POST /api/merged/four-axis-decision`
- `POST /api/merged/radical-kinetics`
- `POST /api/merged/boltzmann-weights`
- `POST /api/merged/wigner-rate`

### 前端

| 来源 | 迁入位置 | 用途 |
| --- | --- | --- |
| `Si-O/frontend/src/utils/physics.ts`、`bayesian.ts`、`qmc.ts` | `frontend/lib/advanced-science.ts` | 轻量科学公式、GPR / EI、VMC 预览 |
| `Si-O/frontend/src/data/catalystDatabase.ts` | `frontend/lib/integrated-catalyst-database.ts` | 催化剂示例数据库 |
| 多个子项目可视化思路 | `frontend/components/modules/merged-ultra-panel.tsx` | 合并工作台中文 UI |
| 子项目整体前端源码 | `integrated/origin-frontend/` | 分类保留，用于后续逐页重构，不作为独立 Next 应用运行 |

### 文档与资产

| 来源 | 迁入位置 |
| --- | --- |
| `Si-O/docs/*`、`Si-O/PHYSICAL_MODELS.md`、`Si-O/TEST_REPORT.md` | `docs/merged-from-si-o/` |
| `Si-O/SiO_Catalyst_Software_Copyright_Details.pdf`、`Si-O/success.png` | `docs/merged-from-si-o/assets/` |
| `Si-O/Dockerfile`、`nginx.conf`、`Makefile`、`docker-compose.yml` | `docs/merged-from-si-o/deployment/` |
| `Si-O/scripts/quality-gate.py` | `scripts/quality_gate.py`，并改写为根项目命令 |
| 子项目完整剩余资产 | `integrated/origin-assets`、`integrated/origin-docs`、`integrated/origin-scripts`、`integrated/origin-deployment` | 拆解归档 |

## 未直接迁入

以下内容不直接迁入活动代码路径：

- WebGPU、Yjs、ReactFlow、Three.js 大型交互模块：需要单独适配依赖后再迁入。
- 自动修复脚本：多数为一次性修复旧项目语法/编码问题，不应进入当前生产路径。

## 数据可靠性

迁入的示例数据库、VMC 预览、贝叶斯 TS 指导均为示例或算法演示。真实科研结论必须来自上传 Gaussian 输出、用户核验实验数据或论文抽取证据。
