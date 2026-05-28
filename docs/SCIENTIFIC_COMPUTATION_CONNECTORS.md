# 科学计算连接器设计说明

## 定位

科学计算连接器用于把 Gaussian16、cubegen、Multiwfn、GoodVibes、SLURM 和只读 parser 纳入统一科研工作流。当前实现只负责：

- 登记外部工具配置。
- 生成输入文件或命令模板。
- 只读解析用户提供的文本输出。
- 保存任务草稿、provenance、证据等级和安全边界。

平台默认不执行 Gaussian、cubegen、Multiwfn、GoodVibes、SLURM 或用户上传文件。

## 安全边界

所有连接器任务默认满足：

- `will_execute = false`
- `execution_mode = template_only` 或 `parse_only`
- `evidence_grade = D`，直到真实输出文件经只读 parser 解析并人工核验后才可能升级
- 外部工具路径只做格式登记，不执行 `version`、`help` 或任何命令
- 检测到路径穿越时返回中文错误：“检测到非法路径，禁止登记科学计算工具。”

## 默认工具

| 工具 | 默认模式 | 用途 | 是否执行 |
| --- | --- | --- | --- |
| Gaussian16 | template_only | 生成 `.gjf/.com` 输入模板 | 否 |
| formchk | template_only | 生成 fchk 转换命令模板 | 否 |
| cubegen | template_only | 生成 density / ESP / MO cube 命令模板 | 否 |
| Multiwfn | template_only | 生成 QTAIM / NCI / ESP 脚本模板 | 否 |
| GoodVibes | parse_only | 只读解析 GoodVibes 输出文本 | 否 |
| RDKit | template_only | 分子处理占位 | 否 |
| SLURM | template_only | 生成批处理脚本模板 | 否 |
| 只读解析器 | parse_only | 解析 log、cube、NBO、QTAIM、NCI、GoodVibes 文本 | 否 |

## API

### 工具注册

```text
GET /api/simulation/tools
POST /api/simulation/tools
GET /api/simulation/tools/{tool_id}
PATCH /api/simulation/tools/{tool_id}
POST /api/simulation/tools/{tool_id}/validate-template
```

### 任务模板

```text
POST /api/simulation/jobs
GET /api/simulation/jobs
GET /api/simulation/jobs/{job_id}
POST /api/simulation/jobs/{job_id}/generate-template
POST /api/simulation/jobs/{job_id}/mark-ready
POST /api/simulation/jobs/{job_id}/cancel
```

### 只读解析

```text
POST /api/simulation/parse/gaussian-log
POST /api/simulation/parse/cube
POST /api/simulation/parse/nbo
POST /api/simulation/parse/qtaim
POST /api/simulation/parse/nci
POST /api/simulation/parse/goodvibes
```

## 示例请求

生成 cubegen ESP 模板：

```json
{
  "tool_type": "cubegen",
  "job_type": "cubegen_esp",
  "molecule_name": "MCSOMe"
}
```

返回结果中必须包含：

```json
{
  "will_execute": false,
  "evidence_grade": "D",
  "command_template": "cubegen 0 potential=scf input.fchk esp.cube 0 h"
}
```

## 证据等级

- 模板任务：D 级证据，只能说明平台生成了可复核模板。
- 只读解析成功：默认 A 级候选计算证据，但仍需要人工核验方法、基组、频率、TS/IRC 和原始文件来源。
- 解析失败或示例文本：D 级证据，不能作为真实科学结论。

## 前端入口

前端新增“科学计算连接器”页面，位于“量子计算”分组。页面包含：

- 工具注册表。
- 外部执行安全提示。
- 任务模板生成器。
- 命令模板预览。
- 生成文本预览。
- provenance / evidence grade 详情面板。

## 剩余边界

当前版本尚未实现外部执行队列。即使某个工具配置了可执行路径，平台也不会自动运行它。后续若需要执行，应单独设计：

- 用户二次确认。
- 项目目录沙箱。
- 作业队列与日志审计。
- 资源限制。
- 明确的失败恢复策略。
