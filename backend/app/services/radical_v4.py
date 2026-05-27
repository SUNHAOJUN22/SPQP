from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

from app.core.constants import HARTREE_TO_KCAL_MOL
from app.services.literature import extract_docx_text


ALLOWED_LITERATURE_EXTENSIONS = {".docx", ".pdf", ".txt", ".md"}
PDF_GARBLED_WARNING = "PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；建议提供 OCR 文本或可复制文本版 PDF。"
PDF_OCR_WARNING = "PDF 未提取到可搜索文本，可能是扫描件；当前不会执行 OCR，请导入 OCR 文本。"


PEROXIDE_LIBRARY: list[dict[str, Any]] = [
    {
        "key": "dicumyl-peroxide",
        "chinese_name": "过氧化二异丙苯",
        "english_name": "Dicumyl peroxide",
        "peroxide_class": "二烷基过氧化物",
        "has_carbonyl": False,
        "radical_type": "枯基氧自由基 / 甲基自由基副通道",
        "typical_role": "PP 熔融接枝和可控降解常见引发剂；是否交联取决于共剂、氧含量和停留时间。",
        "example_roor_bde_kcal_mol": 37.0,
        "source": "示例数据 / MOCK；请用供应商半衰期或真实计算替换",
    },
    {
        "key": "benzoyl-peroxide",
        "chinese_name": "过氧化苯甲酰",
        "english_name": "Benzoyl peroxide",
        "peroxide_class": "二酰基过氧化物",
        "has_carbonyl": True,
        "radical_type": "苯甲酰氧自由基，可脱羧生成苯基自由基",
        "typical_role": "羰基改变 O–O 键极化、分解自由基和副产物，需单独评价氧化/接枝风险。",
        "example_roor_bde_kcal_mol": 32.0,
        "source": "示例数据 / MOCK；不能作为真实半衰期结论",
    },
    {
        "key": "peroxycarbonate",
        "chinese_name": "过氧碳酸酯类",
        "english_name": "Peroxycarbonate peroxide",
        "peroxide_class": "含羰基过氧化物",
        "has_carbonyl": True,
        "radical_type": "烷氧羰氧自由基 / 烷氧自由基",
        "typical_role": "极性和副产物更复杂，适合在低温或固态窗口中作为待验证变量。",
        "example_roor_bde_kcal_mol": None,
        "source": "结构族示例 / MOCK",
    },
    {
        "key": "dialkyl-peroxide",
        "chinese_name": "通用二烷基过氧化物",
        "english_name": "Generic dialkyl peroxide",
        "peroxide_class": "二烷基过氧化物",
        "has_carbonyl": False,
        "radical_type": "烷氧自由基",
        "typical_role": "用于 RO–OR 均裂、PP 抽氢、β-scission 与交联/支化竞争的基准族。",
        "example_roor_bde_kcal_mol": 38.0,
        "source": "机制占位 / MOCK",
    },
]


def assess_text_quality(text: str, source_type: str = "text") -> dict[str, Any]:
    """Return a conservative, provenance-friendly text quality score."""
    visible_chars = [char for char in text if not char.isspace()]
    if not visible_chars:
        quality = "scanned-needs-ocr" if source_type == "pdf" else "failed"
        return {
            "quality": quality,
            "text_length": len(text),
            "visible_char_count": 0,
            "readable_ratio": 0.0,
            "control_ratio": 0.0,
            "warning": PDF_OCR_WARNING if source_type == "pdf" else "当前文本为空，无法抽取可靠文献线索。",
        }

    control_count = sum(1 for char in visible_chars if ord(char) < 32)
    readable_count = sum(1 for char in visible_chars if char.isascii() and char.isalnum())
    readable_count += sum(1 for char in visible_chars if "\u4e00" <= char <= "\u9fff")
    readable_ratio = readable_count / len(visible_chars)
    control_ratio = control_count / len(visible_chars)
    quality = "encoded-garbled" if source_type == "pdf" and (control_ratio > 0.01 or readable_ratio < 0.22) else "readable"
    return {
        "quality": quality,
        "text_length": len(text),
        "visible_char_count": len(visible_chars),
        "readable_ratio": round(readable_ratio, 4),
        "control_ratio": round(control_ratio, 4),
        "warning": PDF_GARBLED_WARNING if quality == "encoded-garbled" else None,
    }


