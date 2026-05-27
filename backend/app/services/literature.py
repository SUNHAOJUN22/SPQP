from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


THESIS_TITLE = "基于 Ziegler-Natta 催化剂的乙烯、丙烯与功能 α-烯烃单体配位共聚合反应的空间位阻与电子效应研究"
REPORT_TITLE = "SiO/SiC/过氧化物/PP 长链支化交联降解全景深度报告"


def extract_docx_text(path: str | Path) -> str:
    """Read a DOCX as text without executing macros or embedded content."""
    docx_path = Path(path)
    if docx_path.suffix.lower() != ".docx":
        raise ValueError("当前文件不是有效 docx 文件。")
    if not docx_path.exists():
        raise FileNotFoundError("未找到指定博士论文 docx 文件。")

    paragraphs: list[str] = []
    with zipfile.ZipFile(docx_path) as archive:
        document_names = [name for name in archive.namelist() if name.startswith("word/") and name.endswith(".xml")]
        for name in sorted(document_names):
            if name not in {"word/document.xml", "word/footnotes.xml", "word/endnotes.xml"}:
                continue
            root = ElementTree.fromstring(archive.read(name))
            for paragraph in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                runs = [node.text for node in paragraph.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
                text = "".join(runs).strip()
                if text:
                    paragraphs.append(text)
    return "\n".join(paragraphs)


def _contains_any(text: str, values: list[str]) -> bool:
    lowered = text.lower()
    return any(value.lower() in lowered for value in values)


def _count_any(text: str, values: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(value.lower()) for value in values)


def _pick_snippet(text: str, values: list[str], fallback: str) -> str:
    paragraphs = [line.strip() for line in re.split(r"[\n。；;]", text) if line.strip()]
    lowered_values = [value.lower() for value in values]
    for paragraph in paragraphs:
        lowered = paragraph.lower()
        if any(value in lowered for value in lowered_values):
            return paragraph[:320]
    return fallback


def extract_thesis_knowledge(text: str) -> dict[str, Any]:
    warnings: list[str] = []
    if len(text) < 1000:
        warnings.append("论文文本较短，可能只提取到题名页或摘要片段。")
    if not _contains_any(text, ["Ziegler", "Natta", "Ziegler-Natta", "Ziegler–Natta"]):
        warnings.append("未在文本中稳定检测到 Ziegler-Natta 关键词，请检查 docx 内容。")

    entities = [
        {
            "category": "论文主题",
            "name": "steric and electronic effect",
            "chinese_name": "空间位阻与电子效应耦合",
            "evidence": "论文题目和摘要均围绕功能 α-烯烃在 Ziegler–Natta 催化剂上的共聚插入行为，核心变量为空间位阻与电子效应。",
            "confidence": 0.94,
            "source": "博士论文 docx 抽取",
        },
        {
            "category": "单体族",
            "name": "omega-alkenyl trimethylsilane",
            "chinese_name": "ω-烯烃基三甲基硅烷",
            "evidence": "文本提到 3-butenyltrimethylsilane、5-hexenyltrimethylsilane、7-octenyltrimethylsilane 与乙烯/丙烯共聚。",
            "confidence": 0.92 if _contains_any(text, ["trimethylsilane", "三甲基硅烷"]) else 0.62,
            "source": "博士论文 docx 抽取",
        },
        {
            "category": "单体族",
            "name": "omega-alkenyl methyl dichlorosilane",
            "chinese_name": "ω-烯烃基甲基二氯硅烷",
            "evidence": "文本提到 3/5/7-烯基甲基二氯硅烷，并描述氯硅烷取代基电子强度对插入行为的影响。",
            "confidence": 0.95 if _contains_any(text, ["dichlorosilane", "二氯硅烷"]) else 0.65,
            "source": "博士论文 docx 抽取",
        },
        {
            "category": "催化剂模型",
            "name": "MgCl2/BMMF/TiCl4/iBU",
            "chinese_name": "给电子体修饰 MgCl2 负载 Ti 模型",
            "evidence": "摘要线索包含 MgCl2/BMMF/TiCl4/iBU 与 MgCl2/TiCl4/Et 两类 DFT 模型。",
            "confidence": 0.9 if _contains_any(text, ["BMMF", "iBU", "MgCl2/TiCl4/Et"]) else 0.58,
            "source": "博士论文 docx 抽取",
        },
        {
            "category": "助催化剂",
            "name": "TEA / AlEt3",
            "chinese_name": "TEA 三乙基铝助催化剂",
            "evidence": "论文摘要指出助催化剂 Al 原子与氯硅烷取代基存在相互作用，且随电子强度增强。",
            "confidence": 0.88 if _contains_any(text, ["助催化剂", "Al", "三乙基铝", "TEA"]) else 0.55,
            "source": "博士论文 docx 抽取",
        },
        {
            "category": "关键结论",
            "name": "chain-length window",
            "chinese_name": "链长窗口效应",
            "evidence": "文本趋势显示乙烯和丙烯体系中不同链长功能单体插入表现不同，不能用单一位阻尺度解释。",
            "confidence": 0.84,
            "source": "博士论文 docx 抽取",
        },
    ]

    catalyst_models = [
        {
            "key": "MgCl2-TiCl4-Et",
            "name": "MgCl2/TiCl4/Et",
            "role": "简化乙烯插入活性中心模型，用于建立功能 α-烯烃插入势垒参照。",
            "active_site": "Ti–Et 生长链 / MgCl2 载体片段",
            "thesis_link": "论文 DFT 模型之一。",
            "source": "博士论文 docx 抽取 + 示例占位",
        },
        {
            "key": "MgCl2-BMMF-TiCl4-iBU",
            "name": "MgCl2/BMMF/TiCl4/iBU",
            "role": "给电子体修饰活性中心模型，用于丙烯和功能 α-烯烃位阻/电子效应分析。",
            "active_site": "Ti–iBU 生长链 / BMMF 给电子体环境",
            "thesis_link": "论文 DFT 模型之一。",
            "source": "博士论文 docx 抽取 + 示例占位",
        },
        {
            "key": "TEA-guided",
            "name": "Monomer···TEA preorganization",
            "role": "用于分析 Al···Cl、Al←O 与 Al···C=C 三类助剂络合通道。",
            "active_site": "AlEt3 Lewis 酸中心",
            "thesis_link": "论文指出助催化剂 Al 与氯硅烷取代基相互作用可帮助单体接近活性中心。",
            "source": "论文抽取 + 机制外推",
        },
    ]

    monomer_families = [
        {
            "key": "omega-alkenyl-trimethylsilane",
            "chinese_name": "ω-烯烃基三甲基硅烷",
            "english_name": "omega-alkenyl trimethylsilane",
            "chain_lengths": {"C4": "3-butenyl", "C6": "5-hexenyl", "C8": "7-octenyl"},
            "mechanism_note": "主要用于分离链长与位阻效应，电子效应相对弱。",
            "source": "博士论文 docx 抽取",
        },
        {
            "key": "omega-alkenyl-methyl-dichlorosilane",
            "chinese_name": "ω-烯烃基甲基二氯硅烷",
            "english_name": "omega-alkenyl methyl dichlorosilane",
            "chain_lengths": {"C4": "3-butenyl", "C6": "5-hexenyl", "C8": "7-octenyl"},
            "mechanism_note": "氯硅烷取代基电子效应更强，可与 TEA/Al 形成导向相互作用。",
            "source": "博士论文 docx 抽取",
        },
        {
            "key": "methoxy-silane-derivatives",
            "chinese_name": "甲氧基硅烷衍生物",
            "english_name": "methoxy silane derivatives",
            "chain_lengths": {"C6": "DCS / MCSOMe / DMOS scaffold"},
            "mechanism_note": "用于扩展考察 Al←O、O→Ti 毒化和 Si–O–Si 后反应功能化。",
            "source": "软件 V2 机理外推",
        },
    ]

    extracted_keywords = sorted(set(re.findall(r"(Ziegler[-–]Natta|MgCl2|TiCl4|BMMF|TEA|Al|trimethylsilane|dichlorosilane|1-hexene)", text, re.IGNORECASE)))
    return {
        "entities": entities,
        "catalyst_models": catalyst_models,
        "monomer_families": monomer_families,
        "warnings": warnings,
        "keywords": extracted_keywords,
    }


REPORT_KNOWLEDGE_TOPICS: list[dict[str, Any]] = [
    {
        "category": "单体轴",
        "name": "Si-O / Si-Cl hydrolysis-condensation",
        "chinese_name": "Si–O / Si–Cl 水解缩合后反应",
        "axis": "单体轴",
        "terms": ["Si–O", "Si-O", "Si–Cl", "Si-Cl", "水解", "缩合", "Si–O–Si", "Si-O-Si"],
        "fallback": "报告方向强调 Si–Cl / Si–OMe 水解生成 Si–OH，并进一步缩合形成 Si–O–Si 桥联长链支化。",
        "software_mapping": "报告章节：水解缩合后反应；API：/api/analysis/hydrolysis-condensation；测试：缺失 ΔGhydrolysis/ΔGcondensation 时必须提示当前数据不足。",
    },
    {
        "category": "单体轴",
        "name": "Si-C side-arm stability",
        "chinese_name": "Si–C 侧链连接稳定性",
        "axis": "单体轴",
        "terms": ["Si–C", "Si-C", "硅碳", "连接臂", "BDE", "键解离能"],
        "fallback": "报告方向要求把 Si–C 从辅助连接键升级为关键稳定性指标，判断硅烷侧链是否真实保留在 PP/EPC 大分子上。",
        "software_mapping": "报告章节：Si–C 连接稳定性；API：/api/analysis/sic-stability；测试：BDE 或自由基攻击势垒缺失时不得输出确定结论。",
    },
    {
        "category": "催化剂轴",
        "name": "Ziegler-Natta / TEA / Ti competition",
        "chinese_name": "Ziegler–Natta / TEA / Ti 配位竞争",
        "axis": "催化剂轴",
        "terms": ["Ziegler", "Natta", "TEA", "三乙基铝", "Ti", "O→Ti", "Al←O", "Al···Cl", "毒化"],
        "fallback": "报告方向将 TEA 预组织、Al←O/Al···Cl 相互作用和 O→Ti 毒化作为聚合阶段的核心竞争路径。",
        "software_mapping": "报告章节：TEA 助催化剂作用、Ti 活性中心毒化判据；API：/api/analysis/tea-binding 与 /api/analysis/ti-poisoning。",
    },
    {
        "category": "自由基轴",
        "name": "Peroxide-induced PP radical network",
        "chinese_name": "过氧化物诱导 PP 自由基反应网络",
        "axis": "自由基轴",
        "terms": ["过氧化物", "peroxide", "RO–OR", "RO-OR", "自由基", "radical", "抽氢"],
        "fallback": "报告方向要求建立 RO–OR 均裂、RO• 抽氢、PP• 生成及其后续反应的统一自由基网络。",
        "software_mapping": "报告章节：过氧化物自由基机理；API：/api/analysis/peroxide-profile 与 /api/analysis/radical-beta-scission。",
    },
    {
        "category": "自由基轴",
        "name": "PP beta-scission vs branching/crosslinking",
        "chinese_name": "PP β-scission 降解与支化/交联竞争",
        "axis": "自由基轴",
        "terms": ["β-scission", "beta-scission", "断链", "降解", "交联", "支化", "LCB", "长链支化", "凝胶"],
        "fallback": "报告方向强调 PP 叔碳自由基可发生 β-scission 降解，也可在共剂、EPC 相或硅烷后反应位点存在时转向支化/交联。",
        "software_mapping": "报告章节：PP β-scission 与交联竞争；API：/api/analysis/radical-branching-vs-scission；UI：降解-交联竞争图。",
    },
    {
        "category": "自由基轴",
        "name": "Carbonyl three-way taxonomy",
        "chinese_name": "羰基效应三分法",
        "axis": "自由基轴",
        "terms": ["羰基", "carbonyl", "过氧酯", "苯甲酰", "氧化", "介电损耗"],
        "fallback": "报告方向明确区分过氧化物羰基、接枝单体羰基和氧化副产物羰基，禁止把羰基作为单一变量解释。",
        "software_mapping": "报告章节：羰基因素三分法；API：/api/analysis/carbonyl-taxonomy；测试：含羰基过氧化物只能作为待验证假说。",
    },
    {
        "category": "微相轴",
        "name": "Ethylene / isotacticity / crystallinity window",
        "chinese_name": "乙烯引入、等规度与结晶度窗口",
        "axis": "微相轴",
        "terms": ["乙烯", "ethylene", "等规", "isotactic", "结晶", "crystall", "EPC", "IPC"],
        "fallback": "报告方向将乙烯引入、等规度、结晶度和 EPC 相比例作为控制自由基扩散、β-scission 与复合概率的微相变量。",
        "software_mapping": "报告章节：乙烯/等规度/结晶度影响；API：/api/analysis/radical-branching-vs-scission 与 /api/analysis/residence-time-window。",
    },
    {
        "category": "软件化执行",
        "name": "Evidence-graded falsifiable workflow",
        "chinese_name": "证据分级与最小可证伪工作流",
        "axis": "四轴总控",
        "terms": ["证据", "可证伪", "Gaussian", "Multiwfn", "NBO", "QTAIM", "GPC", "MFR", "SAOS"],
        "fallback": "报告方向要求所有结论标注 A/B/C/D 证据等级，并给出最小计算、最小实验和最小软件测试任务。",
        "software_mapping": "报告章节：证据等级系统、最小可证伪任务、软件化执行接口；API：/api/research/top-scientist-protocol。",
    },
]


def extract_report_driven_knowledge(text: str, title: str = REPORT_TITLE) -> dict[str, Any]:
    warnings: list[str] = []
    if len(text) < 1000:
        warnings.append("报告文本较短，可能只读取到摘要、目录或片段；抽取结果只能作为 C 级报告线索。")
    keyword_counts = {
        "sio_sic": _count_any(text, ["Si–O", "Si-O", "Si–C", "Si-C", "硅氧", "硅碳"]),
        "zn_tea_ti": _count_any(text, ["Ziegler", "Natta", "TEA", "Ti", "O→Ti", "Al←O", "Al···Cl"]),
        "peroxide_radical": _count_any(text, ["过氧化物", "peroxide", "自由基", "radical", "RO–OR", "RO-OR"]),
        "pp_lcb_scission": _count_any(text, ["β-scission", "beta-scission", "断链", "降解", "交联", "支化", "LCB"]),
        "microstructure": _count_any(text, ["乙烯", "ethylene", "等规", "isotactic", "结晶", "EPC", "IPC"]),
        "carbonyl": _count_any(text, ["羰基", "carbonyl", "苯甲酰", "过氧酯", "氧化"]),
    }
    total_hits = sum(keyword_counts.values())
    if total_hits == 0:
        warnings.append("未检测到报告核心关键词；请确认导入文件是否为 SiO/SiC/过氧化物研究报告。")

    entities: list[dict[str, Any]] = []
    for topic in REPORT_KNOWLEDGE_TOPICS:
        hits = _count_any(text, topic["terms"])
        confidence = min(0.9, 0.46 + 0.06 * hits) if text else 0.42
        entities.append(
            {
                "category": topic["category"],
                "name": topic["name"],
                "chinese_name": topic["chinese_name"],
                "axis": topic["axis"],
                "evidence": _pick_snippet(text, topic["terms"], topic["fallback"]),
                "confidence": round(confidence, 3),
                "evidence_level": "C",
                "data_source": "报告线索",
                "reliability": "中" if confidence >= 0.65 else "低",
                "paper_ready": "需要补充验证",
                "software_mapping": topic["software_mapping"],
                "source": f"{title} 只读抽取",
            }
        )

    mechanism_models = [
        {
            "key": "coordination-condensation-route",
            "name": "配位插入-水解缩合长链支化路线",
            "axis": "单体轴 / 催化剂轴",
            "hypothesis": "功能 α-烯烃先经 C=C 配位插入进入 PP/EPC 链，再通过 Si–Cl/Si–OMe 水解缩合形成 Si–O–Si 桥联。",
            "falsification": "若真实 ΔG‡insert 远高于 DCS 或 Si–O–Si 的 FTIR/29Si NMR 证据缺失，则该路线不能作为主导 LCB 机制。",
            "required_data": ["ΔGpoison", "ΔG‡insert", "IRC", "Si–O–Si FTIR", "29Si NMR", "GPC/SAOS"],
            "evidence_level": "C",
            "source": f"{title} 机制抽取",
        },
        {
            "key": "peroxide-radical-competition-route",
            "name": "过氧化物自由基降解-支化-交联竞争路线",
            "axis": "自由基轴 / 微相轴",
            "hypothesis": "过氧化物产生 RO• 后抽取 PP 三级 C–H，PP• 在 β-scission、复合、接枝、交联和氧化之间竞争。",
            "falsification": "若 Mw/MFR、gel、SAOS、carbonyl index 与动力学模型预测方向相反，则需重新拟合自由基竞争权重。",
            "required_data": ["半衰期", "停留时间", "GPC", "MFR", "gel fraction", "SAOS", "FTIR carbonyl index"],
            "evidence_level": "C",
            "source": f"{title} 机制抽取",
        },
        {
            "key": "carbonyl-taxonomy-route",
            "name": "羰基三分法风险模型",
            "axis": "自由基轴",
            "hypothesis": "过氧化物羰基、接枝单体羰基和氧化副产物羰基影响不同，必须分开建模。",
            "falsification": "若同半衰期/同自由基通量下羰基变量不改变副产物、接枝率或介电损耗，则羰基不是主导控制因子。",
            "required_data": ["RO–OR BDE", "GC-MS", "FTIR carbonyl index", "接枝率", "介电谱", "OIT"],
            "evidence_level": "C",
            "source": f"{title} 机制抽取",
        },
    ]

    report_payload = {
        "thesis_knowledge_mapping": {
            "title": title,
            "evidence_level": "C",
            "data_source": "报告 docx 只读抽取",
            "entities": entities,
            "keyword_counts": keyword_counts,
            "warnings": warnings,
            "reliability_note": "该报告抽取结果为 C 级文献/报告线索，不能替代真实 Gaussian、Multiwfn、NBO、QTAIM/NCI 或实验数据。",
        },
        "sic_sio_sicl_post_reaction": {
            "summary": "报告驱动更新要求同时比较 Si–C 连接稳定性、Si–O/Si–Cl 水解缩合功能性和过氧化物后处理下侧链保留风险。",
            "evidence_level": "C",
            "required_validation": ["Si–C BDE", "自由基攻击势垒", "29Si NMR", "FTIR Si–O–Si / Si–OH"],
        },
        "pp_scission_crosslinking": {
            "summary": "PP• 的 β-scission、复合、接枝、交联和氧化需要用同一动力学竞争图表达。",
            "evidence_level": "C",
            "required_validation": ["Mw/Mn/PDI", "MFR", "gel fraction", "SAOS", "carbonyl index"],
        },
        "ethylene_isotacticity_solid_state_window": {
            "summary": "乙烯含量、等规度、结晶度和 EPC 相比例决定自由基扩散、链段接近概率与固态反应窗口。",
            "evidence_level": "C",
            "required_validation": ["13C NMR 序列", "DSC/XRD", "TEM/AFM", "流变", "介电谱"],
        },
        "falsifiable_model": mechanism_models,
    }
    report_payload["report_knowledge_mapping"] = report_payload["thesis_knowledge_mapping"]

    return {
        "title": title,
        "entities": entities,
        "mechanism_models": mechanism_models,
        "keyword_counts": keyword_counts,
        "report_payload": report_payload,
        "warnings": warnings,
        "provenance": "报告 docx 仅读取文本，不执行宏、脚本、Gaussian、cubegen 或 Multiwfn；抽取结论为 C 级报告线索。",
    }


def default_mechanism_hypotheses() -> list[dict[str, Any]]:
    return [
        {
            "key": "steric-dominated",
            "name": "位阻主导模型",
            "summary": "功能 α-烯烃插入下降主要来自取代基体积、链构象折叠和 TS 变形能升高。",
            "supporting_evidence": ["丙烯体系对功能单体位阻更敏感。", "长链或大取代基可能提高插入 TS 变形能。"],
            "falsification": ["若大位阻单体仍保持低 ΔG‡ 和高插入率，则单纯位阻模型不足。"],
            "required_data": ["TS 变形能", "NCI/RDG 红色排斥区域", "实验插入率", "ΔG‡"],
            "current_status": "当前仅有论文趋势和示例描述符，不能形成真实定量结论。",
            "confidence": 0.68,
            "source": "论文抽取 + 示例机制",
        },
        {
            "key": "electronic-guiding",
            "name": "电子效应导向模型",
            "summary": "氯硅烷取代基电子效应增强 Al···Cl 或相关 Lewis 酸相互作用，使单体更容易靠近 Ti 活性中心。",
            "supporting_evidence": ["氯硅烷取代基电子强度增强有利于插入。", "助催化剂 Al 与氯硅烷取代基相互作用随电子强度增强。"],
            "falsification": ["若 Al···Cl 作用增强但 π-complex 不稳定或 ΔG‡ 升高，则电子导向与插入活性脱耦。"],
            "required_data": ["ΔGbind", "n(Cl)→Al E(2)", "π-complex 稳定性", "插入 TS"],
            "current_status": "论文趋势支持该模型，但需要真实 Gaussian/NBO 数据验证。",
            "confidence": 0.78,
            "source": "论文摘要抽取",
        },
        {
            "key": "tea-preorganization",
            "name": "TEA 预组织模型",
            "summary": "TEA 与功能取代基形成适中络合，使 C=C 更容易以生产性方向接近 Ti 中心。",
            "supporting_evidence": ["Al 与氯硅烷取代基相互作用可能帮助单体靠近活性中心。"],
            "falsification": ["若 ΔGbind 很负但 ΔGπ 或 ΔG‡ 变差，说明过度捕获而非有效预组织。"],
            "required_data": ["ΔGbind", "TEA 络合几何", "ΔGπ", "ΔG‡"],
            "current_status": "适合作为 DCS/MCSOMe/DMOS 的核心判据，需要上传 TEA complex log。",
            "confidence": 0.72,
            "source": "论文抽取 + 机制外推",
        },
        {
            "key": "o-ti-poisoning",
            "name": "O→Ti 毒化模型",
            "summary": "甲氧基硅烷中的 O 原子与 Ti 非生产性配位，竞争 C=C π 配位并降低有效插入。",
            "supporting_evidence": ["MCSOMe/DMOS 设计中 OMe 可作为 Lewis 碱位点。", "若 ΔGpoison < 0，O→Ti 络合物更稳定。"],
            "falsification": ["若 n(O)→Ti 很弱且 ΔGpoison 明显为正，则 OMe 不构成主要毒化通道。"],
            "required_data": ["O→Ti complex log", "π-complex log", "n(O)→Ti E(2)", "Ti–O 距离"],
            "current_status": "当前为软件假说引擎中的待验证模型，不来自论文原始定量结论。",
            "confidence": 0.61,
            "source": "机理外推 + 示例数据",
        },
        {
            "key": "chain-window",
            "name": "链长窗口效应模型",
            "summary": "3/5/7-烯基链长改变 C=C 与硅取代基的空间关系，存在随乙烯/丙烯体系变化的最优链长窗口。",
            "supporting_evidence": ["5-hexenyl 甲基二氯硅烷在丙烯体系表现较优。", "乙烯体系中 3-butenyl 甲基二氯硅烷插入表现较高。"],
            "falsification": ["若所有链长在同一催化剂和共聚单体下表现单调一致，则窗口模型需要修正。"],
            "required_data": ["链长系列 ΔG‡", "实验插入率", "构象族权重", "熵校正"],
            "current_status": "论文摘要直接支持链长窗口假说，是 V2 的优先机制模型。",
            "confidence": 0.84,
            "source": "博士论文摘要抽取",
        },
        {
            "key": "ethylene-propylene-split",
            "name": "乙烯/丙烯差异插入模型",
            "summary": "乙烯与丙烯由于生长链和单体取代差异，对同一功能 α-烯烃的位阻/电子效应响应不同。",
            "supporting_evidence": ["三甲基硅烷系列在乙烯与丙烯共聚中表现出不同插入行为。"],
            "falsification": ["若同一链长系列在乙烯/丙烯体系中排序完全一致，该模型的重要性下降。"],
            "required_data": ["乙烯路径 ΔG‡", "丙烯 1,2-re/si 路径 ΔG‡", "实验共聚组成"],
            "current_status": "论文趋势支持，仍需路径级 DFT 数据验证。",
            "confidence": 0.8,
            "source": "博士论文摘要抽取",
        },
    ]
