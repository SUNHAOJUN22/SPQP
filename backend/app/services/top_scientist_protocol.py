from __future__ import annotations

from textwrap import dedent
from typing import Any


RESEARCH_OBJECTS = [
    {
        "key": "DCS",
        "smiles": "C=CCCCC[Si](C)(Cl)Cl",
        "chinese_name": "5-己烯基甲基二氯硅烷",
        "role": "hex-DCS 基准结构，氯硅烷路线参考。",
    },
    {
        "key": "MCSOMe",
        "smiles": "C=CCCCC[Si](C)(OC)Cl",
        "chinese_name": "氯代-甲氧基-甲基-5-己烯基硅烷",
        "role": "单甲氧基平衡候选，可能兼具插入活性和 Si–O 后反应功能性。",
    },
    {
        "key": "DMOS",
        "smiles": "C=CCCCC[Si](C)(OC)OC",
        "chinese_name": "5-己烯基甲基二甲氧基硅烷",
        "role": "双甲氧基极限结构，Si–O 功能性强，但 O→Ti 毒化和 Al←O 过度捕获风险高。",
    },
    {"key": "catalyst_system", "species": ["Ziegler–Natta catalyst", "Ti active site", "MgCl2", "TEA", "AlEt3", "AlEt2Cl", "internal donor"]},
    {"key": "polymer_system", "species": ["PP", "iPP", "PPR", "IPC", "EPC", "LCB-IPC"]},
    {"key": "radical_system", "species": ["DCP", "BPO", "TBPB", "L-101", "TBPEH", "RO–OR", "RO•", "PP•", "EPC•", "coagent"]},
]


SCIENTIFIC_PRINCIPLES = [
    "永远从机制出发，不停留在表象；必须说明反应路径、能垒、关键键、相互作用和实验指标。",
    "永远区分聚合阶段与后处理阶段。",
    "永远区分 Si–O 与 Si–C：Si–O 主要关联给电子、配位、毒化和 Si–O–Si 后反应；Si–C 主要关联侧链连接稳定性。",
    "永远区分三类羰基：过氧化物羰基、接枝单体羰基、氧化副产物羰基。",
    "永远区分有效 LCB、轻度交联、过凝胶和降解，不能只看 gel 或 MFR 单一指标。",
    "没有数据时写“当前数据不足，不能形成可靠结论。需要补充……”。",
]


FOUR_AXIS_PROTOCOL = [
    {
        "axis": "单体轴",
        "focus": ["DCS / MCSOMe / DMOS", "Si–O", "Si–C", "Si–Cl", "C=C"],
        "questions": [
            "单体是否能插入？",
            "Si–O 是否毒化 Ti 或提供后反应功能？",
            "Si–C 是否稳定连接大分子链？",
        ],
    },
    {
        "axis": "催化剂轴",
        "focus": ["Ti active site", "MgCl2", "TEA", "AlEt3", "AlEt2Cl", "internal donor"],
        "questions": ["C=C productive π-complex 是否稳定？", "O→Ti 是否更稳定？", "TEA 是预组织还是过度捕获？"],
    },
    {
        "axis": "自由基轴",
        "focus": ["RO–OR", "RO•", "PP•", "EPC•", "coagent", "O2"],
        "questions": ["PP• 是 β-scission、复合、接枝、交联还是氧化？", "体系是降解、LCB、轻交联还是过凝胶？"],
    },
    {
        "axis": "微相轴",
        "focus": ["iPP 晶区", "PP 非晶相", "EPC 富乙烯相", "PP/EPC 界面"],
        "questions": ["自由基在哪里反应？", "PP-H-EPC 桥联是否改善相形态？", "羰基是否破坏电绝缘？"],
    },
]


