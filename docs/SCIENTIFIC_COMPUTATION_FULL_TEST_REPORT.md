# 全面科学计算测试与专业数据报告

## 1. 测试时间

- 测试时间：2026-05-27 12:30:07 +08:00
- 项目根目录：`D:\codex2_cataSi-O`
- 测试类型：全面科学计算测试、数理严谨性审计、API smoke、UI smoke、质量门禁、中文乱码审计

## 2. 测试环境

| 项目 | 环境 |
| --- | --- |
| 操作系统 | Windows / PowerShell |
| 后端 | FastAPI / Python 3.11+ / pytest |
| 前端 | Next.js / React / TypeScript strict / ESLint / Playwright |
| 数据库 | 本地 SQLite MVP |
| 测试入口 | `npm` scripts、FastAPI TestClient、Playwright |
| 科研边界 | 只生成模板、只读解析、只调用本地 API |

## 3. 安全边界声明

本次测试未执行 Gaussian、cubegen、Multiwfn、GoodVibes 或用户上传文件。所有由示例数据得到的趋势仅用于验证软件逻辑，不能作为真实科学结论。

已确认：

- Gaussian 输入生成只生成文本模板。
- Gaussian/cube/GoodVibes/QTAIM/NCI parser 只读解析文本。
- MCP 工具执行走白名单，不提供 shell 执行入口。
- mock/example 数据保留 `is_mock`、source、evidence grade 或可靠性声明。
- 没有真实 A/B 级数据时，报告必须写“当前数据不足，不能形成可靠结论。”

## 4. 执行命令清单

| 顺序 | 命令 | 结果 |
| ---: | --- | --- |
| 1 | `npm run test:backend` | PASS，70 passed |
| 2 | `backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py` | PASS，报告已写入 `docs/SCIENTIFIC_RIGOR_TEST_REPORT.md` |
| 3 | `backend\.venv\Scripts\python.exe scripts\full_function_smoke.py` | PASS，全功能 API smoke 通过 |
| 4 | `npm run audit:mojibake` | PASS，活动文件乱码 0 行 |
| 5 | `npm --prefix frontend run typecheck` | PASS |
| 6 | `npm --prefix frontend run lint` | PASS |
| 7 | `npm --prefix frontend run build` | PASS |
| 8 | `npm run test:e2e` | PASS，Playwright UI smoke 通过 |
| 9 | `python scripts\quality_gate.py` | PASS，质量门禁通过 |

## 5. 科学公式核查表

| 公式 | 测试状态 | 说明 |
| --- | --- | --- |
| `ΔGbind = G(complex) - ΣG(fragments)` | PASS | `-0.025 Hartree = -15.6877 kcal/mol` |
| `ΔGpoison = G(O→Ti) - G(C=C π-complex)` | PASS | 示例输出 `6.275095 kcal/mol`，判为生产性 C=C 插入占优 |
| `ΔGπ = G(π-complex) - G(free site + monomer)` | PASS | 插入剖面自动计算 |
| `ΔG‡insert = G(TS) - G(free site + monomer)` | PASS | 插入剖面自动计算 |
| `ΔG‡complex = G(TS) - G(π-complex)` | PASS | 插入剖面自动计算 |
| `ΔGproduct = G(product) - G(free site + monomer)` | PASS | 插入剖面自动计算 |
| `ΔΔG‡ = ΔG‡candidate - ΔG‡reference` | PASS | 速率比较中自动计算 |
| `krel = exp[-ΔΔG‡ / RT]` | PASS | `ΔΔG‡=0` 时 `krel=1`，正负能垒符号行为正确 |
| Boltzmann 权重 | PASS | `/api/merged/boltzmann-weights` 已通过 smoke |

## 6. 单位换算核查表

