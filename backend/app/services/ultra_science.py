from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_KCAL_MOL, HARTREE_TO_EV, R_KCAL_MOL_K

PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
SPEED_OF_LIGHT_CM_S = 2.99792458e10


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


def calculate_delta_g_bind(complex_g_hartree: float, fragment_g_hartrees: list[float]) -> dict[str, float | str]:
    delta_hartree = complex_g_hartree - sum(fragment_g_hartrees)
    return {
        "delta_g_bind_hartree": delta_hartree,
        "delta_g_bind_kcal_mol": hartree_to_kcal_mol(delta_hartree),
        "formula": "ΔGbind = G(络合物) - ΣG(片段)",
    }


def calculate_delta_g_poison(o_ti_complex_g_hartree: float, pi_complex_g_hartree: float) -> dict[str, float | str]:
    delta = hartree_to_kcal_mol(o_ti_complex_g_hartree - pi_complex_g_hartree)
    if delta > 5.0:
        label, tone = "生产性 C=C 插入占优", "green"
    elif delta >= 0.0:
        label, tone = "O→Ti 与 C=C 配位竞争", "yellow"
    else:
        label, tone = "Ti 活性中心存在甲氧基毒化风险", "red"
    return {
        "delta_g_poison_kcal_mol": delta,
        "label": label,
        "tone": tone,
        "formula": "ΔGpoison = G(O→Ti 毒化络合物) - G(C=C π-络合物)",
    }


def calculate_delta_g_pi(pi_complex_g_hartree: float, free_site_monomer_g_hartree: float) -> float:
    return hartree_to_kcal_mol(pi_complex_g_hartree - free_site_monomer_g_hartree)


def calculate_delta_g_insert(ts_g_hartree: float, free_site_monomer_g_hartree: float) -> float:
    return hartree_to_kcal_mol(ts_g_hartree - free_site_monomer_g_hartree)


def calculate_delta_g_complex(ts_g_hartree: float, pi_complex_g_hartree: float) -> float:
    return hartree_to_kcal_mol(ts_g_hartree - pi_complex_g_hartree)


def calculate_delta_g_product(product_g_hartree: float, free_site_monomer_g_hartree: float) -> float:
    return hartree_to_kcal_mol(product_g_hartree - free_site_monomer_g_hartree)


def calculate_relative_rate(delta_delta_g_kcal_mol: float, temperature_k: float = DEFAULT_TEMPERATURE_K) -> float:
    if temperature_k <= 0:
        raise ValueError("温度必须大于 0 K。")
    exponent = -delta_delta_g_kcal_mol / (R_KCAL_MOL_K * max(temperature_k, 1e-12))
    return math.exp(_clamp(exponent))


def calculate_wigner_tunneling(nu_imag_cm_1: float, temperature_k: float = DEFAULT_TEMPERATURE_K) -> float:
    if temperature_k <= 0:
        raise ValueError("温度必须大于 0 K。")
    if nu_imag_cm_1 >= 0:
        return 1.0
    x = PLANCK_CONSTANT * SPEED_OF_LIGHT_CM_S * abs(nu_imag_cm_1) / (BOLTZMANN_CONSTANT * temperature_k)
    return 1.0 + (x * x) / 24.0


def calculate_k_rel_with_tunneling(
    delta_delta_g_kcal_mol: float,
    temperature_k: float = DEFAULT_TEMPERATURE_K,
    nu_imag_1_cm_1: float = 0.0,
    nu_imag_2_cm_1: float = 0.0,
) -> dict[str, float | str]:
    classical = calculate_relative_rate(delta_delta_g_kcal_mol, temperature_k)
    kappa_1 = calculate_wigner_tunneling(nu_imag_1_cm_1, temperature_k)
    kappa_2 = calculate_wigner_tunneling(nu_imag_2_cm_1, temperature_k)
    corrected = classical * (kappa_1 / max(kappa_2, 1e-12))
    return {
        "krel_classical": classical,
        "wigner_factor_1": kappa_1,
        "wigner_factor_2": kappa_2,
        "krel_wigner_corrected": corrected,
        "formula": "krel = exp[-ΔΔG‡ / RT] × κ1/κ2",
    }


def calculate_bde_sic(g_fragments_hartree: float, g_molecule_hartree: float) -> dict[str, float | str]:
    bde_hartree = g_fragments_hartree - g_molecule_hartree
    return {
        "bde_hartree": bde_hartree,
        "bde_kcal_mol": hartree_to_kcal_mol(bde_hartree),
        "bond": "Si–C",
        "mechanistic_meaning": "用于评价硅烷侧基在后处理或副反应中的断裂敏感性。",
    }


