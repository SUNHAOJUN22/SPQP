from __future__ import annotations

import csv
import io
import json
from typing import Any

from app.services.top_scientist_protocol import top_scientist_protocol


REPORT_SECTIONS = [
    "项目概述",
    "论文知识映射",
    "报告知识映射",
    "真实文件实例测试",
    "分子结构与研究对象",
    "Si–O 键本征属性",
    "电子云密度与静电势分析",
    "前线轨道分析",
    "电荷布居与电荷转移",
    "NBO 给体-受体相互作用",
    "QTAIM / NCI 弱相互作用分析",
    "TEA 助催化剂作用",
    "Ti 活性中心毒化判据",
    "插入反应自由能面",
    "水解缩合后反应",
    "过氧化物自由基机理",
    "PP β-scission 与交联竞争",
    "Si–C 连接稳定性",
    "Si–C / Si–O / Si–Cl 后反应差异",
    "羰基三分法",
    "乙烯/等规度/结晶度影响",
    "乙烯引入、等规度与固态反应窗口",
    "实验-DFT 对照",
    "可证伪机制模型",
    "链长效应与电子效应分解",
    "文献证据等级与未验证假说",
    "证据等级系统",
    "最小可证伪任务",
    "软件化执行映射",
    "软件化执行接口",
    "研究对象与四轴机制协议",
    "量子化学任务设计要求",
    "波函数与电子结构分析要求",
    "过氧化物比较维度",
    "实验表征逻辑",
    "顶尖 PI 工作标准",
    "科学计算连接器配置",
    "MCP 工具清单",
    "生成的 Gaussian 输入模板",
    "cubegen / Multiwfn / GoodVibes 命令模板",
    "只读解析结果",
    "外部执行安全边界",
    "未执行任务清单",
    "下一步可证伪计算任务",
    "DCS / MCSOMe / DMOS 最终排序",
    "数据可靠性说明",
    "Gaussian 输入文件附录",
]


SECTION_KEYS = {
    "项目概述": "project_summary",
    "论文知识映射": "thesis_knowledge_mapping",
    "报告知识映射": "report_knowledge_mapping",
    "真实文件实例测试": "real_instance_test",
    "分子结构与研究对象": "molecule_structures",
    "Si–O 键本征属性": "sio_intrinsic_descriptors",
    "电子云密度与静电势分析": "electron_density_esp",
    "前线轨道分析": "frontier_orbitals",
    "电荷布居与电荷转移": "charge_population",
    "NBO 给体-受体相互作用": "nbo_interactions",
    "QTAIM / NCI 弱相互作用分析": "qtaim_nci",
    "TEA 助催化剂作用": "tea_cocatalyst",
    "Ti 活性中心毒化判据": "ti_poisoning",
    "插入反应自由能面": "insertion_free_energy",
    "水解缩合后反应": "hydrolysis_condensation",
    "过氧化物自由基机理": "peroxide_radical_mechanism",
    "PP β-scission 与交联竞争": "pp_scission_crosslinking",
    "Si–C 连接稳定性": "sic_stability",
    "Si–C / Si–O / Si–Cl 后反应差异": "sic_sio_sicl_post_reaction",
    "羰基三分法": "carbonyl_three_way_taxonomy",
    "乙烯/等规度/结晶度影响": "ethylene_isotacticity_crystallinity_effect",
    "乙烯引入、等规度与固态反应窗口": "ethylene_isotacticity_solid_state_window",
    "实验-DFT 对照": "experiment_dft_comparison",
    "可证伪机制模型": "falsifiable_model",
    "链长效应与电子效应分解": "chain_length_electronic_effect",
    "文献证据等级与未验证假说": "literature_evidence_unverified_hypotheses",
    "证据等级系统": "evidence_level_system",
    "最小可证伪任务": "minimal_falsification_tasks",
    "软件化执行映射": "software_execution_mapping",
    "软件化执行接口": "software_execution_interfaces",
    "研究对象与四轴机制协议": "top_scientist_research_objects",
    "量子化学任务设计要求": "quantum_task_design_requirements",
    "波函数与电子结构分析要求": "wavefunction_electronic_analysis_requirements",
    "过氧化物比较维度": "peroxide_comparison_dimensions",
    "实验表征逻辑": "experimental_characterization_logic",
    "顶尖 PI 工作标准": "top_pi_working_standard",
    "科学计算连接器配置": "simulation_connector_config",
    "MCP 工具清单": "mcp_tool_inventory",
    "生成的 Gaussian 输入模板": "generated_gaussian_templates",
    "cubegen / Multiwfn / GoodVibes 命令模板": "external_command_templates",
    "只读解析结果": "read_only_parse_results",
    "外部执行安全边界": "external_execution_safety_boundary",
    "未执行任务清单": "unexecuted_simulation_jobs",
    "下一步可证伪计算任务": "next_falsifiable_simulation_tasks",
    "DCS / MCSOMe / DMOS 最终排序": "final_ranking",
    "数据可靠性说明": "data_reliability",
    "Gaussian 输入文件附录": "gaussian_appendix",
}


