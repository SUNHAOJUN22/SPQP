# CHANGELOG

## 2026-05-28 - 科学计算连接器与 MCP 仿真接口

- 新增科学计算连接器数据模型：`simulation_tools`、`simulation_jobs`、`simulation_parse_results`，保存工具配置、任务模板、只读解析结果、provenance、证据等级和安全边界。
- 新增 `/api/simulation/*` 接口，支持 Gaussian、cubegen、Multiwfn、GoodVibes、SLURM 等工具登记、路径模板校验、任务草稿生成和只读 parser 调用。
- 所有连接器任务默认 `will_execute = false`，路径校验不执行 version command；检测到路径穿越时返回中文错误。
- MCP 工具清单扩展到 `parse_nbo`、`parse_qtaim`、`parse_nci`、`parse_goodvibes`、`calculate_insert_barrier`、`calculate_bde_sio`、`calculate_radical_kinetics`、`generate_cubegen_template`、`generate_multiwfn_qtaim_template`、`generate_multiwfn_nci_template`、`generate_goodvibes_parse_task`、`generate_slurm_script_template` 和 `generate_chinese_report`。
- 前端新增“科学计算连接器”页面，展示工具注册表、安全边界、任务模板生成器、命令模板预览和 provenance 面板。
- 中文报告新增科学计算连接器、MCP 工具清单、命令模板、只读解析结果、未执行任务清单和下一步可证伪计算任务章节。
- 新增 `docs/SCIENTIFIC_COMPUTATION_CONNECTORS.md` 与 `docs/MCP_SIMULATION_INTERFACE.md`，明确连接器/MCP 的模板生成、只读解析和不执行外部程序边界。
- 新增 `backend/tests/test_simulation_connectors.py`，覆盖非执行默认值、非法路径中文错误、任务模板、只读解析、MCP 白名单和未知工具拒绝。

## 2026-05-27 - 科学计算验证机制工作流

- 新增 `GET /api/scientific-computation/task-matrix`，显式暴露 36 个 Gaussian / 后处理任务模板、关键输出、可靠性判据和“不执行外部软件”安全边界。
- 新增 `POST /api/scientific-computation/energy-workbench`，统一计算 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔGproduct 和 krel，并在缺少 Gibbs/π-complex/O→Ti/TS 时返回中文 warnings。
- 新增 `POST /api/analysis/bde`，支持 Si–C、Si–O、Si–Cl、RO–OR BDE 计算，输出 Hartree、kcal/mol、eV、证据等级、is_mock、provenance 和中文解释。
- 新增 `POST /api/analysis/radical-kinetics` 分析别名，显式返回自由基竞争公式和只求解用户参数、不执行外部软件的 provenance。
- 前端新增“科学计算工作流”页面，包含计算任务矩阵、能量公式工作台、BDE 计算、证据与安全边界和报告输出边界。
- 新增 `backend/tests/test_scientific_computation_workflow.py`，覆盖 BDE 单位/判据、36 任务矩阵、能量公式工作台、mock 边界和自由基动力学入口。
- 扩展 `scripts/full_function_smoke.py` 与 `scripts/ui_smoke_check.mjs`，把科学计算工作流纳入 API 和 UI smoke。
- 新增 `docs/SCIENTIFIC_COMPUTATION_WORKFLOW.md` 与 `docs/SCIENTIFIC_CALCULATION_TEST_REPORT.md`，记录计算任务矩阵、公式、API 示例、判据边界、测试结果和剩余风险。

## 2026-05-26 - Google Workspace 式科研工作台 UI 重构

