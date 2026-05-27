from __future__ import annotations

from typing import Any

from app.services.top_scientist_protocol import build_top_scientist_prompt, top_scientist_protocol


SAFE_TOOLS = [
    {
        "name": "generate_gaussian_input",
        "title": "生成 Gaussian 输入模板",
        "description": "只生成 .gjf 文本，不执行 Gaussian。",
        "input_schema": {"name": "str", "job_type": "str", "coordinates": "str"},
    },
    {
        "name": "parse_gaussian_log",
        "title": "解析 Gaussian log 文本",
        "description": "只读解析粘贴文本，不执行 Gaussian。",
        "input_schema": {"file_name": "str", "text": "str"},
    },
    {
        "name": "parse_cube",
        "title": "解析 cube 文本元数据",
        "description": "只读解析 cube 头、网格与数值预览，不执行 cubegen。",
        "input_schema": {"file_name": "str", "text": "str"},
    },
    {"name": "calculate_delta_g_bind", "title": "计算 ΔGbind", "description": "按 Hartree 输入计算结合自由能。", "input_schema": {"complex_g_hartree": "float", "fragment_g_hartrees": "list[float]"}},
    {"name": "calculate_delta_g_poison", "title": "计算 ΔGpoison", "description": "比较 O→Ti 与 C=C π-络合物自由能。", "input_schema": {"o_ti_complex_g_hartree": "float", "pi_complex_g_hartree": "float"}},
    {"name": "calculate_bde_sic", "title": "计算 Si–C BDE", "description": "按片段和母体 Gibbs 能计算 Si–C BDE。", "input_schema": {"g_fragments_hartree": "float", "g_molecule_hartree": "float"}},
    {
        "name": "validate-upload",
        "title": "校验上传文件名",
        "description": "检查扩展名和路径安全，不读取或执行文件。",
        "input_schema": {"file_name": "str"},
    },
    {
        "name": "peroxide_profile",
        "title": "过氧化物结构画像",
        "description": "基于用户输入参数计算半衰期窗口和风险标签。",
        "input_schema": {"half_life_min": "float", "residence_time_min": "float"},
    },
    {
        "name": "generate_chinese_report_prompt",
        "title": "生成中文科研任务 Prompt",
        "description": "输出面向 Si-O/Si-C/自由基机理的开发或研究 prompt。",
        "input_schema": {"topic": "str"},
    },
    {
        "name": "generate_top_scientist_prompt",
        "title": "生成顶尖科学家进化 Prompt",
        "description": "输出包含四轴机制、证据等级、最小可证伪任务和软件化映射的研究协议 prompt。",
        "input_schema": {"topic": "str", "include_safety": "bool"},
    },
]


SAFE_RESOURCES = [
    {
        "uri": "local://docs/README",
        "title": "README 中文使用说明",
        "description": "项目功能、运行方式、安全边界和测试命令。",
        "read_policy": "本接口只返回资源索引，不直接读取任意路径。",
    },
    {
        "uri": "local://reports/TEST_REPORT",
        "title": "自动化质量审计报告",
        "description": "科学公式、parser、API、安全和性能审计结果。",
        "read_policy": "只读报告索引。",
    },
    {"uri": "local://project/current", "title": "当前项目索引", "description": "项目、分子、任务、cube、报告和审计入口。", "read_policy": "只返回索引，不读取任意路径。"},
    {"uri": "local://cubes", "title": "cube 文件资源", "description": "上传 cube 的元数据、剖切和下采样预览。", "read_policy": "仅通过受控 API 读取数据库记录。"},
    {"uri": "local://experimental-datasets", "title": "实验数据集", "description": "GPC/MFR/凝胶/流变/FTIR/NMR/DSC/介电等用户输入数据。", "read_policy": "仅返回已登记数据源。"},
    {"uri": "local://protocol/top-scientist", "title": "顶尖科学家能力进化协议", "description": "四轴机制、证据等级、最小可证伪任务和软件化执行映射。", "read_policy": "返回内置协议元数据，不读取外部文件。"},
]


def list_mcp_tools() -> dict[str, Any]:
    return {
        "tools": SAFE_TOOLS,
        "provenance": "MCP 工具为平台内置安全工作流，不执行 shell、Gaussian、cubegen 或 Multiwfn。",
    }


def list_mcp_resources() -> dict[str, Any]:
    return {
        "resources": SAFE_RESOURCES,
        "provenance": "仅暴露受控资源索引，不开放项目目录外路径访问。",
    }


def generate_research_prompt(topic: str, include_safety: bool = True) -> dict[str, str]:
    result = build_top_scientist_prompt(topic, include_safety)
    return {
        "prompt": result["prompt"],
        "language": "zh-CN",
        "provenance": "由内置 MCP prompt 生成器创建；已包含顶尖科学家协议、证据等级和可证伪任务约束。",
    }


def generate_top_scientist_protocol_prompt(topic: str, include_safety: bool = True) -> dict[str, Any]:
    return build_top_scientist_prompt(topic, include_safety)


def get_top_scientist_protocol() -> dict[str, Any]:
    return top_scientist_protocol()