| 常数 | 期望值 | 测试状态 |
| --- | ---: | --- |
| Hartree to kcal/mol | `627.509474` | PASS |
| Hartree to eV | `27.211386245988` | PASS |
| Hartree to kJ/mol | `2625.499638` | PASS，协议与文档锁定 |
| `R` | `0.00198720425864083 kcal mol^-1 K^-1` | PASS |
| 默认温度 | `350 K` | PASS |

## 7. BDE 核查表

| BDE 类型 | 公式 | 测试状态 | 证据边界 |
| --- | --- | --- | --- |
| Si-C | `BDE(Si-C) = G(R•) + G(•Si fragment) - G(R-Si)` | PASS | 仅验证公式与单位，真实结论需真实片段输出 |
| Si-O | `BDE(Si-O) = G(R•) + G(•O-Si fragment) - G(R-O-Si)` | PASS | 需核验频率、自旋多重度、provenance |
| Si-Cl | `BDE(Si-Cl) = ΣG(fragments) - G(parent)` | PASS，API 支持 | 水解路径不能只靠均裂 BDE 判断 |
| RO-OR | `BDE(RO-OR) = G(2RO•) - G(RO-OR)` | PASS | 半衰期、温度和自由基副产物仍需实测或真实计算 |

## 8. 自由基动力学核查表

| 项目 | 测试状态 | 说明 |
| --- | --- | --- |
| `R_scission = kβ[PP•]` | PASS | 自由基竞争模型和 API smoke 覆盖 |
| `R_branch = krec[PP•]^2 + kg[PP•][M] + kc[PP•][coagent]` | PASS | `/api/analysis/radical-kinetics` 与 `/api/merged/radical-kinetics` 可调用 |
| `S_LCB = R_branch / (R_branch + R_scission + R_oxidation)` | PASS | V4 统一 LCB 框架已通过 smoke |
| β-scission / branching / oxidation 竞争 | PASS | `radical-beta-scission`、`peroxide-selection`、`unified-lcb-framework` 均通过 |

## 9. Gaussian Parser 核查结果

| 字段 | 状态 |
| --- | --- |
| normal termination / error termination | PASS |
| SCF energy / Gibbs free energy / ZPE / thermal corrections | PASS |
| frequencies / imaginary frequency count / lowest frequency | PASS |
| HOMO / LUMO / gap eV | PASS |
| dipole / Mulliken charges / NPA charges | PASS |
| Wiberg bond index / NBO E(2) | PASS |
| Counterpoise energy | PASS |
| missing fields = null | PASS |
| quality = complete / partial / failed | PASS |
| 中文 warnings | PASS |

错误路径：空 Gaussian log 返回 failed，不伪造 Gibbs、NBO 或正常终止标记。

## 10. cube Parser 核查结果

| 项目 | 状态 |
| --- | --- |
| valid cube | PASS |
| invalid / malformed cube | PASS，返回中文错误 |
| origin / grid vectors / dimensions | PASS |
| atom list / scalar field shape | PASS |
| min / max value | PASS |
| downsample | PASS |
| slice | PASS |
| isosurface metadata | PASS |
| difference density preview | PASS |

限制：当前支持元数据、下采样体素、剖切矩阵和差分预览；完整 marching-cubes / Three.js 三维等值面重建仍列为剩余风险。

## 11. NBO / QTAIM / NCI Parser 核查结果

| Parser | 核查字段 | 状态 |
| --- | --- | --- |
| NBO | NBO E(2)、Wiberg、NPA、donor-acceptor 字段 | PASS，Gaussian parser 和 rigor 测试覆盖 |
| QTAIM | BCP pair、rho、laplacian、H | PASS，轻量文本 parser 通过 |
| NCI | sign(lambda2)rho、RDG、blue attractive 分类 | PASS，轻量文本 parser 通过 |
| GoodVibes | 输出条目解析 | PASS |

限制：大型真实 NBO/QTAIM/NCI 输出格式仍需要继续用真实样本扩展 parser 适配矩阵。

