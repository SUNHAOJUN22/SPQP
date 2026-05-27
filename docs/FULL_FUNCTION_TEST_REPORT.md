# 全功能测试报告

- 测试时间：2026-05-25
- 工作目录：`D:\codex2_cataSi-O`
- 测试环境：Windows / PowerShell / Python 3.11 venv / FastAPI TestClient / Node.js / Next.js / Playwright
- 安全边界：测试未执行 Gaussian、cubegen、Multiwfn、GoodVibes 或用户上传文件。

## 执行命令

```powershell
npm run test:backend
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
npm run test:ultra
npm run typecheck
npm run lint
npm run test:coverage
npm test
npm run test:e2e
npm run build
python scripts\quality_gate.py
```

## 功能覆盖

| 模块 | 验证方式 | 结果 |
| --- | --- | --- |
| 分子库、XYZ 导出、RDKit 构象占位 | API smoke + pytest | 通过 |
| 分子图谱与功能位点识别 | API smoke + pytest | 通过 |
| Gaussian 输入、log 上传和文本解析 | API smoke + parser tests | 通过 |
| GoodVibes/QTAIM/NCI 只读文本解析 | API smoke + pytest | 通过 |
| cube 上传、metadata、下采样体素、slice 剖切和差分电子密度预览 | API smoke + pytest | 通过 |
| ΔGbind、ΔGpoison、插入能量面、krel | scientific audit + pytest | 通过 |
| Si-O / Si-C / 水解缩合分析别名 | API smoke + pytest | 通过 |
| 过氧化物画像、β-scission/支化竞争、ΦLCB | API smoke + radical tests | 通过 |
| 实验 CSV 与 GPC/MFR/Gel 等表征导入占位 | API smoke + route tests | 通过 |
| 中文报告生成和报告读取 | API smoke + report tests | 通过 |
| MCP 工具列表、资源索引、prompt、白名单 tool run | API smoke + pytest | 通过 |

## 修复项

- 新增数据库扩展表，覆盖原质量报告列出的 atom/bond/orbital/QTAIM/NCI/实验表征/MCP/audit 结构缺口。
- 增加 GoodVibes、QTAIM、NCI 只读 parser，缺失字段保留为缺失，不补造科学结果。
- 增加 MCP 安全白名单 API；未知工具返回中文拦截错误。
- 增加 `/api/cubes/*`、`/api/cubes/difference-density`、`/api/molecules/{id}/graph`、`/api/gaussian/parse-log`、实验表征导入、Si-O/Si-C、水解缩合和自由基分析别名端点。
- 修复 Next dev 的 Turbopack root 推断，避免根目录双 lockfile 时放大扫描导致资源不足。

## 剩余风险

- 当前 QTAIM/NCI/GoodVibes parser 已覆盖轻量文本样本，真实 Multiwfn/AIMAll/GoodVibes 输出变体仍需由真实样本扩展。
- cube 当前已支持下采样体素点、剖切矩阵和差分电子密度预览；完整 marching-cubes 三维等值面重建仍需后续实现。
- SQLite 仍依赖 `create_all` 建表，正式多用户部署应引入迁移脚本和 PostgreSQL 验证。

## 报告结论边界

- 论文抽取、示例数据、用户输入和上传解析数据继续分开记录。
- 没有真实 Gaussian、cube、实验或文献核验数据时，平台只输出可证伪判据和“当前数据不足”提示。