def calculate_bde_sio(g_fragments_hartree: float, g_molecule_hartree: float) -> dict[str, float | str]:
    bde_hartree = g_fragments_hartree - g_molecule_hartree
    return {
        "bde_hartree": bde_hartree,
        "bde_kcal_mol": hartree_to_kcal_mol(bde_hartree),
        "bond": "Si–O",
        "mechanistic_meaning": "用于评价 Si–O 键在 Lewis 酸配位和水解缩合中的稳定性。",
    }


def calculate_bde_roor(g_radicals_hartree: float, g_peroxide_hartree: float) -> dict[str, float | str]:
    bde_hartree = g_radicals_hartree - g_peroxide_hartree
    return {
        "bde_hartree": bde_hartree,
        "bde_kcal_mol": hartree_to_kcal_mol(bde_hartree),
        "bond": "RO–OR",
        "mechanistic_meaning": "用于热引发或过氧化物后反应动力学扩展；不等同 Ziegler–Natta 插入步骤。",
    }


def calculate_boltzmann_weights(energies_kcal_mol: list[float], temperature_k: float = DEFAULT_TEMPERATURE_K) -> list[float]:
    if temperature_k <= 0:
        raise ValueError("温度必须大于 0 K。")
    if not energies_kcal_mol:
        return []
    e_min = min(energies_kcal_mol)
    factors = [math.exp(_clamp(-(energy - e_min) / (R_KCAL_MOL_K * max(temperature_k, 1e-12)))) for energy in energies_kcal_mol]
    total = sum(factors)
    if total == 0:
        return [0.0 for _ in factors]
    return [factor / total for factor in factors]


def calculate_s_lcb(branches_per_1000c: float, branch_length: float, randomness: float) -> float:
    return max(0.0, branches_per_1000c) * max(0.0, branch_length) * max(0.0, min(1.0, randomness))


def _score_window(value: float | None, ideal: float, width: float) -> float | None:
    if value is None:
        return None
    return max(0.0, min(100.0, 100.0 - abs(value - ideal) * (100.0 / width)))


def _score_low_is_good(value: float | None, scale: float, offset: float = 100.0) -> float | None:
    if value is None:
        return None
    return max(0.0, min(100.0, offset - value * scale))


@dataclass(frozen=True)
class FourAxisScores:
    monomer_intrinsic: float | None
    catalyst_compatibility: float | None
    radical_processability: float | None
    microphase_performance: float | None
    overall: float | None
    label: str
    explanation: str