def extract_pdf_text(path: str | Path) -> tuple[str, list[str], dict[str, Any]]:
    """Extract PDF text without executing embedded content.

    PyMuPDF is optional. If the PDF is scanned or PyMuPDF is unavailable, the
    caller receives a Chinese warning instead of fabricated text.
    """
    pdf_path = Path(path)
    warnings: list[str] = []
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("当前文件不是有效 PDF 文件。")
    if not pdf_path.exists():
        raise FileNotFoundError("未找到指定 PDF 文件。")
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional install
        raise ValueError("未安装 PyMuPDF，无法只读解析 PDF；请安装 requirements 后重试。") from exc

    chunks: list[str] = []
    with fitz.open(pdf_path) as doc:  # type: ignore[attr-defined]
        for page in doc:
            text = page.get_text("text").strip()
            if text:
                chunks.append(text)
    text = "\n".join(chunks)
    source_quality = assess_text_quality(text, "pdf")
    if source_quality["quality"] == "scanned-needs-ocr":
        warnings.append(PDF_OCR_WARNING)
    elif source_quality["quality"] == "encoded-garbled":
        warnings.append(PDF_GARBLED_WARNING)
    return text, warnings, source_quality


def extract_literature_text(path: str | Path) -> tuple[str, list[str], str, dict[str, Any]]:
    literature_path = Path(path)
    suffix = literature_path.suffix.lower()
    if suffix not in ALLOWED_LITERATURE_EXTENSIONS:
        raise ValueError("仅允许读取 .docx、.pdf、.txt、.md 文献文件。")
    if not literature_path.exists():
        raise FileNotFoundError("未找到指定文献文件。")
    if suffix == ".docx":
        text = extract_docx_text(literature_path)
        return text, [], "docx", assess_text_quality(text, "docx")
    if suffix == ".pdf":
        text, warnings, source_quality = extract_pdf_text(literature_path)
        return text, warnings, "pdf", source_quality
    text = literature_path.read_text(encoding="utf-8", errors="ignore")
    return text, [], suffix.lstrip("."), assess_text_quality(text, suffix.lstrip("."))


def _count_terms(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term.lower()) for term in terms)


def _pick_evidence(text: str, terms: list[str], fallback: str) -> str:
    paragraphs = [line.strip() for line in re.split(r"[\n。；;]", text) if line.strip()]
    lowered_terms = [term.lower() for term in terms]
    for paragraph in paragraphs:
        lowered = paragraph.lower()
        if any(term in lowered for term in lowered_terms):
            return paragraph[:280]
    return fallback