- 新增 `scripts/mojibake_audit.py` 与 `npm run audit:mojibake`，可扫描活动源码、脚本、测试和当前文档中的疑似 UTF-8/GBK 误解码中文乱码，并生成 `docs/MOJIBAKE_CLEANUP_REPORT.md`。
- 修复前端“前线轨道”和“电荷布居”面板中的历史中文乱码，移除未被引用且含错误替换规则的旧 `frontend/fix.js`。
- 质量门禁新增“中文乱码活动文件审计”阶段；当前活动文件疑似乱码行数为 0，`integrated/origin-*` 历史来源目录保留为归档记录。
- 左侧导航重组为“首页 / 知识库 / 分子与结构 / 量子计算 / 机理分析 / 实验闭环 / 报告 / 自动化”分组，弱化长列表 demo 感。
- 新增 `frontend/components/layout/*` 与 `frontend/components/data/*`，提供顶部栏、分组导航、页面标题、详情面板、资源表格、证据等级 badge、解析质量 badge 和 provenance 面板。
- 顶部栏新增全局搜索框，占位为“搜索分子、任务、报告、证据…”，并保留数据源状态、当前分子选择、主题切换和设置入口。
- “论文与报告知识库”改为 Google Drive 风格真实文件实例表格 + 右侧文件详情面板，保留 PDF 乱码 warning、OCR 文本导入和 C级证据边界。
- “分子库”改为 Drive + scientific viewer 三栏工作台，新增分子资源表、结构视图和分子详情/provenance 面板。
- “Gaussian 输入生成”改为 Colab/Docs 风格任务模板 + 参数表单 + 输入文件预览布局，明确“不执行 Gaussian，仅生成输入文件”。
- “Gaussian 输出解析”改为 Cloud Log Viewer 风格三栏布局，明确“仅读取，不执行 Gaussian”，并在右侧展示解析质量、warnings 和 provenance。
- “中文报告生成”改为 Google Docs 风格章节大纲 / 报告预览 / 证据与数据来源三栏工作台。
- “MCP 自动化工作流”改为 Cloud Console 工具页，展示工具列表、工具详情、输入 schema、运行结果、安全边界和 Prompt 生成器。
- “数据管理”改为 Drive 式上传区 + 资源表 + 数据源详情 + provenance 审计面板，并明确只读解析边界。
- “实验-DFT 对照”清理乱码并改为 Sheets 风格实验记录表、来源面板和中文图表标题/坐标轴。
- “量子判据引擎”清理乱码并改为判据资源表、证据与结论边界、候选热图和中文论文式结论模板。
- “整合总控台”和“总览驾驶舱”继续重构为 Cloud Console 式入口，显示项目资源、待处理任务、数据健康、运行边界和可恢复路径。
- “合并工作台”清理历史乱码，保留四轴判据、后反应动力学、贝叶斯 TS 指导、VMC 预览和催化剂数据库资源表。
- TEA 助剂、Ti 毒化、插入能量面、水解缩合、NBO、电子云密度/ESP/Fukui/差分密度页面完成中文化修复，图表标题、公式、状态标签和 cube 提示均可读。
- Playwright E2E 已复跑通过：全导航抽样、Gaussian 解析、cube 上传预览、合并工作台、MCP 工作流和 390px 移动端检查均通过。

## 2026-05-26 - 真实文件实例测试与 PDF 编码边界

- 使用真实文件完成端到端实例测试：博士论文 DOCX、`Radical reactions on polypropylene in the solid state.pdf`、张志箭毕业论文 PDF。
- 新增 `docs/REAL_INSTANCE_TEST_REPORT.md`，记录真实抽取长度、实体数量、关键词计数、报告生成 ID 和 C 级证据边界。
- `extract_pdf_text` 增加结构化解析质量评分：`readable`、`encoded-garbled`、`scanned-needs-ocr`、`failed`；当 PDF 能读取字符但关键词不可可靠统计时返回中文 warning，建议提供 OCR 文本或可复制文本版 PDF。
- 新增 `POST /api/literature/import-ocr-text`、`GET /api/literature/source-quality`、`GET /api/literature/real-instance-summary`，OCR 文本固定标注为 C 级证据，服务器不执行 OCR 程序。
- 中文报告新增“真实文件实例测试”章节；前端“论文与报告知识库”新增真实文件实例卡片、PDF 解析质量 badge、乱码 warning、关键词统计柱状图和“导入 OCR 文本”输入区。
- 真实实例验证后复跑 backend、typecheck、lint、build、full function smoke 和 Playwright E2E，均通过。

## 2026-05-25 - 报告驱动知识闭环升级