class FourAxisMechanismModel:
    """Merged from the nested Si-O project and adapted to the Chinese V2 mechanism platform."""

    def evaluate(self, data: dict[str, Any]) -> FourAxisScores:
        monomer = self._monomer_axis(data)
        catalyst = self._catalyst_axis(data)
        radical = self._radical_axis(data)
        microphase = self._microphase_axis(data)
        available = [score for score in [monomer, catalyst, radical, microphase] if score is not None]
        overall = sum(available) / len(available) if available else None
        label = self._label(overall, data)
        explanation = self._explain(label, data, monomer, catalyst, radical, microphase)
        return FourAxisScores(monomer, catalyst, radical, microphase, overall, label, explanation)

    def _monomer_axis(self, data: dict[str, Any]) -> float | None:
        delta_g_insert = _to_float(data.get("delta_g_insert_kcal_mol"))
        delta_g_pi = _to_float(data.get("delta_g_pi_kcal_mol"))
        steric = _to_float(data.get("steric_penalty"))
        electronic = _to_float(data.get("electronic_guiding_score"))
        scores = [
            _score_low_is_good(delta_g_insert, 3.2),
            _score_window(delta_g_pi, ideal=-8.0, width=24.0),
            _score_low_is_good(steric, 1.2),
            electronic,
        ]
        return _mean_present(scores)

    def _catalyst_axis(self, data: dict[str, Any]) -> float | None:
        delta_g_poison = _to_float(data.get("delta_g_poison_kcal_mol"))
        tea = _to_float(data.get("tea_binding_kcal_mol"))
        ti_o = _to_float(data.get("n_o_to_ti_e2_kcal_mol"))
        ccti = _to_float(data.get("pi_c_c_to_ti_e2_kcal_mol"))
        poison_score = None if delta_g_poison is None else max(0.0, min(100.0, 50.0 + delta_g_poison * 6.0))
        tea_score = _score_window(tea, ideal=-12.0, width=32.0)
        nbo_score = None
        if ti_o is not None or ccti is not None:
            nbo_score = max(0.0, min(100.0, 50.0 + (ccti or 0.0) * 2.5 - (ti_o or 0.0) * 2.5))
        return _mean_present([poison_score, tea_score, nbo_score])

    def _radical_axis(self, data: dict[str, Any]) -> float | None:
        sic_bde = _to_float(data.get("bde_sic_kcal_mol"))
        sio_bde = _to_float(data.get("bde_sio_kcal_mol"))
        roor_bde = _to_float(data.get("bde_roor_kcal_mol"))
        chain_scission = _to_float(data.get("chain_scission_risk"))
        scores = [
            _score_window(sic_bde, ideal=86.0, width=60.0),
            _score_window(sio_bde, ideal=105.0, width=80.0),
            _score_window(roor_bde, ideal=38.0, width=40.0),
            _score_low_is_good(chain_scission, 1.1),
        ]
        return _mean_present(scores)

    def _microphase_axis(self, data: dict[str, Any]) -> float | None:
        transparency = _to_float(data.get("transparency_percent"))
        crystallinity = _to_float(data.get("crystallinity_percent"))
        sequence = _to_float(data.get("sequence_length"))
        lcb = _to_float(data.get("long_chain_branching_score"))
        scores = [
            transparency,
            _score_window(crystallinity, ideal=35.0, width=70.0),
            _score_window(sequence, ideal=4.0, width=12.0),
            _score_window(lcb, ideal=24.0, width=60.0),
        ]
        return _mean_present(scores)

    def _label(self, overall: float | None, data: dict[str, Any]) -> str:
        poison = _to_float(data.get("delta_g_poison_kcal_mol"))
        if poison is not None and poison < 0:
            return "Ti 毒化风险主导"
        if overall is None:
            return "数据不足"
        if overall >= 72:
            return "论文驱动平衡候选"
        if overall >= 55:
            return "需要补充验证的可行候选"
        return "机制风险较高"

    def _explain(
        self,
        label: str,
        data: dict[str, Any],
        monomer: float | None,
        catalyst: float | None,
        radical: float | None,
        microphase: float | None,
    ) -> str:
        if label == "Ti 毒化风险主导":
            return "当前 ΔGpoison < 0，非生产性 O→Ti 配位相对更稳定，应优先补充 Ti–O 距离、NBO E(2) 和 IRC 证据。"
        if all(score is None for score in [monomer, catalyst, radical, microphase]):
            return "当前未提供足够真实数据，系统只返回可证伪判据框架，不输出确定性科学结论。"
        strongest = max(
            [(monomer, "单体本征插入"), (catalyst, "催化剂兼容"), (radical, "后反应加工"), (microphase, "微观结构性能")],
            key=lambda item: -1 if item[0] is None else item[0],
        )[1]
        return f"当前四轴模型中“{strongest}”维度相对占优；该判断来自用户输入或上传解析数据，不会自动替代论文和实验验证。"


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mean_present(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return max(0.0, min(100.0, sum(present) / len(present)))


class RadicalKineticsEngine:
    species = ["ROOR", "RO", "PPH", "PP_radical", "monomer", "coagent", "branch", "scission", "oxidation"]

    default_rate_constants = {
        "kd": 0.012,
        "k_abs": 0.18,
        "k_add_m": 0.30,
        "k_add_c": 0.22,
        "k_scission": 0.035,
        "k_oxidation": 0.018,
        "k_term": 0.14,
    }

    def simulate_rk4(
        self,
        initial: dict[str, float] | None = None,
        rate_constants: dict[str, float] | None = None,
        t_end: float = 10.0,
        steps: int = 80,
    ) -> dict[str, Any]:
        if steps < 2:
            raise ValueError("steps 至少为 2。")
        if t_end <= 0:
            raise ValueError("t_end 必须大于 0。")
        initial = initial or {}
        rates = {**self.default_rate_constants, **(rate_constants or {})}
        y = [
            max(0.0, float(initial.get("ROOR", 1.0))),
            max(0.0, float(initial.get("RO", 0.0))),
            max(0.0, float(initial.get("PPH", 1.0))),
            max(0.0, float(initial.get("PP_radical", 0.0))),
            max(0.0, float(initial.get("monomer", 0.4))),
            max(0.0, float(initial.get("coagent", 0.1))),
            max(0.0, float(initial.get("branch", 0.0))),
            max(0.0, float(initial.get("scission", 0.0))),
            max(0.0, float(initial.get("oxidation", 0.0))),
        ]
        dt = t_end / (steps - 1)
        time = [i * dt for i in range(steps)]
        series: list[dict[str, float]] = []
        for t in time:
            series.append({"time": t, **{name: y[index] for index, name in enumerate(self.species)}})
            y = self._rk4_step(y, dt, rates)
            y = [max(0.0, value) for value in y]
        return {
            "species": self.species,
            "time_unit": "任意时间单位 / 示例动力学时间",
            "series": series,
            "final": series[-1],
            "provenance": "自由基后反应动力学为合并自 Si-O 子项目的扩展模型；未用于替代 Ziegler–Natta 插入主判据。",
        }

    def _rk4_step(self, y: list[float], dt: float, rates: dict[str, float]) -> list[float]:
        k1 = self._derivatives(y, rates)
        k2 = self._derivatives([value + 0.5 * dt * deriv for value, deriv in zip(y, k1)], rates)
        k3 = self._derivatives([value + 0.5 * dt * deriv for value, deriv in zip(y, k2)], rates)
        k4 = self._derivatives([value + dt * deriv for value, deriv in zip(y, k3)], rates)
        return [value + dt * (a + 2 * b + 2 * c + d) / 6.0 for value, a, b, c, d in zip(y, k1, k2, k3, k4)]

    def _derivatives(self, y: list[float], rates: dict[str, float]) -> list[float]:
        roor, ro, pph, pp_radical, monomer, coagent, branch, scission, oxidation = y
        kd = rates["kd"]
        k_abs = rates["k_abs"]
        k_add_m = rates["k_add_m"]
        k_add_c = rates["k_add_c"]
        k_scission = rates["k_scission"]
        k_oxidation = rates["k_oxidation"]
        k_term = rates["k_term"]

        initiation = kd * roor
        abstraction = k_abs * ro * pph
        monomer_add = k_add_m * pp_radical * monomer
        coagent_add = k_add_c * pp_radical * coagent
        scission_rate = k_scission * pp_radical
        oxidation_rate = k_oxidation * pp_radical
        termination = k_term * pp_radical * pp_radical

        return [
            -initiation,
            2 * initiation - abstraction,
            -abstraction,
            abstraction - monomer_add - coagent_add - scission_rate - oxidation_rate - 2 * termination,
            -monomer_add,
            -coagent_add,
            monomer_add + coagent_add,
            scission_rate,
            oxidation_rate,
        ]


four_axis_model = FourAxisMechanismModel()
radical_kinetics_engine = RadicalKineticsEngine()


def merged_ultra_inventory() -> dict[str, Any]:
    return {
        "title": "Si-O 子项目合并资产清单",
        "merge_strategy": "非破坏式吸收合并：保留根项目中文 V2 主线，不覆盖旧文件；只迁入可复用科学核心、API 和文档。",
        "backend_capabilities": [
            "Hartree/kcal/mol/eV 换算与 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex 公式",
            "Wigner 隧穿修正相对速率与 Boltzmann 权重",
            "Si–C、Si–O、RO–OR 键离解能扩展公式",
            "论文驱动四轴机制模型：单体本征、催化剂兼容、后反应动力学、微相/性能",
            "自由基后反应 RK4 动力学扩展，用于后处理功能化研究",
        ],
        "frontend_capabilities": [
            "新增合并工作台页面，集中展示已合并公式、四轴判据和动力学曲线",
            "通过 lazy-loaded 主应用模块接入，不引入子项目的重型依赖冲突",
            "迁入轻量 TypeScript 科学工具：Eyring 速率、选择性、GPR/Expected Improvement、VMC block average 预览",
        ],
        "docs_copied": [
            "PHYSICAL_MODELS.md",
            "FUNCTION_MATRIX.md",
            "OPTIMIZATION_ROADMAP.md",
            "TESTING_STRATEGY.md",
            "UNIT_SYSTEM.md",
        ],
        "not_merged_directly": [
            "Si-O/frontend/src 中的 Three.js、ReactFlow、Yjs、Playwright 页面未直接覆盖根项目，原因是依赖版本和架构差异较大。",
            "子项目中的 Ultra/SiC/自由基主题仅作为后反应扩展模块，不改写当前 Ziegler–Natta 主机制结论。",
        ],
        "reliability_note": "所有合并能力仍遵守：不执行 Gaussian、不执行任意 shell、示例数据必须标注，真实结论只能来自上传解析或用户核验数据。",
    }