def analyze_polypropylene_radical_literature(text: str, source: str) -> dict[str, Any]:
    warnings: list[str] = []
    if len(text) < 1000:
        warnings.append("文献文本较短，可能只读取到摘要、目录或扫描 PDF 的少量文本。")

    entities = [
        {
            "category": "反应链",
            "name": "RO–OR homolysis / PP H-abstraction",
            "chinese_name": "过氧化物均裂与 PP 抽氢",
            "evidence": _pick_evidence(text, ["peroxide", "过氧", "radical", "自由基"], "文献线索用于建立 RO–OR 均裂、RO• 抽氢和 PP 大分子自由基通道。"),
            "confidence": min(0.95, 0.45 + 0.05 * _count_terms(text, ["peroxide", "过氧", "radical", "自由基"])),
            "source": source,
        },
        {
            "category": "竞争路径",
            "name": "beta-scission vs recombination",
            "chinese_name": "β-scission 降解与自由基复合竞争",
            "evidence": _pick_evidence(text, ["scission", "degradation", "降解", "交联", "crosslink"], "聚丙烯大分子自由基可走 β-scission 降解，也可在共剂或链段接近时复合/交联。"),
            "confidence": min(0.92, 0.42 + 0.06 * _count_terms(text, ["scission", "degradation", "降解", "交联", "crosslink"])),
            "source": source,
        },
        {
            "category": "结构变量",
            "name": "carbonyl-containing peroxide",
            "chinese_name": "含羰基过氧化物",
            "evidence": _pick_evidence(text, ["carbonyl", "羰基", "benzoyl", "acyl"], "含羰基过氧化物会改变 O–O 键极化、自由基类型、脱羧/氧化副反应，必须作为待验证变量。"),
            "confidence": min(0.88, 0.35 + 0.08 * _count_terms(text, ["carbonyl", "羰基", "benzoyl", "acyl"])),
            "source": source,
        },
        {
            "category": "微结构变量",
            "name": "isotacticity / ethylene incorporation",
            "chinese_name": "等规度与乙烯引入",
            "evidence": _pick_evidence(text, ["isotactic", "等规", "ethylene", "乙烯", "crystall"], "等规度、乙烯引入和结晶度共同控制固态链段运动、自由基扩散和 β-scission/复合概率。"),
            "confidence": min(0.9, 0.38 + 0.05 * _count_terms(text, ["isotactic", "等规", "ethylene", "乙烯", "crystall"])),
            "source": source,
        },
    ]
    hypotheses = [
        {
            "key": "pp-beta-scission-dominated",
            "name": "PP β-scission 降解主导模型",
            "supporting_evidence": ["三级 C–H 抽氢后形成 PP 大分子自由基，β-scission 可导致分子量下降。"],
            "falsification": ["若 GPC 显示分子量升高且凝胶分数增加，同时断链指标低，则降解主导模型不成立。"],
            "required_data": ["过氧化物半衰期", "停留时间", "GPC 分子量", "凝胶分数", "β-scission 速率常数"],
            "current_status": "可作为默认待检验假说；不能在无真实数据时判定样品必然降解。",
            "confidence": 0.72,
            "source": source,
        },
        {
            "key": "coagent-assisted-branching",
            "name": "共剂/双官能单体促进交联或长链支化模型",
            "supporting_evidence": ["双官能单体、硅烷后反应位点或共剂可把 PP 自由基从断链导向复合/接枝。"],
            "falsification": ["若共剂增加但支化指数、熔体强度或凝胶分数没有上升，则该模型贡献较弱。"],
            "required_data": ["共剂浓度", "支化指数", "凝胶分数", "流变低频模量", "单体接枝率"],
            "current_status": "需要与 β-scission 通道同时拟合。",
            "confidence": 0.66,
            "source": source,
        },
        {
            "key": "carbonyl-peroxide-specific",
            "name": "含羰基过氧化物特异性模型",
            "supporting_evidence": ["羰基影响 RO–OR 键离解能、自由基稳定性、极性副产物和氧化风险。"],
            "falsification": ["若同半衰期、同自由基通量下含羰基与非羰基过氧化物表现无差异，则羰基不是主导变量。"],
            "required_data": ["RO–OR BDE", "半衰期曲线", "副产物分析", "氧化羰基指数", "抽氢选择性"],
            "current_status": "必须作为待验证假说，禁止默认得出更易交联或更易降解结论。",
            "confidence": 0.58,
            "source": source,
        },
    ]
    return {
        "entities": entities,
        "hypotheses": hypotheses,
        "warnings": warnings,
        "keyword_counts": {
            "peroxide_or_radical": _count_terms(text, ["peroxide", "过氧", "radical", "自由基"]),
            "degradation_or_scission": _count_terms(text, ["degradation", "降解", "scission", "断链"]),
            "crosslink_or_branching": _count_terms(text, ["crosslink", "交联", "branch", "支化"]),
            "carbonyl": _count_terms(text, ["carbonyl", "羰基", "benzoyl", "acyl"]),
            "ethylene_isotacticity": _count_terms(text, ["ethylene", "乙烯", "isotactic", "等规"]),
        },
    }