def _reliability_block() -> str:
    return (
        "数据可靠性说明：上传 Gaussian 输出解析得到的数据、用户手动输入的数据、示例数据分别记录。"
        "示例数据仅用于界面演示，不能作为真实量子化学结论。缺失数据统一写作“当前文件未提供”。"
    )


def _default_conclusion() -> str:
    return (
        "在当前数据集中，MCSOMe 的 ΔGpoison 为正，说明 O→Ti 非生产性配位相对于 C=C π-络合物不占优势；"
        "同时其插入势垒接近 DCS，并保留 Si–O 后反应位点。因此，MCSOMe 可被视为兼具聚合兼容性和"
        "后反应功能化潜力的平衡候选结构。该结论模板只有在真实上传数据或经验证用户输入支持时才可作为科学结论。"
    )


def _default_thesis_mapping() -> str:
    return (
        "当前报告已预留论文知识映射章节。若尚未调用 /api/literature/import-thesis，"
        "则只能记录内置论文主题线索，不能引用为完整文献抽取结果。"
    )


def _default_experiment_dft() -> str:
    return (
        "当前未导入实验 CSV 或 DFT 对照数据，无法评价实验活性、插入率与 ΔG‡ / ΔGpoison 的相关性。"
        "请导入实验记录并上传 Gaussian 输出后再生成真实结论。"
    )


def _default_radical_mechanism() -> str:
    return (
        "当前报告采用 V4 统一机制框架：Si–O 路线解决的是如何可设计地形成长链支化；"
        "过氧化物路线解决的是如何在自由基不可控副反应中争取支化/交联而避免 PP β-断裂降解。"
        "RO–OR 均裂产生 RO•，RO• 抽取 PP 三级 C–H 后形成 PP 大分子自由基；该自由基可能发生 β-scission 降解，"
        "也可能在共剂、双官能单体、EPC 相或硅烷后反应位点存在时发生复合、接枝或长链支化。"
        "有效长链支化效率可写为 ΦLCB = f(χinsert, χhydrolysis, χcondensation, χradical_recombination) − "
        "f(χβ-scission, χoxidation, χTi_poison, χover-gel)。"
        "没有真实 GPC、流变、凝胶分数或半衰期数据时，禁止输出确定性降解/交联结论。"
    )


def _default_evidence_level_system() -> str:
    return (
        "证据等级系统：A级为真实收敛计算与正确 TS/IRC/波函数分析，B级为真实实验数据，"
        "C级为文献线索或用户输入，D级为 mock/example 或趋势假说。当前报告若未上传真实计算或实验数据，"
        "只能给出 C/D 级机制假说，不能写成确定性论文结论。"
    )


def _default_minimal_falsification_tasks() -> str:
    return (
        "最小可证伪任务：每个机制判断至少对应一个 Gaussian/NBO/QTAIM/NCI 计算任务、一个实验表征任务和一个软件测试任务。"
        "例如 O→Ti 毒化假说需要 π-complex 与 O→Ti complex 的 Gibbs 自由能、n(O)→Ti E(2)、Ti–O 距离、"
        "以及缺失数据时返回“当前数据不足”的 API/UI/报告测试。"
    )


def _default_software_mapping() -> str:
    return (
        "软件化执行映射：能量判断写入 API 输入/输出、单位和公式；parser 判断写入 normalized JSON、warnings 和 provenance；"
        "机制判据写入 decision-engine 阈值、颜色标签和中文解释；实验结论写入数据表字段、导入模板、图表和可靠性等级；"
        "报告内容写入中文章节、缺失数据声明和后续验证建议。"
    )