## 12. API 测试矩阵

| API 类别 | 代表接口 | 状态 |
| --- | --- | --- |
| 健康检查 | `GET /api/health` | PASS |
| 科学任务矩阵 | `GET /api/scientific-computation/task-matrix` | PASS |
| 能量工作台 | `POST /api/scientific-computation/energy-workbench` | PASS |
| 能量组分 | `POST /api/analysis/energy-components` | PASS |
| TEA 结合 | `POST /api/analysis/tea-binding` | PASS |
| Ti 毒化 | `POST /api/analysis/ti-poisoning` | PASS |
| 插入路径 | `POST /api/analysis/insertion-profile` | PASS |
| BDE | `POST /api/analysis/bde` | PASS |
| Si-O / Si-C | `POST /api/analysis/sio-bond`、`/sic-bond` | PASS |
| 水解缩合 | `POST /api/analysis/hydrolysis-condensation` | PASS |
| 自由基 | `POST /api/analysis/radical-beta-scission`、`/radical-kinetics` | PASS |
| parser | Gaussian / GoodVibes / QTAIM / NCI | PASS |
| cube | upload / metadata / slice / isosurface | PASS |
| report | `POST /api/reports/generate` | PASS |

## 13. UI 测试矩阵

| 页面 / 流程 | 检查项 | 状态 |
| --- | --- | --- |
| 科学计算工作流 | 计算任务矩阵、能量公式工作台、BDE 计算 | PASS |
| 科学计算交互 | 点击“计算自由能差”后出现 ΔGbind / ΔGpoison | PASS |
| Gaussian 输出解析 | 仅读取、不执行 Gaussian、normalized JSON、解析质量 | PASS |
| cube 页面 | sample cube 上传、真实下采样预览 | PASS |
| 报告生成 | 章节大纲、报告预览、证据与数据来源 | PASS |
| MCP 工作流 | 工具列表、输入 schema、运行结果、安全边界 | PASS |
| 移动端 | 390px 无横向溢出 | PASS |
| 控制台 | 无 console error | PASS |

## 14. 错误路径测试矩阵

| 错误路径 | 状态 | 说明 |
| --- | --- | --- |
| 缺少 Gibbs 自由能 | PASS | parser warnings / failed quality |
| 缺少 π-complex | PASS | 422 或中文 warning |
| 缺少 O->Ti complex | PASS | 422 或中文 warning |
| 缺少 TS 自由能 | PASS | 422 或中文 warning |
| 空 Gaussian log | PASS | failed，不伪造数据 |
| 非法文件类型 | PASS | 400 中文错误 |
| malformed cube | PASS | 400 中文错误 |
| mock 数据报告 | PASS | 报告含可靠性声明 |
| C/D 级证据升级防护 | PASS | 报告与 API 保留 evidence/mock 边界 |

## 15. mock/example 数据边界

已确认：

- mock 判据矩阵来源明确。
- mock 报告包含“示例数据，不能作为真实结论”或等价可靠性声明。
- 任务模板、命令模板、示例能量不自动生成 A/B 级结论。
- 没有真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 或真实实验数据时，系统仅能输出方法演示、C/D 级线索或下一步验证任务。

## 16. 证据等级统计

| 证据等级 | 数量 / 状态 | 说明 |
| --- | --- | --- |
| A 级真实计算数据 | 0 | 本轮未执行 Gaussian/Multiwfn/NBO/QTAIM/NCI，也未导入可判定为 A 级的新真实计算结果 |
| B 级真实实验数据 | 0 | 本轮未导入真实实验表征数据 |
| C 级文献/用户输入 | 已覆盖 | 文献 DOCX/PDF/OCR 与用户输入能量均作为 C 级线索处理 |
| D 级示例/mock | 已覆盖 | smoke、UI、报告中的示例数据均保留 mock/example 边界 |

## 17. 可作为论文结论的结果