def import_polypropylene_radical_review(path: str, title: str | None = None) -> dict[str, Any]:
    text, warnings, source_type, source_quality = extract_literature_text(path)
    analysis = analyze_polypropylene_radical_literature(text, title or Path(path).name)
    return {
        "title": title or Path(path).stem,
        "path": path,
        "source_type": source_type,
        "parse_quality": source_quality["quality"],
        "source_quality": source_quality,
        "text_length": len(text),
        "text_preview": text[:1800],
        **analysis,
        "warnings": warnings + analysis["warnings"],
        "provenance": "文献文件仅读取文本或 PDF 页面文本，不执行宏、脚本、OCR 程序或外部化学程序；抽取结论为 C 级文献证据线索。",
    }


def calculate_roor_bde(g_radicals_hartree: float, g_peroxide_hartree: float) -> dict[str, float | str]:
    bde_hartree = g_radicals_hartree - g_peroxide_hartree
    return {
        "bde_hartree": bde_hartree,
        "bde_kcal_mol": bde_hartree * HARTREE_TO_KCAL_MOL,
        "formula": "BDE(RO–OR) = G(2RO• 或自由基片段) - G(RO–OR)",
    }


def _bounded(value: float, low: float = 0.0, high: float = 100.0) -> float:
    if not math.isfinite(value):
        return low
    return max(low, min(high, value))


def _clamp(val: float, min_val: float = -50.0, max_val: float = 50.0) -> float:
    if not math.isfinite(val):
        return min_val if val < 0 else max_val
    return max(min_val, min(max_val, val))


def peroxide_profile(data: dict[str, Any]) -> dict[str, Any]:
    bde = data.get("roor_bde_kcal_mol")
    half_life_min = data.get("half_life_min")
    residence_time_min = float(data.get("residence_time_min") or 5.0)
    temperature_c = float(data.get("temperature_c") or 180.0)
    has_carbonyl = bool(data.get("has_carbonyl", False))
    oxygen_level = _bounded(float(data.get("oxygen_level_percent") or 0.0), 0.0, 21.0)

    conversion = None
    if half_life_min is not None and float(half_life_min) >= 0:
        kd = math.log(2.0) / max(float(half_life_min), 1e-12)
        conversion = _bounded((1.0 - math.exp(_clamp(-kd * residence_time_min))) * 100.0)

    activation_score = None
    if bde is not None:
        activation_score = _bounded(100.0 - abs(float(bde) - 36.0) * 3.2)

    carbonyl_note = (
        "该过氧化物含羰基；羰基可能改变 O–O 键极化、自由基类型、脱羧/氧化副反应和抽氢选择性，需要单独验证。"
        if has_carbonyl
        else "该输入未标记羰基；仍需用半衰期和自由基产物验证其真实引发行为。"
    )
    if conversion is None:
        label = "缺少半衰期，无法判断停留时间窗口"
    elif conversion < 20:
        label = "引发不足"
    elif conversion <= 80:
        label = "停留时间窗口适中"
    else:
        label = "过度暴露风险"
    oxidation_risk = _bounded(oxygen_level * 4.0 + (14.0 if has_carbonyl else 4.0))
    return {
        "name": data.get("name") or "未命名过氧化物",
        "peroxide_class": data.get("peroxide_class") or "未指定",
        "has_carbonyl": has_carbonyl,
        "roor_bde_kcal_mol": bde,
        "half_life_min": half_life_min,
        "residence_time_min": residence_time_min,
        "temperature_c": temperature_c,
        "conversion_percent": conversion,
        "activation_score": activation_score,
        "oxidation_risk_score": oxidation_risk,
        "label": label,
        "carbonyl_note": carbonyl_note,
        "formula": "若给定半衰期：kd = ln2 / t1/2，过氧化物转化率 = 1 - exp(-kd × 停留时间)",
        "reliability_note": "该结果只根据用户输入参数计算；示例 BDE 或半衰期不能作为真实工艺结论。",
    }