def _default_report_driven_section(section: str) -> str:
    defaults = {
        "Si–C 连接稳定性": (
            "当前文件未提供真实 Si–C BDE、自由基攻击势垒、Si–C WBI/Mayer 或 29Si NMR 证据，"
            "不能判断硅烷侧链连接臂是否在过氧化物后处理下保持稳定。"
        ),
        "羰基三分法": (
            "羰基必须分为过氧化物羰基、接枝单体羰基和氧化副产物羰基三类。当前文件未提供 GC-MS、"
            "FTIR carbonyl index、接枝率或介电损耗数据，不能判定羰基对交联/降解的真实贡献。"
        ),
        "乙烯/等规度/结晶度影响": (
            "当前文件未提供 13C NMR 乙烯序列、等规度、DSC/XRD 结晶度或 EPC 相比例数据，"
            "只能把乙烯/等规度/结晶度作为控制自由基扩散和 β-scission/复合竞争的待验证变量。"
        ),
        "软件化执行接口": (
            "软件化执行接口：POST /api/literature/import-report-docx 导入报告线索；"
            "GET /api/literature/report-knowledge 读取 C 级报告知识；"
            "POST /api/reports/generate 将报告线索写入中文章节；"
            "POST /api/research/top-scientist-prompt 生成带证据等级和可证伪任务的研究 Prompt。"
        ),
        "科学计算连接器配置": (
            "当前科学计算连接器默认处于 template_only / parse_only 模式。工具路径可登记为配置项，"
            "但平台不会自动探测系统路径，也不会执行 Gaussian、cubegen、Multiwfn、GoodVibes 或 version command。"
        ),
        "MCP 工具清单": (
            "MCP 工具清单包括 generate_gaussian_input、parse_gaussian_log、parse_cube、parse_nbo、parse_qtaim、"
            "parse_nci、parse_goodvibes、calculate_delta_g_bind、calculate_delta_g_poison、calculate_insert_barrier、"
            "calculate_bde_sic、calculate_bde_sio、calculate_radical_kinetics、generate_cubegen_template、"
            "generate_multiwfn_qtaim_template、generate_multiwfn_nci_template、generate_goodvibes_parse_task、"
            "generate_slurm_script_template 和 generate_chinese_report。所有工具默认不执行外部程序。"
        ),
        "生成的 Gaussian 输入模板": (
            "当前报告未附加真实 Gaussian 输入模板。生成的 .gjf/.com 文本只能作为任务草稿，不能作为已完成计算证据。"
        ),
        "cubegen / Multiwfn / GoodVibes 命令模板": (
            "本报告中列出的 cubegen、Multiwfn、GoodVibes 相关命令均为模板，除非用户显式确认并在安全工作目录内执行，"
            "否则本平台不会运行外部科学计算程序。"
        ),
        "只读解析结果": (
            "当前文件未提供真实外部输出解析结果。只有用户上传真实 log/out/cube/NBO/QTAIM/NCI/GoodVibes 文本并完成解析后，"
            "相关字段才可能进入 A 级计算证据候选。"
        ),
        "外部执行安全边界": (
            "外部执行默认关闭：will_execute = false。Simulation Job 只保存模板、输入文本、命令草稿和输出文件预期；"
            "任何真实执行都必须在项目安全目录内经过二次确认。"
        ),
        "未执行任务清单": (
            "当前所有 Simulation Jobs 均按未执行任务记录。未执行任务只能用于计划和复现实验设计，不能写成真实结果。"
        ),
        "下一步可证伪计算任务": (
            "建议优先生成 DCS/MCSOMe/DMOS 的 isolated monomer opt/freq/NBO、TEA complex、Ti pi-complex、"
            "O-to-Ti poison complex、insertion TS/IRC、Si-C BDE 和 RO-OR homolysis 模板；完成真实计算后再上传输出解析。"
        ),
    }
    return defaults.get(section, "当前文件未提供")


def _default_real_instance_test() -> str:
    return (
        "当前报告尚未合并真实文件实例摘要。需要通过 /api/literature/import-thesis、"
        "/api/literature/import-polypropylene-radical-review、/api/literature/import-report-docx 或 "
        "/api/literature/import-ocr-text 导入只读文本线索。所有文献抽取均为 C 级证据；"
        "PDF 文本层疑似字体编码异常时，关键词统计不可作为可靠结论。"
    )