- 新增 `POST /api/literature/import-report-docx` 与 `GET /api/literature/report-knowledge`，可只读解析 `SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿` 类报告，抽取 Si–O/Si–C、TEA/Ti、过氧化物、PP β-scission、LCB、羰基三分法、乙烯/等规度/结晶度等 C 级报告线索。
- 顶尖科学家协议新增“报告驱动闭环扩展槽位”，明确报告抽取结果只能作为 C 级线索，必须映射到 API、报告章节、UI 和测试，不能替代真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 或实验数据。
- 中文报告新增“Si–C 连接稳定性”“羰基三分法”“乙烯/等规度/结晶度影响”“软件化执行接口”等章节；报告生成会自动合并最新导入报告的 C 级知识映射。
- 前端“论文知识库”升级为“论文与报告知识库”，新增报告驱动知识映射、默认报告 docx 导入按钮、C 级证据卡片；“MCP 自动化工作流”新增报告证据闭环展示。
- 测试与 smoke 覆盖报告 docx 导入、报告知识读取、报告章节引用、顶尖科学家协议报告扩展和 UI 检查。

## 2026-05-25 - 顶尖科学家能力进化协议落地

- 新增 `backend/app/services/top_scientist_protocol.py`，把四轴机制模型、A/B/C/D 证据等级、核心公式、机制判据、最小可证伪任务和软件化执行映射固化为后端协议。
- 协议扩展到完整总控版：研究总对象、最高科学原则、20 类 Gaussian/Multiwfn-like 任务、波函数/电子结构分析、过氧化物比较表、实验表征逻辑、思维流程、输出格式、能力标准和禁止行为均已结构化。
- 新增 `GET /api/research/top-scientist-protocol` 与 `POST /api/research/top-scientist-prompt`，并把 `generate_top_scientist_prompt` 加入 MCP 安全白名单。
- MCP prompt 生成器默认输出包含证据等级、最小可证伪任务和安全边界的中文科研工作流。
- 中文报告新增证据等级、最小可证伪任务、软件化执行映射、研究对象/四轴机制、量子化学任务、电子结构分析、过氧化物比较、实验表征逻辑和顶尖 PI 工作标准章节，避免 C/D 级假说被写成确定性结论。
- 前端“MCP 自动化工作流”页面新增顶尖科学家协议卡片，可查看 A/B/C/D 证据等级、机制判据、量子任务矩阵、实验表征映射、禁止行为和软件化映射。

## 2026-05-25 - 根目录总控测试入口修复

- 新增根目录 `pytest.ini`，使 `pytest` 从 `D:\codex2_cataSi-O` 执行时自动定位 `backend/tests` 并加入 `backend` 到 Python path。
- 新增根目录 `conftest.py`，在 Windows 开发环境中把原生 `pytest` / `pytest --cov` 转交给 `backend/.venv`，保持验收文档中的原生命令可直接运行。
- 复跑总控命令：`npm run lint`、`npm run typecheck`、`npm test`、`npm run test:e2e`、`pytest`、`pytest --cov`、`npm run build`、`python scripts\quality_gate.py`、`npm run test:ci` 全部通过。

## 2026-05-22 - Ultra prompt 全量执行扩展

- 增加真实 cube 下采样体素预览、剖切矩阵预览和两个 cube 差分电子密度 API；电子云密度页可上传 cube 并显示真实预览。
- 增加 ESP 静电势、Fukui 局部反应性、差分电子密度和自由基动力学中文导航入口。
- 增加 `/api/molecules/{id}/graph`、DSC/相形态实验导入占位、扩展 MCP 工具白名单和 GitHub Actions CI。
- Playwright UI smoke 扩展为全导航抽样、cube 上传预览和 390px 移动端检查。
- 增加 atom/bond/orbital/QTAIM/NCI/实验表征/MCP/audit 数据表，补齐上一轮质量审计暴露的数据库结构缺口。
- 增加 GoodVibes、QTAIM、NCI 只读文本 parser 与对应 API、单元测试和 smoke 覆盖。
- 增加 MCP 安全工作流 API 与中文前端页面；未知工具禁止执行。
- 增加 prompt 要求的 cube、Gaussian、实验导入、Si-O/Si-C、水解缩合和自由基分析别名接口。
- 增加根目录覆盖率门禁与固定 Playwright UI smoke，报告覆盖当前 E2E 边界。
- 修复 Next dev Turbopack root 推断和 MCP 页面 abort 文案泄漏。

## 2026-05-21 16:32:00 - Pro Max Ultra 自动化质量审计

- 增加 `scripts/ultra_quality_audit.py`，统一检查科学公式、parser、API、数据库、安全、性能和未实现风险。
- 收紧上传文件名安全边界，新增安全回归测试。
- cube parser 增加数据计数和等值面元数据。
- 增加根目录 npm 测试脚本入口。