def radical_branching_vs_scission(data: dict[str, Any]) -> dict[str, Any]:
    ethylene = _bounded(float(data.get("ethylene_mol_percent") or 0.0))
    isotacticity = _bounded(float(data.get("isotacticity_percent") or 92.0))
    crystallinity = _bounded(float(data.get("crystallinity_percent") or 45.0))
    coagent = max(0.0, float(data.get("coagent_phr") or 0.0))
    oxygen = _bounded(float(data.get("oxygen_level_percent") or 0.0), 0.0, 21.0)
    residence = max(0.0, float(data.get("residence_time_min") or 5.0))
    temperature = float(data.get("temperature_c") or 180.0)
    has_carbonyl = bool(data.get("has_carbonyl", False))

    tertiary_site_factor = _bounded(1.0 - ethylene / 100.0 * 0.65, 0.25, 1.0)
    amorphous_mobility = _bounded((100.0 - crystallinity) / 100.0 * 0.75 + (temperature - 120.0) / 180.0 * 0.25, 0.05, 1.0)
    stereoregularity_constraint = _bounded(isotacticity / 100.0 * crystallinity / 100.0, 0.0, 1.0)
    oxygen_factor = 1.0 + oxygen / 21.0 * 1.2 + (0.18 if has_carbonyl else 0.0)
    residence_factor = 1.0 - math.exp(_clamp(-residence / 8.0))
    coagent_factor = 1.0 - math.exp(_clamp(-coagent / 0.35))

    scission_raw = tertiary_site_factor * oxygen_factor * (0.65 + 0.35 * amorphous_mobility) * residence_factor
    branching_raw = (0.22 + 1.25 * coagent_factor) * amorphous_mobility * (1.0 - oxygen / 30.0) * residence_factor
    crosslink_raw = (0.15 + 0.75 * coagent_factor) * stereoregularity_constraint * (1.0 - oxygen / 25.0) * residence_factor
    oxidation_raw = oxygen_factor * oxygen / 21.0 * residence_factor

    total = max(scission_raw + branching_raw + crosslink_raw + oxidation_raw, 1e-12)
    fractions = {
        "beta_scission": scission_raw / total,
        "branching": branching_raw / total,
        "crosslinking": crosslink_raw / total,
        "oxidation": oxidation_raw / total,
    }
    dominant = max(fractions.items(), key=lambda item: item[1])[0]
    labels = {
        "beta_scission": "β-scission 降解占优",
        "branching": "长链支化/接枝占优",
        "crosslinking": "自由基复合交联占优",
        "oxidation": "氧化副反应占优",
    }
    explanation = (
        "乙烯单元会稀释 PP 三级 C–H 位点并改变结晶/链段运动；等规度和结晶度越高，固态自由基扩散越受限。"
        "共剂提高支化/交联通道权重，氧和部分含羰基过氧化物会提高氧化与断链风险。"
    )
    return {
        "fractions": fractions,
        "dominant_path": dominant,
        "label": labels[dominant],
        "indices": {
            "tertiary_site_factor": tertiary_site_factor,
            "amorphous_mobility": amorphous_mobility,
            "stereoregularity_constraint": stereoregularity_constraint,
            "oxygen_factor": oxygen_factor,
        },
        "series": [
            {"path": "β-scission 降解", "fraction": fractions["beta_scission"] * 100.0},
            {"path": "长链支化/接枝", "fraction": fractions["branching"] * 100.0},
            {"path": "自由基复合交联", "fraction": fractions["crosslinking"] * 100.0},
            {"path": "氧化副反应", "fraction": fractions["oxidation"] * 100.0},
        ],
        "explanation": explanation,
        "reliability_note": "该竞争图是参数化机制模型，不会替代真实 GPC、流变、凝胶分数或 ESR 数据。",
    }