def _default_protocol_section(section: str) -> Any:
    protocol = top_scientist_protocol()
    if section == "研究对象与四轴机制协议":
        return {
            "research_objects": protocol["research_objects"],
            "four_axis_protocol": protocol["four_axis_protocol"],
            "scientific_principles": protocol["scientific_principles"],
        }
    if section == "量子化学任务设计要求":
        return {"tasks": protocol["quantum_tasks"], "required_fields": protocol["quantum_task_fields"]}
    if section == "波函数与电子结构分析要求":
        return protocol["electronic_analysis_requirements"]
    if section == "过氧化物比较维度":
        return protocol["peroxide_analysis_requirements"]
    if section == "实验表征逻辑":
        return protocol["experimental_mapping"]
    if section == "顶尖 PI 工作标准":
        return {
            "thinking_workflow": protocol["thinking_workflow"],
            "output_format_requirements": protocol["output_format_requirements"],
            "capability_standards": protocol["capability_standards"],
            "forbidden_behaviors": protocol["forbidden_behaviors"],
        }
    return "当前文件未提供"


def _section_value(section: str, payload: dict[str, Any]) -> Any:
    return payload.get(SECTION_KEYS[section], "当前文件未提供")


def generate_markdown_report(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", _reliability_block(), ""]
    for section in REPORT_SECTIONS:
        lines.append(f"## {section}")
        if section == "数据可靠性说明":
            value = payload.get(SECTION_KEYS[section], _reliability_block())
        elif section in {"论文知识映射", "报告知识映射"}:
            value = payload.get(SECTION_KEYS[section], _default_thesis_mapping())
        elif section == "真实文件实例测试":
            value = payload.get(SECTION_KEYS[section], _default_real_instance_test())
        elif section == "实验-DFT 对照":
            value = payload.get(SECTION_KEYS[section], _default_experiment_dft())
        elif section in {
            "过氧化物自由基机理",
            "PP β-scission 与交联竞争",
            "Si–C / Si–O / Si–Cl 后反应差异",
            "乙烯引入、等规度与固态反应窗口",
            "文献证据等级与未验证假说",
        }:
            value = payload.get(SECTION_KEYS[section], _default_radical_mechanism())
        elif section in {
            "Si–C 连接稳定性",
            "羰基三分法",
            "乙烯/等规度/结晶度影响",
            "软件化执行接口",
            "科学计算连接器配置",
            "MCP 工具清单",
            "生成的 Gaussian 输入模板",
            "cubegen / Multiwfn / GoodVibes 命令模板",
            "只读解析结果",
            "外部执行安全边界",
            "未执行任务清单",
            "下一步可证伪计算任务",
        }:
            value = payload.get(SECTION_KEYS[section], _default_report_driven_section(section))
        elif section == "证据等级系统":
            value = payload.get(SECTION_KEYS[section], _default_evidence_level_system())
        elif section == "最小可证伪任务":
            value = payload.get(SECTION_KEYS[section], _default_minimal_falsification_tasks())
        elif section == "软件化执行映射":
            value = payload.get(SECTION_KEYS[section], _default_software_mapping())
        elif section in {
            "研究对象与四轴机制协议",
            "量子化学任务设计要求",
            "波函数与电子结构分析要求",
            "过氧化物比较维度",
            "实验表征逻辑",
            "顶尖 PI 工作标准",
        }:
            value = payload.get(SECTION_KEYS[section], _default_protocol_section(section))
        elif section == "可证伪机制模型":
            value = payload.get(SECTION_KEYS[section], _default_conclusion())
        else:
            value = _section_value(section, payload)
        if isinstance(value, (dict, list)):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2, ensure_ascii=False))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines)


