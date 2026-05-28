# MCP 科学计算仿真接口

## 目标

MCP 科学计算仿真接口把平台内的科学计算能力暴露为安全工具。它面向 Agent 工作流，但默认只允许模板生成、公式计算和只读解析。

## 工具清单

| MCP 工具 | 功能 | 安全模式 |
| --- | --- | --- |
| `generate_gaussian_input` | 生成 Gaussian 输入文件 | template_only |
| `parse_gaussian_log` | 只读解析 Gaussian log/out 文本 | parse_only |
| `parse_cube` | 只读解析 cube 元数据 | parse_only |
| `parse_nbo` | 只读解析 NBO E(2) 文本 | parse_only |
| `parse_qtaim` | 只读解析 QTAIM BCP 文本 | parse_only |
| `parse_nci` | 只读解析 NCI/RDG 文本 | parse_only |
| `parse_goodvibes` | 只读解析 GoodVibes 输出文本 | parse_only |
| `calculate_delta_g_bind` | 计算 ΔGbind | formula_only |
| `calculate_delta_g_poison` | 计算 ΔGpoison | formula_only |
| `calculate_insert_barrier` | 计算插入势垒 | formula_only |
| `calculate_bde_sic` | 计算 Si-C BDE | formula_only |
| `calculate_bde_sio` | 计算 Si-O BDE | formula_only |
| `calculate_radical_kinetics` | 计算自由基竞争动力学 | formula_only |
| `generate_cubegen_template` | 生成 cubegen 命令模板 | template_only |
| `generate_multiwfn_qtaim_template` | 生成 Multiwfn QTAIM 脚本模板 | template_only |
| `generate_multiwfn_nci_template` | 生成 Multiwfn NCI 脚本模板 | template_only |
| `generate_goodvibes_parse_task` | 生成 GoodVibes 解析任务模板 | template_only |
| `generate_slurm_script_template` | 生成 SLURM 脚本模板 | template_only |
| `generate_chinese_report` | 生成中文报告草稿 | report_only |

## 统一安全声明

所有 MCP 工具必须声明：

- `can_execute_external = false`
- 不执行 Gaussian、cubegen、Multiwfn、GoodVibes 或用户上传文件
- 输出包含 provenance 和 evidence grade
- mock/example 数据不能作为真实结论

未知工具名必须被拒绝，并返回中文错误：“工具不在安全白名单中。”

## Agent 调用示例

生成 cubegen ESP 模板：

```json
{
  "tool_name": "generate-cubegen-template",
  "arguments": {
    "template_type": "esp"
  }
}
```

解析 NBO 文本：

```json
{
  "tool_name": "parse_nbo",
  "arguments": {
    "file_name": "mcsome_nbo.txt",
    "text": "n(O)->Ti E(2)=18.2 gap=0.31 Fock=0.08"
  }
}
```

## 与报告系统的连接

报告系统新增章节：

- 科学计算连接器配置。
- MCP 工具清单。
- 生成的 Gaussian 输入模板。
- cubegen / Multiwfn / GoodVibes 命令模板。
- 只读解析结果。
- 外部执行安全边界。
- 未执行任务清单。
- 下一步可证伪计算任务。

这些章节默认写明：“当前仅生成模板或解析用户提供文本，未执行外部科学计算程序。”