当前没有新增 A/B 级真实数据，因此本次测试结果本身不能作为化学机理或材料性能的论文结论。

可以作为论文或软件方法章节依据的是：

- 公式实现、单位换算和判据边界通过自动化测试。
- parser 的只读解析与缺失字段处理策略可复现。
- 平台安全边界、provenance、evidence grade 和 mock 边界可审计。
- 科学计算工作流可以作为“计算与数据处理平台”的软件验证结果。

## 18. 不能作为论文结论的结果

以下内容不能作为真实科学结论：

- 示例 ΔGpoison、ΔGbind、BDE、krel 数值。
- mock 候选排序。
- 由 sample Gaussian log / sample cube 得到的解析演示。
- 未执行的 Gaussian/cubegen/Multiwfn 命令模板。
- C 级文献线索在未复现前不能写成 A/B 级结论。

## 19. 剩余风险

1. 完整 marching-cubes / Three.js 三维等值面重建尚未实现。
2. 大型真实 Gaussian/NBO/QTAIM/NCI/GoodVibes 输出仍需样本驱动扩展 parser。
3. BDE 阈值仅用于软件判据提示，真实结论必须结合方法、基组、自旋多重度、频率和片段定义。
4. 自由基动力学参数需要真实计算、实验拟合或可靠文献，不能由示例参数外推工艺结论。
5. PostgreSQL migration 与生产级大文件任务队列仍可继续强化。

## 20. 下一步最小可证伪计算任务

1. 对 DCS、MCSOMe、DMOS 分别执行真实 `monomer_opt/freq/NBO`，上传 Gaussian log，核验 Gibbs、NPA、WBI、NBO E(2)。
2. 对 MCSOMe 构建 `C=C π-complex` 与 `O->Ti poison complex`，上传真实 log，计算 ΔGpoison。
3. 对 MCSOMe 与 DCS 分别构建插入 TS，要求恰好一个合理虚频，并用 IRC 验证连接。
4. 对 Si-C 片段计算 BDE，核验自由基片段自旋多重度和频率。
5. 对 PP 叔碳模型与 RO• 抽氢/β-scission TS 计算势垒，建立自由基竞争真实参数。

## 21. 下一步最小实验任务

1. 对 iPP / PPR / IPC / LCB-IPC 样品做 GPC、MFR、gel、SAOS 和拉伸流变，区分降解、LCB、轻度交联和过凝胶。
2. 对过氧化物处理前后样品做 FTIR carbonyl index、Si-O-Si、Si-OH、Si-Cl/Si-OMe 残留分析。
3. 做 29Si NMR 验证 Si-Cl、Si-OH、Si-O-Si、Si-C 环境变化。
4. 做 DSC/XRD/TEM 或 SEM 验证结晶和 EPC 相畴稳定性。
5. 若关注电绝缘，补充介电谱、击穿、空间电荷或 TSC 陷阱数据。

## 22. 下一步软件测试任务

1. 加入真实大 Gaussian log、NBO、QTAIM、NCI、GoodVibes 输出样本回归测试。
2. 扩展 cube 大文件性能测试与真实 3D 等值面渲染截图测试。
3. 为 `SCIENTIFIC_COMPUTATION_FULL_TEST_REPORT.md` 增加 JSON/CSV 自动导出版本。
4. 扩展 Playwright 截图矩阵，覆盖 1280px、1600px、390px 以及浅色/深色主题。
5. 建立 PostgreSQL-ready migration 验证和大文件异步解析队列测试。

## 23. 总结

本次全面科学计算测试通过。当前可以认为：平台的科学计算逻辑、单位换算、自由能公式、BDE 公式、parser 边界、API 错误路径、mock 数据边界和中文 UI 工作流已通过自动化验证。

但当前测试没有产生新的真实 A/B 级科学结论；真实机理判断仍必须来自后续上传的真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 计算结果或真实实验数据。