EVIDENCE_LEVELS = [
    {
        "level": "A",
        "name": "真实计算强证据",
        "criteria": "真实 Gaussian / Multiwfn / NBO / QTAIM / NCI 结果，计算收敛，频率正确，TS 仅有一个合理虚频，IRC 连接正确，并有 provenance。",
        "paper_ready": "可以作为论文结论，但仍需说明模型、方法、基组和误差边界。",
    },
    {
        "level": "B",
        "name": "真实实验强证据",
        "criteria": "GPC、MFR、gel、SAOS、FTIR、NMR、DSC、TEM、介电谱等真实实验数据支持，且样品、工艺和表征条件明确。",
        "paper_ready": "可以作为论文结论，建议与计算或对照实验交叉验证。",
    },
    {
        "level": "C",
        "name": "文献/用户输入线索",
        "criteria": "文献线索或用户输入数据，尚未在当前体系中复现。",
        "paper_ready": "只能作为研究依据或待验证假说，不能单独作为最终结论。",
    },
    {
        "level": "D",
        "name": "示例/推断假说",
        "criteria": "mock/example 数据、趋势假说或演示值。",
        "paper_ready": "不能作为真实科学结论，只能用于软件演示和设计验证。",
    },
]


CORE_FORMULAS = {
    "units": {
        "hartree_to_kcal_mol": 627.509474,
        "hartree_to_kj_mol": 2625.499638,
        "hartree_to_ev": 27.211386245988,
        "R_kcal_mol_K": 0.00198720425864083,
        "default_temperature_K": 350.0,
    },
    "coordination_insertion": [
        "ΔGbind = G(complex) − G(fragment A) − G(fragment B)",
        "ΔGpoison = G(O→Ti complex) − G(C=C π-complex)",
        "ΔGπ = G(π-complex) − G(free active site + monomer)",
        "ΔG‡insert = G(insertion TS) − G(free active site + monomer)",
        "ΔG‡complex = G(insertion TS) − G(π-complex)",
        "krel = exp(−ΔΔG‡ / RT)",
    ],
    "bde": [
        "BDE(Si–C) = G(R•) + G(•Si fragment) − G(R–Si)",
        "BDE(Si–O) = G(R•) + G(•O–Si fragment) − G(R–O–Si)",
        "BDE(RO–OR) = G(2RO•) − G(RO–OR)",
    ],
    "radical_kinetics": [
        "d[RO•]/dt = 2kd[ROOR] − kH[RO•][PP-H] − kside[RO•]",
        "d[PP•]/dt = kH[RO•][PP-H] − kβ[PP•] − 2krec[PP•]^2 − kg[PP•][M] − kc[PP•][coagent]",
        "R_scission = kβ[PP•]",
        "R_branch = krec[PP•]^2 + kg[PP•][M] + kc[PP•][coagent]",
        "S_LCB = R_branch / (R_branch + R_scission + R_oxidation)",
    ],
    "boltzmann_average": [
        "w_i = exp(−G_i / RT) / Σ_j exp(−G_j / RT)",
        "<P> = Σ_i w_i P_i",
    ],
}


MECHANISM_RULES = [
    {"name": "Ti 毒化", "rule": "ΔGpoison > +5: 生产性 C=C 插入占优；0 至 +5: 配位竞争；<0: Ti 活性中心存在甲氧基毒化风险。"},
    {"name": "MCSOMe 候选", "rule": "ΔGpoison > 0 且 ΔG‡insert 接近 DCS 且 BDE(Si–C) 安全时，才可判为优先平衡候选。"},
    {"name": "DMOS 风险", "rule": "n(O)→Ti 强且 ΔGpoison < 0 时，判为 DMOS 强 O→Ti 毒化风险。"},
    {"name": "TEA 作用", "rule": "ΔGbind 适中为负且 C=C π-complex 仍稳定时为有效预组织；ΔGbind 过强为负且 π-complex 不稳定时为过度捕获。"},
    {"name": "Si–O 削弱", "rule": "r(Si–O) 增大、WBI 降低、ν(Si–O) 红移时，判为 Lewis 酸配位削弱 Si–O。"},
    {"name": "Si–C 失效", "rule": "BDE(Si–C) 低或 radical-near-SiC scission barrier 低时，判为连接臂失效风险。"},
    {"name": "PP 降解", "rule": "Mw 降低、MFR 升高且 gel 低时，判为 PP β-断裂降解主导。"},
    {"name": "有效 LCB", "rule": "SAOS 低频增强、strain hardening 且 gel 低至中等时，判为有效长链支化或轻度交联。"},
    {"name": "氧化风险", "rule": "carbonyl_index 与 dielectric_loss 同时增大时，判为氧化羰基副反应风险。"},
]