def generate_html_report(title: str, payload: dict[str, Any]) -> str:
    sections = []
    for section in REPORT_SECTIONS:
        value = _section_value(section, payload)
        if section == "数据可靠性说明":
            value = payload.get(SECTION_KEYS[section], _reliability_block())
        if section in {"论文知识映射", "报告知识映射"}:
            value = payload.get(SECTION_KEYS[section], _default_thesis_mapping())
        if section == "真实文件实例测试":
            value = payload.get(SECTION_KEYS[section], _default_real_instance_test())
        if section == "实验-DFT 对照":
            value = payload.get(SECTION_KEYS[section], _default_experiment_dft())
        if section in {
            "过氧化物自由基机理",
            "PP β-scission 与交联竞争",
            "Si–C / Si–O / Si–Cl 后反应差异",
            "乙烯引入、等规度与固态反应窗口",
            "文献证据等级与未验证假说",
        }:
            value = payload.get(SECTION_KEYS[section], _default_radical_mechanism())
        if section in {"Si–C 连接稳定性", "羰基三分法", "乙烯/等规度/结晶度影响", "软件化执行接口"}:
            value = payload.get(SECTION_KEYS[section], _default_report_driven_section(section))
        if section == "证据等级系统":
            value = payload.get(SECTION_KEYS[section], _default_evidence_level_system())
        if section == "最小可证伪任务":
            value = payload.get(SECTION_KEYS[section], _default_minimal_falsification_tasks())
        if section == "软件化执行映射":
            value = payload.get(SECTION_KEYS[section], _default_software_mapping())
        if section in {
            "研究对象与四轴机制协议",
            "量子化学任务设计要求",
            "波函数与电子结构分析要求",
            "过氧化物比较维度",
            "实验表征逻辑",
            "顶尖 PI 工作标准",
        }:
            value = payload.get(SECTION_KEYS[section], _default_protocol_section(section))
        if section == "可证伪机制模型":
            value = payload.get(SECTION_KEYS[section], _default_conclusion())
        content = f"<pre>{json.dumps(value, indent=2, ensure_ascii=False)}</pre>" if isinstance(value, (dict, list)) else f"<p>{value}</p>"
        sections.append(f"<section><h2>{section}</h2>{content}</section>")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{ font-family: "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif; line-height: 1.65; color: #17202a; margin: 48px; }}
    h1 {{ color: #0e3a4f; }}
    h2 {{ border-bottom: 1px solid #d7e3ea; padding-bottom: 6px; color: #203040; }}
    pre {{ white-space: pre-wrap; background: #f4f8fb; padding: 16px; border-radius: 10px; }}
    .note {{ background: #fff7df; border: 1px solid #ead58c; padding: 12px 16px; border-radius: 12px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="note">{_reliability_block()}</p>
  {''.join(sections)}
</body>
</html>"""


def generate_csv_report(payload: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["章节", "内容"])
    for section in REPORT_SECTIONS:
        value = _section_value(section, payload)
        if section in {"论文知识映射", "报告知识映射"}:
            value = payload.get(SECTION_KEYS[section], _default_thesis_mapping())
        if section == "真实文件实例测试":
            value = payload.get(SECTION_KEYS[section], _default_real_instance_test())
        if section == "实验-DFT 对照":
            value = payload.get(SECTION_KEYS[section], _default_experiment_dft())
        if section in {
            "过氧化物自由基机理",
            "PP β-scission 与交联竞争",
            "Si–C / Si–O / Si–Cl 后反应差异",
            "乙烯引入、等规度与固态反应窗口",
            "文献证据等级与未验证假说",
        }:
            value = payload.get(SECTION_KEYS[section], _default_radical_mechanism())
        if section in {"Si–C 连接稳定性", "羰基三分法", "乙烯/等规度/结晶度影响", "软件化执行接口"}:
            value = payload.get(SECTION_KEYS[section], _default_report_driven_section(section))
        if section == "证据等级系统":
            value = payload.get(SECTION_KEYS[section], _default_evidence_level_system())
        if section == "最小可证伪任务":
            value = payload.get(SECTION_KEYS[section], _default_minimal_falsification_tasks())
        if section == "软件化执行映射":
            value = payload.get(SECTION_KEYS[section], _default_software_mapping())
        if section in {
            "研究对象与四轴机制协议",
            "量子化学任务设计要求",
            "波函数与电子结构分析要求",
            "过氧化物比较维度",
            "实验表征逻辑",
            "顶尖 PI 工作标准",
        }:
            value = payload.get(SECTION_KEYS[section], _default_protocol_section(section))
        if section == "可证伪机制模型":
            value = payload.get(SECTION_KEYS[section], _default_conclusion())
        writer.writerow([section, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value])
    writer.writerow(["数据可靠性说明", _reliability_block()])
    return output.getvalue()


def generate_report(title: str, fmt: str, payload: dict[str, Any]) -> str:
    if fmt == "markdown":
        return generate_markdown_report(title, payload)
    if fmt == "json":
        return json.dumps({"标题": title, "章节": payload, "数据可靠性说明": _reliability_block()}, indent=2, ensure_ascii=False)
    if fmt == "csv":
        return generate_csv_report(payload)
    if fmt == "html":
        return generate_html_report(title, payload)
    if fmt == "pdf-placeholder":
        return generate_markdown_report(title, payload) + "\n\nPDF 导出占位：后续阶段可使用受控 HTML 渲染器生成 PDF。"
    raise ValueError(f"不支持的报告格式：{fmt}")
