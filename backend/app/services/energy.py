from __future__ import annotations

import math
from dataclasses import dataclass

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_EV, HARTREE_TO_KCAL_MOL, R_KCAL_MOL_K


def hartree_to_kcal_mol(value: float) -> float:
    return value * HARTREE_TO_KCAL_MOL


def hartree_to_ev(value: float) -> float:
    return value * HARTREE_TO_EV


def kcal_mol_to_hartree(value: float) -> float:
    return value / HARTREE_TO_KCAL_MOL


def _clamp(val: float, min_val: float = -50.0, max_val: float = 50.0) -> float:
    if not math.isfinite(val):
        return min_val if val < 0 else max_val
    return max(min_val, min(max_val, val))


def delta_g_binding(complex_g_hartree: float, fragment_g_hartree: list[float]) -> tuple[float, float]:
    _ensure_finite("complex_g_hartree", complex_g_hartree)
    for index, value in enumerate(fragment_g_hartree):
        _ensure_finite(f"fragment_g_hartree[{index}]", value)
    delta_hartree = complex_g_hartree - sum(fragment_g_hartree)
    return delta_hartree, hartree_to_kcal_mol(delta_hartree)


def _ensure_finite(name: str, value: float) -> None:
    if not math.isfinite(float(value)):
        raise ValueError(f"{name} 必须是有限数值。")


def bond_dissociation_energy(g_fragments_hartree: float, g_molecule_hartree: float) -> dict[str, float]:
    """Return BDE in Hartree, kcal/mol and eV from fragment and parent Gibbs energies."""

    _ensure_finite("g_fragments_hartree", g_fragments_hartree)
    _ensure_finite("g_molecule_hartree", g_molecule_hartree)
    bde_hartree = g_fragments_hartree - g_molecule_hartree
    return {
        "bde_hartree": bde_hartree,
        "bde_kcal_mol": hartree_to_kcal_mol(bde_hartree),
        "bde_ev": hartree_to_ev(bde_hartree),
    }


def classify_bde(bond_type: str, bde_kcal_mol: float) -> str:
    normalized = bond_type.strip().upper().replace("–", "-")
    if normalized == "SI-C":
        if bde_kcal_mol >= 80.0:
            return "Si–C 侧链连接稳定"
        if bde_kcal_mol < 65.0:
            return "Si–C 连接臂存在失效风险"
        return "Si–C 稳定性处于过渡区，需要补充自由基攻击势垒与实验验证"
    if normalized == "SI-O":
        if bde_kcal_mol >= 90.0:
            return "Si–O 键本征强度较高，后反应更可能受 Lewis 酸配位、水解和缩合控制"
        return "Si–O BDE 偏低或未充分验证，需结合 WBI、ρBCP 和振动频率判断"
    if normalized == "SI-CL":
        return "Si–Cl BDE 只描述均裂代价，水解缩合反应还需显式水和离去物路径验证"
    if normalized == "RO-OR":
        if bde_kcal_mol <= 40.0:
            return "RO–OR BDE 处于易热分解窗口，应结合半衰期、温度和自由基副产物判断"
        return "RO–OR BDE 较高，需核验加工温度下半衰期是否足以释放自由基"
    return "当前键类型未配置专用阈值，仅返回 BDE 数值；不能形成确定机制结论"


def classify_binding(delta_g_bind_kcal_mol: float) -> str:
    if delta_g_bind_kcal_mol <= -25.0:
        return "过度捕获"
    if delta_g_bind_kcal_mol <= -8.0:
        return "有效预组织"
    if delta_g_bind_kcal_mol <= -2.0:
        return "弱导向"
    return "无显著相互作用"


def delta_g_poison(o_ti_complex_g_hartree: float, pi_complex_g_hartree: float) -> tuple[float, str, str]:
    _ensure_finite("o_ti_complex_g_hartree", o_ti_complex_g_hartree)
    _ensure_finite("pi_complex_g_hartree", pi_complex_g_hartree)
    delta = hartree_to_kcal_mol(o_ti_complex_g_hartree - pi_complex_g_hartree)
    if delta > 5.0:
        return delta, "生产性 C=C 插入占优", "green"
    if delta >= 0.0:
        return delta, "O→Ti 与 C=C 配位竞争", "yellow"
    return delta, "Ti 活性中心存在甲氧基毒化风险", "red"


def relative_rate(delta_delta_g_kcal_mol: float, temperature_k: float = DEFAULT_TEMPERATURE_K) -> float:
    if temperature_k <= 0:
        raise ValueError("temperature_k 必须为正数。")
    exponent = -delta_delta_g_kcal_mol / (R_KCAL_MOL_K * max(temperature_k, 1e-12))
    return math.exp(_clamp(exponent))


@dataclass(frozen=True)
class InsertionProfile:
    delta_g_pi_kcal_mol: float
    delta_g_barrier_kcal_mol: float
    delta_g_complex_barrier_kcal_mol: float
    delta_g_product_kcal_mol: float | None
    delta_delta_g_barrier_kcal_mol: float | None
    krel: float | None
    temperature_k: float