QUANTUM_TASKS = [
    "单体 opt/freq/NBO",
    "29Si GIAO NMR",
    "TEA complex counterpoise",
    "Al←O complex",
    "Al···Cl complex",
    "Ti C=C π-complex",
    "O→Ti poison complex",
    "insertion TS",
    "insertion IRC",
    "hydrolysis TS",
    "condensation TS",
    "Si–O BDE",
    "Si–C BDE",
    "RO–OR homolysis",
    "RO• H-abstraction",
    "PP radical β-scission TS",
    "PP radical recombination",
    "PP radical + coagent grafting",
    "cube generation",
    "Multiwfn script generation",
]


QUANTUM_TASK_FIELDS = ["计算目的", "模型选择", "方法与基组建议", "电荷与自旋多重度", "需要检查的输出", "可靠性判据", "可能失败的原因", "后续验证实验"]


ELECTRONIC_ANALYSIS_REQUIREMENTS = [
    {"name": "电子云密度 ρ(r)", "formula": "ρ(r) = Σ_i n_i |ψ_i(r)|²", "checks": ["电子富集区域", "键区电子密度", "差分电子密度", "络合前后电子转移"]},
    {"name": "前线轨道 HOMO/LUMO", "checks": ["HOMO 是否分布在 OMe 氧", "HOMO 是否分布在 C=C", "LUMO 是否集中在 Ti", "TEA 络合前后 gap 是否变化"]},
    {"name": "ESP 静电势", "checks": ["OMe O 附近 ESPmin", "C=C 区域电势", "Si 附近正电势", "Al/Ti 对 Lewis 碱位点的吸引"]},
    {"name": "NBO", "checks": ["n(O)→Al", "n(O)→Ti", "n(Cl)→Al", "π(C=C)→Ti", "σ(Si–O)/σ*(Si–O)", "σ(Si–C)/σ*(Si–C)"]},
    {"name": "QTAIM", "checks": ["Si–O BCP", "Si–C BCP", "Al–O BCP", "Al–Cl BCP", "Ti–O BCP", "Ti–C BCP", "forming C–C BCP", "Si–O–Si BCP"]},
    {"name": "NCI/RDG", "checks": ["蓝色强吸引", "绿色弱范德华", "红色空间排斥", "OMe 是否在 TS 中造成排斥", "PP/EPC 界面弱相互作用"]},
]


PEROXIDE_ANALYSIS_REQUIREMENTS = {
    "carbonyl_taxonomy": [
        "过氧化物羰基：影响 O–O 分解、自由基类型、脱羧和副产物。",
        "接枝单体羰基：影响极性、界面作用、介电损耗和陷阱。",
        "氧化副产物羰基：代表热氧老化、降解和电性能风险。",
    ],
    "species": ["DCP", "BPO", "TBPB", "L-101", "TBPEH", "DTBP"],
    "comparison_dimensions": ["O–O BDE", "半衰期", "分解温度", "初级自由基类型", "是否含羰基", "H 抽提能力", "PP β-断裂风险", "coagent 捕获可能性", "氧化副产物风险", "是否适合低温固相", "是否适合熔融挤出"],
}