def sic_stability(data: dict[str, Any]) -> dict[str, Any]:
    sic = data.get("bde_sic_kcal_mol")
    sio = data.get("bde_sio_kcal_mol")
    sicl = data.get("bde_sicl_kcal_mol")
    radical_barrier = data.get("radical_attack_barrier_kcal_mol")
    values = [value for value in [sic, sio, sicl, radical_barrier] if value is not None]
    if not values:
        return {
            "label": "当前数据不足",
            "interpretations": ["缺少 Si–C/Si–O/Si–Cl BDE 或自由基攻击势垒，不能判断硅碳键稳定性。"],
            "reliability_note": "不会用示例值补全缺失真实数据。",
        }
    interpretations: list[str] = []
    if sic is not None:
        if float(sic) >= 80:
            interpretations.append("Si–C BDE 较高，硅烷侧基在热自由基条件下本征断裂敏感性较低。")
        else:
            interpretations.append("Si–C BDE 偏低，应重点检查自由基攻击或加工热历史导致的侧基断裂。")
    if sio is not None and sic is not None:
        if float(sio) > float(sic):
            interpretations.append("Si–O 键 BDE 高于 Si–C 时，后反应更可能受水解/缩合而非 Si–C 均裂控制。")
        else:
            interpretations.append("Si–C 与 Si–O 稳定性接近，需分别检查 Lewis 酸配位、自由基攻击和水解通道。")
    if radical_barrier is not None and float(radical_barrier) < 12:
        interpretations.append("自由基攻击势垒较低，过氧化物后处理可能影响硅烷侧基完整性。")
    label = "Si–C 键相对稳定" if sic is not None and float(sic) >= 80 else "需要补充 Si–C 稳定性验证"
    return {
        "label": label,
        "bde_sic_kcal_mol": sic,
        "bde_sio_kcal_mol": sio,
        "bde_sicl_kcal_mol": sicl,
        "radical_attack_barrier_kcal_mol": radical_barrier,
        "interpretations": interpretations,
        "formula": "BDE(Si–C) = G(R3Si• + •R) - G(R3Si–R)",
        "reliability_note": "BDE 必须来自真实量子化学输出或用户核验输入；示例值不能作为真实结论。",
    }


def residence_time_window(data: dict[str, Any]) -> dict[str, Any]:
    profile = peroxide_profile(data)
    conversion = profile["conversion_percent"]
    low = float(data.get("target_conversion_low_percent") or 20.0)
    high = float(data.get("target_conversion_high_percent") or 80.0)
    if conversion is None:
        status = "无法判定"
        advice = "缺少过氧化物半衰期，无法把停留时间映射为自由基通量。"
    elif conversion < low:
        status = "停留时间偏短"
        advice = "过氧化物分解不足，可能接枝/支化效率低；应检查半衰期温度或延长停留时间。"
    elif conversion <= high:
        status = "窗口适中"
        advice = "自由基通量处于目标窗口；下一步应同时检查 β-scission、凝胶分数和氧化指标。"
    else:
        status = "停留时间偏长"
        advice = "过氧化物过度分解，PP β-scission、氧化或凝胶化风险上升。"
    return {
        **profile,
        "target_window_percent": [low, high],
        "status": status,
        "advice": advice,
        "axis_data": [
            {"name": "目标下限", "value": low},
            {"name": "当前转化率", "value": conversion or 0.0},
            {"name": "目标上限", "value": high},
        ],
    }