def insertion_profile(
    free_site_monomer_g_hartree: float,
    pi_complex_g_hartree: float,
    ts_g_hartree: float,
    product_g_hartree: float | None = None,
    reference_barrier_kcal_mol: float | None = None,
    temperature_k: float = DEFAULT_TEMPERATURE_K,
) -> InsertionProfile:
    delta_g_pi = hartree_to_kcal_mol(pi_complex_g_hartree - free_site_monomer_g_hartree)
    delta_g_barrier = hartree_to_kcal_mol(ts_g_hartree - free_site_monomer_g_hartree)
    delta_g_complex_barrier = hartree_to_kcal_mol(ts_g_hartree - pi_complex_g_hartree)
    delta_g_product = (
        hartree_to_kcal_mol(product_g_hartree - free_site_monomer_g_hartree)
        if product_g_hartree is not None
        else None
    )
    delta_delta = delta_g_barrier - reference_barrier_kcal_mol if reference_barrier_kcal_mol is not None else None
    krel_value = relative_rate(delta_delta, temperature_k) if delta_delta is not None else None
    return InsertionProfile(
        delta_g_pi_kcal_mol=delta_g_pi,
        delta_g_barrier_kcal_mol=delta_g_barrier,
        delta_g_complex_barrier_kcal_mol=delta_g_complex_barrier,
        delta_g_product_kcal_mol=delta_g_product,
        delta_delta_g_barrier_kcal_mol=delta_delta,
        krel=krel_value,
        temperature_k=temperature_k,
    )


def rate_comparison(
    barriers_kcal_mol: dict[str, float],
    reference_key: str,
    temperature_k: float = DEFAULT_TEMPERATURE_K,
) -> dict[str, dict[str, float]]:
    if reference_key not in barriers_kcal_mol:
        raise ValueError("reference_key 必须存在于 barriers_kcal_mol。")
    reference = barriers_kcal_mol[reference_key]
    return {
        key: {
            "barrier_kcal_mol": barrier,
            "delta_delta_g_kcal_mol": barrier - reference,
            "krel": relative_rate(barrier - reference, temperature_k),
        }
        for key, barrier in barriers_kcal_mol.items()
    }


def score_from_window(value: float | None, ideal: float, width: float, invert: bool = False) -> float | None:
    if value is None:
        return None
    score = max(0.0, min(100.0, 100.0 - abs(value - ideal) * (100.0 / width)))
    return 100.0 - score if invert else score


def decision_scores(candidate: dict[str, float | str | None]) -> dict[str, float | str | None]:
    e_insert = candidate.get("e_insert")
    e_poison = candidate.get("e_ti_poison")
    e_al = candidate.get("e_al_capture")
    e_post = candidate.get("e_post")
    e_intrinsic = candidate.get("e_intrinsic")

    insertion = max(0.0, min(100.0, 100.0 - float(e_insert) * 3.2)) if e_insert is not None else None
    poison = max(0.0, min(100.0, 50.0 - float(e_poison) * 6.0)) if e_poison is not None else None
    tea = score_from_window(float(e_al), ideal=-12.0, width=28.0) if e_al is not None else None
    steric = max(0.0, min(100.0, float(e_intrinsic) * 4.0 + max(float(e_insert or 0.0) - 15.0, 0.0) * 3.0)) if e_intrinsic is not None else None
    post = max(0.0, min(100.0, 100.0 - abs(float(e_post)) * 2.4)) if e_post is not None else None

    positive_components = [v for v in [insertion, tea, post] if v is not None]
    penalty_components = [v for v in [poison, steric] if v is not None]
    overall = None
    if positive_components or penalty_components:
        positive = sum(positive_components) / max(len(positive_components), 1)
        penalty = sum(penalty_components) / max(len(penalty_components), 1) if penalty_components else 0.0
        overall = max(0.0, min(100.0, positive - penalty * 0.45))

    label = classify_candidate(e_poison, e_insert, e_al, steric, post, overall)
    return {
        "insertion_compatibility_score": insertion,
        "poisoning_risk_score": poison,
        "tea_capture_score": tea,
        "steric_penalty_score": steric,
        "post_functionalization_score": post,
        "overall_candidate_score": overall,
        "label": label,
    }


def classify_candidate(
    e_poison: float | str | None,
    e_insert: float | str | None,
    e_al: float | str | None,
    steric: float | None,
    post: float | None,
    overall: float | None,
) -> str:
    if e_poison is not None and float(e_poison) < 0:
        return "Ti 毒化"
    if e_al is not None and float(e_al) < -25 and (e_insert is None or float(e_insert) > 18):
        return "强捕获但插入活性差"
    if steric is not None and steric > 70:
        return "位阻主导"
    if post is not None and post > 70 and (overall is None or overall < 45):
        return "后反应潜力高但聚合风险大"
    if overall is not None and overall >= 65:
        return "平衡候选"
    if e_insert is not None and float(e_insert) < 12:
        return "高插入活性基准"
    return "竞争关系不确定"