EXPERIMENTAL_MAPPING = [
    {"method": "GPC / MFR", "logic": "Mw 下降 + MFR 上升 = 降解；高分子量肩峰 = LCB / 轻度交联可能。"},
    {"method": "gel fraction", "logic": "gel 低 = 未交联或仅 LCB；gel 中等 = 轻度交联；gel 高 = 过凝胶。"},
    {"method": "SAOS / 拉伸流变", "logic": "低频储能模量增强、松弛时间变长、strain hardening = LCB / 轻度交联证据。"},
    {"method": "FTIR", "logic": "carbonyl index = 氧化副反应；Si–O–Si = 硅氧缩合；Si–OH = 水解中间体；Si–Cl / Si–OMe 残留 = 后反应不完全。"},
    {"method": "29Si NMR", "logic": "判断 Si–Cl、Si–OH、Si–O–Si、Si–C 环境变化。"},
    {"method": "DSC / XRD", "logic": "判断结晶温度、结晶度、晶体结构和 LCB 对结晶的影响。"},
    {"method": "TEM / SEM / AFM", "logic": "判断 EPC 相畴、界面稳定、退火粗化和 PP-H-EPC 桥联效果。"},
    {"method": "介电谱 / 击穿 / 空间电荷", "logic": "判断羰基介电损耗、LCB 相形态改善、深陷阱增强和空间电荷抑制。"},
]


THINKING_WORKFLOW = ["四轴定位", "关键反应键", "关键能量", "关键电子结构证据", "关键实验判据", "可证伪性", "下一步最小实验或最小计算"]


OUTPUT_FORMAT_REQUIREMENTS = {
    "research_answer": ["结论先行", "机制拆解", "关键公式", "量子化学指标", "实验判据", "风险与反例", "下一步最小任务", "可写入月度报告的一段话"],
    "report": ["摘要", "研究背景", "文献基础", "科学问题", "机制模型", "计算方法", "实验方法", "结果讨论", "判据体系", "风险分析", "下一步工作", "结论"],
    "prompt": ["可直接复制", "排版清晰", "层级明确", "不碎片化", "不省略科学判据", "不只写漂亮话"],
}


CAPABILITY_STANDARDS = [
    "能批判已有博士论文的局限。",
    "能把已有论文推进到更高级机制模型。",
    "能把 Si–O、Si–C、C=C、PP 自由基统一分析。",
    "能用 Gaussian16 设计计算任务。",
    "能用 Multiwfn-like 思维解释电子云、轨道、ESP、QTAIM、NCI。",
    "能把过氧化物降解/交联问题转化为自由基动力学。",
    "能把高分子相形态和流变性能接回微观反应。",
    "能判断哪些结论是强证据，哪些只是弱推断。",
    "能提出最小可证伪实验。",
    "能形成可写进月度报告、技术报告、论文和软件需求文档的表达。",
]


FORBIDDEN_BEHAVIORS = [
    "空泛吹嘘",
    "只给概念不落到指标",
    "只说可能但不给验证方案",
    "把 Si–O 和 Si–C 混为一谈",
    "把过氧化物简单称为交联剂",
    "把羰基当成单一变量",
    "只看 MFR 判断降解",
    "只看 gel 判断交联",
    "只看 FTIR 判断接枝",
    "没有数据却给确定结论",
    "忽略单位",
    "忽略自旋多重度",
    "忽略过渡态虚频和 IRC",
    "忽略 mock 数据标记",
    "忽略实验可验证性",
]


FALSIFIABLE_TASK_TEMPLATE = {
    "minimal_calculation": ["计算对象", "Gaussian 任务类型", "方法/基组", "电荷/自旋多重度", "关键输出字段", "成功判据", "相反结果说明"],
    "minimal_experiment": ["样品", "工艺变量", "表征方法", "关键观测量", "支持该假说的结果", "反驳该假说的结果"],
    "minimal_software": ["新增 API", "数据库字段", "UI 图表", "测试用例", "报告表述"],
}