def carbonyl_taxonomy() -> dict[str, Any]:
    return {
        "title": "羰基效应三分法",
        "items": [
            {
                "type": "过氧化物羰基",
                "english": "carbonyl in peroxide",
                "mechanistic_role": "改变 O–O 键极化、分解自由基类型、脱羧路径、挥发/副产物和抽氢选择性。",
                "examples": ["苯甲酰过氧化物", "过氧酯", "酰基过氧化物"],
                "required_data": ["RO–OR BDE", "半衰期曲线", "自由基产物", "副产物 GC-MS", "氧化指标"],
                "boundary": "不能仅凭含羰基判断更易降解或更易交联。",
            },
            {
                "type": "接枝单体羰基",
                "english": "carbonyl in grafting monomer",
                "mechanistic_role": "提高单体极性和缺电子性，改变自由基加成速率、接枝效率、相容性和界面作用。",
                "examples": ["马来酸酐", "丙烯酸酯", "甲基丙烯酸酯"],
                "required_data": ["接枝率", "酸酐/酯 FTIR", "界面强度", "介电损耗", "接枝副反应"],
                "boundary": "接枝效率提高不等同于主链不降解。",
            },
            {
                "type": "氧化副产物羰基",
                "english": "oxidative carbonyl products",
                "mechanistic_role": "反映热氧老化和副反应，可改变极性、介电陷阱、长期稳定性和进一步降解敏感性。",
                "examples": ["酮", "醛", "酯", "羧酸"],
                "required_data": ["FTIR carbonyl index", "OIT", "介电谱", "空间电荷", "热氧老化"],
                "boundary": "羰基指数升高通常是副反应信号，不能直接视为有效功能化。",
            },
        ],
        "summary": "过氧化物是否含羰基、接枝单体是否含羰基、氧化副产物是否含羰基是三个不同问题，必须分开建模。",
    }


def experimental_design_matrix() -> dict[str, Any]:
    return {
        "title": "PP/IPC/LCB-IPC 自由基后反应三层正交实验矩阵",
        "layers": [
            {
                "name": "结构基准",
                "variables": ["普通 iPP", "PPR", "IPC", "LCB-IPC(hex-DCS)", "MCSOMe 候选体系", "DMOS 候选体系"],
            },
            {
                "name": "过氧化物筛选",
                "variables": ["DCP", "BPO / DBP", "TBPB", "L-101", "TBPEH", "空白对照"],
            },
            {
                "name": "工艺窗口",
                "variables": ["120 / 150 / 170 / 190 ℃", "1 / 5 / 10 / 20 min", "N2 / air", "无 / DVB / TAC / PETA / MAH / styrene-MAH"],
            },
        ],
        "required_characterization": [
            "GPC: Mw, Mn, PDI, 高分子量肩峰",
            "MFR/MFI: 降解程度",
            "凝胶含量: 交联程度",
            "SAOS: 长链支化",
            "拉伸流变: strain hardening",
            "FTIR: carbonyl index, Si–O–Si, Si–OH",
            "29Si NMR: Si–Cl / Si–OH / Si–O–Si",
            "13C NMR: 乙烯/丙烯序列",
            "DSC: Tm, Tc, Xc",
            "SEM/TEM/AFM: 相形态",
            "介电谱/空间电荷: 电性能",
            "GC-MS: 过氧化物副产物/残留",
        ],
        "response_model": "MFR / Mw / gel / LCB index = f(T, residence time, peroxide loading, coagent, crystallinity, ethylene content)",
        "reliability_note": "该矩阵是实验设计建议，不能替代真实实验结果。",
    }


