# V4 自由基后反应与 Si–C 机理实现报告

生成时间：2026-05-21

## 实现范围

- 新增“自由基后反应与硅碳键机理”研究线，覆盖过氧化物诱导 PP β-scission、自由基复合/交联、共剂接枝、长链支化、Si–C 键稳定性、停留时间窗口、乙烯引入和等规度影响。
- 新增只读文献导入接口，支持 `.docx`、`.pdf`、`.txt`、`.md`。PDF 解析使用 PyMuPDF 提取页面文本；扫描型 PDF 不猜测内容。
- 新增前端中文页面：自由基后反应、过氧化物结构库、Si–C 键稳定性、降解-交联竞争图、停留时间窗口、乙烯/等规度影响。
- 报告系统新增 V4 章节，明确区分文献证据、用户输入、真实计算数据和示例数据。

## 新增 API

- `POST /api/literature/import-polypropylene-radical-review`
- `GET /api/analysis/peroxide-library`
- `POST /api/analysis/peroxide-profile`
- `POST /api/analysis/radical-branching-vs-scission`
- `POST /api/analysis/sic-stability`
- `POST /api/analysis/residence-time-window`

## 科学边界

- 平台不执行 Gaussian、cubegen、Multiwfn 或用户上传文件。
- 过氧化物和 PP 自由基模型为参数化机制模型，不替代 GPC、流变、凝胶分数、ESR、真实半衰期曲线或量子化学计算。
- 含羰基过氧化物只作为独立变量建模；不得默认输出“更易交联”或“更易降解”的确定性结论。
- 缺少 Si–C BDE、过氧化物半衰期或真实实验数据时，系统返回“当前数据不足”或可靠性说明。

## 验证结果

- `npm run test:backend`：通过，44 passed。
- `backend\.venv\Scripts\python.exe scripts\full_function_smoke.py`：通过，覆盖 V4 新增 API 和 PDF 文献导入。
- `python scripts\quality_gate.py`：通过。
- `backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py`：通过，最终 PASS。
- `npm --prefix frontend run typecheck`：通过。
- `npm --prefix frontend run lint`：通过。
- `npm --prefix frontend run build`：通过。
- `npm run test:ui-smoke`：HTTP UI smoke 通过；当前 Node 环境未安装 Playwright，因此真实浏览器流程按脚本提示跳过。

## 剩余风险

- 扫描型 PDF 仍需要 OCR 工具链；当前实现只做 PDF 文本层提取。
- 自由基竞争模型中的权重为机制化参数模型，需用真实实验数据重新标定。
- 前端 3D/等值面渲染仍沿用当前占位能力，V4 未引入新的重型三维依赖。