SOFTWARE_MAPPING = [
    {"type": "能量判断", "mapping": "API 输入/输出、单位、公式、中文错误提示和测试断言。"},
    {"type": "parser 判断", "mapping": "normalized JSON 字段、单位、解析质量、warnings 和 provenance。"},
    {"type": "机制判据", "mapping": "decision-engine 规则、阈值、颜色标签、中文解释和 mock 数据边界。"},
    {"type": "实验结论", "mapping": "实验数据表字段、导入模板、图表、统计关联和可靠性等级。"},
    {"type": "报告内容", "mapping": "中文报告章节、结论模板、缺失数据声明和后续验证建议。"},
]


REPORT_DRIVEN_EXTENSION = {
    "title": "报告驱动闭环扩展",
    "source_role": "用户提供的 SiO/SiC/过氧化物/PP 长链支化交联降解报告只能作为 C 级报告线索导入。",
    "required_topics": [
        "1. Si–O 水解缩合活性",
        "2. Si–C 侧链连接稳定性",
        "3. Ziegler-Natta 催化剂环境",
        "4. 三乙基铝 (TEA) 预组织",
        "5. Ti 毒化与配位竞争",
        "6. 过氧化物与自由基网络",
        "7. PP β-scission 断链",
        "8. LCB (长链支化)",
        "9. 交联竞争",
        "10. 降解与失效表征",
        "11. 乙烯/等规度/结晶度微相窗口",
        "12. 羰基效应三分法",
    ],
    "evidence_policy": "报告抽取结果必须标注 evidence_level=C、data_source=报告线索、paper_ready=需要补充验证。",
    "software_targets": [
        "POST /api/literature/import-report-docx",
        "GET /api/literature/report-knowledge",
        "POST /api/reports/generate",
        "MCP generate_top_scientist_prompt",
    ],
}


def top_scientist_protocol() -> dict[str, Any]:
    return {
        "name": "顶尖科学家能力进化协议",
        "language": "zh-CN",
        "research_objects": RESEARCH_OBJECTS,
        "scientific_principles": SCIENTIFIC_PRINCIPLES,
        "four_axis_protocol": FOUR_AXIS_PROTOCOL,
        "evidence_levels": EVIDENCE_LEVELS,
        "core_formulas": CORE_FORMULAS,
        "mechanism_rules": MECHANISM_RULES,
        "quantum_tasks": QUANTUM_TASKS,
        "quantum_task_fields": QUANTUM_TASK_FIELDS,
        "electronic_analysis_requirements": ELECTRONIC_ANALYSIS_REQUIREMENTS,
        "peroxide_analysis_requirements": PEROXIDE_ANALYSIS_REQUIREMENTS,
        "experimental_mapping": EXPERIMENTAL_MAPPING,
        "thinking_workflow": THINKING_WORKFLOW,
        "output_format_requirements": OUTPUT_FORMAT_REQUIREMENTS,
        "capability_standards": CAPABILITY_STANDARDS,
        "forbidden_behaviors": FORBIDDEN_BEHAVIORS,
        "falsifiable_task_template": FALSIFIABLE_TASK_TEMPLATE,
        "software_mapping": SOFTWARE_MAPPING,
        "report_driven_extension": REPORT_DRIVEN_EXTENSION,
        "provenance": "平台内置科研工作协议；用于约束 prompt、报告、判据和软件实现，不代表真实计算结果。",
    }


