# 真实文件实例测试报告

- 测试时间：2026-05-26
- 测试目录：`D:\codex2_cataSi-O`
- 安全边界：未执行 Gaussian、cubegen、Multiwfn、OCR 程序；所有论文/PDF/DOCX/OCR 文本均为只读文本抽取或用户输入。

## 输入文件

| 文件 | 状态 |
| --- | --- |
| `C:\Users\resj6\Desktop\pri\博士学位论文.docx` | 已真实导入 |
| `C:\Users\resj6\Desktop\Radical reactions on polypropylene in the solid state.pdf` | 已真实导入；PDF 字体编码映射异常，关键词统计偏低 |
| `C:\Users\resj6\Desktop\pri\张志箭_毕业论文打印终版.pdf` | 已真实导入 |
| `C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx` | 本机未找到 |

## 真实抽取结果

### 博士论文 DOCX

- 文本长度：197879 字符
- 抽取实体：6 个
- 主要实体：空间位阻与电子效应耦合、ω-烯烃基三甲基硅烷、ω-烯烃基甲基二氯硅烷、MgCl2 负载 Ti 模型、TEA 助催化剂、链长窗口效应
- 警告：无
- 结论边界：文献线索为 C 级证据，不能替代真实量子化学计算。

### PP 自由基综述 PDF

- 文本长度：189480 字符
- 抽取实体：4 个
- 假说数量：3 个
- 关键词计数：由于 PDF 字体编码映射异常，关键词统计为 0
- 新增 parser 行为：`parse_quality = encoded-garbled`；检测到乱码风险时返回中文 warning：“PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；建议提供 OCR 文本或可复制文本版 PDF。”
- 结论边界：只保留机制线索，不输出确定性降解/交联结论。

### 张志箭毕业论文 PDF

- 文本长度：274321 字符
- 抽取实体：4 个
- 假说数量：3 个
- 关键词计数：
  - peroxide/radical：26
  - degradation/scission：9
  - crosslink/branching：347
  - carbonyl：0
  - ethylene/isotacticity：358

## 报告驱动入口压力测试

由于本机未找到指定 SiO/SiC/过氧化物终稿 docx，本轮使用真实博士论文 docx 压测 `/api/literature/import-report-docx`：

- 文本长度：197879 字符
- 报告驱动实体：8 个
- 关键词计数：
  - SiO/SiC：7
  - ZN/TEA/Ti：1973
  - peroxide/radical：9
  - PP/LCB/scission：101
  - microstructure：714
  - carbonyl：2
- 所有实体均标记为 C 级证据。

## 报告生成闭环

- 生成报告 ID：114
- 报告长度：21029 字符
- 已包含章节：
  - 报告知识映射
  - Si–C 连接稳定性
  - 羰基三分法
  - 软件化执行接口
- provenance 已写入：报告 docx 抽取线索为 C 级证据，不能替代真实计算/实验结论。

## OCR 与解析质量接口

新增并通过烟测：

```http
POST /api/literature/import-ocr-text
GET /api/literature/source-quality
GET /api/literature/real-instance-summary
```

- OCR 文本作为用户输入保存，证据等级固定为 C。
- 服务器不执行 OCR 程序，只接收用户粘贴或上传得到的文本。
- `source-quality` 返回每个来源的 `parse_quality`、warnings、关键词统计和论文结论边界。
- `real-instance-summary` 统一展示博士论文、张志箭 PDF、PP 自由基综述 PDF 和 SiO/SiC/PP 报告 docx 的真实实例状态。
- 中文报告新增“真实文件实例测试”章节，自动写入 C 级证据边界和 PDF 乱码 warning。

## 回归验证

已通过：

```text
npm run test:backend
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
python scripts\quality_gate.py
npm run test:e2e
```

## 剩余风险

- 指定终稿 docx 本机未找到；真实终稿导入仍需用户提供正确路径。
- `Radical reactions on polypropylene in the solid state.pdf` 的文本层存在字体编码映射异常，建议提供 OCR 文本版以获得可靠关键词统计。
- 当前 PDF/DOCX 抽取结果为 C 级报告/文献线索，不可作为 A/B 级论文结论。