def unified_lcb_framework(data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or {}
    positive_keys = ["chi_insert", "chi_hydrolysis", "chi_condensation", "chi_radical_recombination"]
    negative_keys = ["chi_beta_scission", "chi_oxidation", "chi_ti_poison", "chi_over_gel"]
    positive_values = [_to_fraction(data.get(key)) for key in positive_keys]
    negative_values = [_to_fraction(data.get(key)) for key in negative_keys]
    lcb_efficiency = None
    if any(value is not None for value in positive_values + negative_values):
        positive = sum(value or 0.0 for value in positive_values)
        negative = sum(value or 0.0 for value in negative_values)
        lcb_efficiency = _bounded((positive - negative + 4.0) / 8.0 * 100.0)

    return {
        "title": "Si–O–Si 配位聚合支化与过氧化物自由基后改性的统一机制框架",
        "route_comparison": [
            {
                "route": "hex-DCS / Si–O–Si 路线",
                "chain": "Ziegler–Natta C=C 配位插入 → PP/EPC-g-silane → Si–Cl/Si–OMe 水解 → Si–O–Si 缩合 → H 型长链支化",
                "advantage": "结构更可设计，PP-H-PP、EPC-H-EPC、PP-H-EPC 桥联关系明确。",
                "risk": "功能单体插入困难、O→Ti 毒化、TEA 过度捕获和水解缩合窗口需要控制。",
            },
            {
                "route": "过氧化物自由基路线",
                "chain": "RO–OR 均裂 → RO• 抽氢 → PP• → β-scission / 自由基复合 / 接枝 / 交联",
                "advantage": "工艺直接，可用于熔融挤出或固相后改性。",
                "risk": "PP 叔碳自由基易 β-scission，可能导致 MFR 上升、Mw 下降和氧化副反应。",
            },
        ],
        "mechanism_stages": [
            {
                "stage": "阶段 A：Ziegler–Natta 插入",
                "criteria": ["ΔGpoison = G(O→Ti) − G(C=C π-complex)", "ΔG‡insert = G(TS) − G(reference)"],
                "output": "PP-g-silane / EPC-g-silane",
            },
            {
                "stage": "阶段 B：水解缩合形成 LCB",
                "criteria": ["ΔGhydrolysis", "ΔGcondensation", "Si–O–Si FTIR / 29Si NMR", "gel fraction / LCB index"],
                "output": "PP-H-PP、EPC-H-EPC、PP-H-EPC 型 Si–O–Si 桥联",
            },
            {
                "stage": "阶段 C：过氧化物自由基后改性",
                "criteria": ["RO–OR 半衰期", "PP 抽氢速率", "β-scission 速率", "复合/接枝/交联速率", "carbonyl index"],
                "output": "降解、轻度支化、交联或氧化副反应的竞争结果",
            },
        ],
        "lcb_efficiency_formula": {
            "formula": "ΦLCB = f(χinsert, χhydrolysis, χcondensation, χradical_recombination) − f(χβ-scission, χoxidation, χTi_poison, χover-gel)",
            "inputs": {
                "positive": positive_keys,
                "negative": negative_keys,
            },
            "score_percent": lcb_efficiency,
            "interpretation": _lcb_efficiency_label(lcb_efficiency),
        },
        "core_hypothesis": (
            "DCS/MCSOMe/DMOS 通过 C=C 插入将 Si–C–silane 功能侧链引入 PP/EPC 分子链；"
            "后处理阶段 Si–Cl/Si–OMe 水解缩合形成 Si–O–Si 桥联。若引入过氧化物，体系进入 PP 主链自由基竞争网络，"
            "最终结构取决于 Si–O–Si 缩合支化与 PP β-scission、复合、接枝、氧化和过凝胶之间的竞争。"
        ),
        "boss_summary": (
            "Si–O 路线解决的是如何可设计地形成长链支化；过氧化物路线解决的是如何在自由基不可控副反应中争取支化/交联而避免 PP β-断裂降解。"
        ),
        "reliability_note": "该框架是可计算、可表征、可工艺优化的机制图谱；没有真实输入时不输出确定性排序。",
    }


def _to_fraction(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number > 1.0:
        number = number / 100.0
    return max(0.0, min(1.0, number))


def _lcb_efficiency_label(score: float | None) -> str:
    if score is None:
        return "当前未提供 χ 项，无法计算有效长链支化效率。"
    if score >= 70:
        return "有效长链支化窗口较好，但仍需凝胶、GPC 和流变验证。"
    if score >= 45:
        return "支化与降解/氧化竞争接近，需要优化过氧化物、共剂和停留时间。"
    return "负向副反应占比偏高，优先降低 β-scission、氧化或过凝胶风险。"