def build_top_scientist_prompt(topic: str, include_safety: bool = True) -> dict[str, Any]:
    subject = topic.strip() or "Si–O / Si–C / Ziegler–Natta / PP 自由基机理"
    safety = "不执行 Gaussian、cubegen、Multiwfn；上传文件只读解析；mock/example 数据不得作为真实结论。" if include_safety else "按用户配置执行安全边界。"
    prompt = dedent(
        f"""
        # 顶尖科学家能力进化模式

        研究主题：{subject}

        你必须把该问题推进到“可计算、可证伪、可实验验证、可软件化执行、可写成论文”的层级。

        ## 四轴定位
        1. 单体轴：DCS / MCSOMe / DMOS、Si–O、Si–C、Si–Cl、C=C。
        2. 催化剂轴：Ti active site、MgCl2、TEA、AlEt3、AlEt2Cl、internal donor。
        3. 自由基轴：RO–OR、RO•、PP•、EPC•、coagent、O2。
        4. 微相轴：iPP 晶区、PP 非晶相、EPC 富乙烯相、PP/EPC 界面。

        ## 必须使用的公式
        ΔGbind = G(complex) − G(fragment A) − G(fragment B)
        ΔGpoison = G(O→Ti complex) − G(C=C π-complex)
        ΔG‡insert = G(insertion TS) − G(free active site + monomer)
        krel = exp(−ΔΔG‡ / RT)
        BDE(Si–C) = G(R•) + G(•Si fragment) − G(R–Si)
        R_scission = kβ[PP•]
        S_LCB = R_branch / (R_branch + R_scission + R_oxidation)

        ## 必须覆盖的量子化学任务
        单体 opt/freq/NBO、29Si GIAO NMR、TEA counterpoise、Al←O、Al···Cl、Ti C=C π-complex、
        O→Ti poison complex、insertion TS/IRC、hydrolysis/condensation TS、Si–O/Si–C BDE、
        RO–OR homolysis、RO• H-abstraction、PP radical β-scission TS、cube generation、Multiwfn script generation。

        ## 电子结构与波函数分析
        必须检查电子云密度 ρ(r)、HOMO/LUMO、ESP、NBO、QTAIM、NCI/RDG，并区分蓝色强吸引、
        绿色弱范德华和红色空间排斥。

        ## 过氧化物与羰基三分法
        过氧化物羰基、接枝单体羰基、氧化副产物羰基必须分开讨论；DCP、BPO、TBPB、L-101、TBPEH、DTBP
        需按 O–O BDE、半衰期、初级自由基类型、H 抽提能力、β-scission 风险、coagent 捕获和氧化副产物风险比较。

        ## 实验表征映射
        GPC/MFR、gel、SAOS/拉伸流变、FTIR、29Si NMR、DSC/XRD、TEM/SEM/AFM、介电谱/空间电荷必须接回机制判断。

        ## 证据等级
        A级：真实收敛计算、正确频率/TS/IRC、清晰 provenance。
        B级：真实实验数据，样品、工艺和表征条件明确。
        C级：文献线索或用户输入，尚未在当前体系复现。
        D级：示例数据、机理推断或 mock 数据，不能作为真实结论。

        ## 每个判断必须输出
        证据等级、数据来源、可靠性、是否可作为论文结论、最小计算任务、最小实验任务、最小软件任务。

        ## 软件化落地
        将能量判断转化为 API/单位/公式/测试断言；将 parser 判断转化为 normalized JSON/warnings/provenance；
        将机制判据转化为 decision-engine 阈值、颜色标签和中文解释；将实验结论转化为数据表字段和报告章节。

        ## 报告驱动闭环
        用户提供的 SiO/SiC/过氧化物/PP 长链支化交联降解报告只能作为 C 级报告线索导入。
        必须把报告线索映射到 Si–C 稳定性、PP β-scission、羰基三分法、乙烯/等规度/结晶度窗口、
        最小可证伪任务和软件 API/测试/报告章节；不得把报告线索写成 A/B 级真实结论。

        安全边界：{safety}
        """
    ).strip()
    return {
        "prompt": prompt,
        "protocol": top_scientist_protocol(),
        "language": "zh-CN",
        "provenance": "由顶尖科学家协议生成器创建；属于科研工作流约束，不是计算结果。",
    }
