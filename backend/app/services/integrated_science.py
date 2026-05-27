from __future__ import annotations

from typing import Any

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_KCAL_MOL
from app.services.ultra_science import calculate_boltzmann_weights


def calculate_relative_energies(energies_hartree: list[float], reference_idx: int = 0) -> list[float]:
    if not energies_hartree:
        raise ValueError("能量列表不能为空。")
    if reference_idx < 0 or reference_idx >= len(energies_hartree):
        raise ValueError("参考态索引超出范围。")
    reference = energies_hartree[reference_idx]
    return [(energy - reference) * HARTREE_TO_KCAL_MOL for energy in energies_hartree]


def ensemble_average(properties: list[float], weights: list[float]) -> float:
    if len(properties) != len(weights):
        raise ValueError("性质列表和权重列表长度必须一致。")
    if not properties:
        raise ValueError("性质列表不能为空。")
    return sum(property_value * weight for property_value, weight in zip(properties, weights))


def analyze_reaction_profile(states: list[dict[str, Any]], temp_k: float = DEFAULT_TEMPERATURE_K) -> dict[str, Any]:
    if not states:
        raise ValueError("至少需要一个反应态。")
    energies_hartree: list[float] = []
    for state in states:
        if state.get("energy_hartree") is None:
            raise ValueError("每个反应态都必须提供 energy_hartree。")
        energies_hartree.append(float(state["energy_hartree"]))

    relative = calculate_relative_energies(energies_hartree)
    weights = calculate_boltzmann_weights(relative, temp_k)
    barriers = []
    for index, state in enumerate(states):
        name = str(state.get("name", f"state-{index + 1}"))
        if "TS" in name.upper() or "过渡态" in name:
            previous_min = min(relative[: index + 1]) if index > 0 else 0.0
            barriers.append(
                {
                    "ts_name": name,
                    "barrier_kcal_mol": relative[index] - previous_min,
                    "relative_energy_kcal_mol": relative[index],
                }
            )

    return {
        "profile": [
            {
                "state": str(states[index].get("name", f"state-{index + 1}")),
                "relative_energy_kcal_mol": relative[index],
                "boltzmann_weight": weights[index],
                "source": states[index].get("source", "用户输入"),
            }
            for index in range(len(states))
        ],
        "barriers": barriers,
        "reaction_energy_kcal_mol": relative[-1],
        "temperature_k": temp_k,
        "reliability_note": "反应剖面只基于用户传入能量；不会自动补全 TS、IRC 或产物态。",
    }


def integration_source_map() -> dict[str, Any]:
    return {
        "status": "已拆解独立 Si-O 文件夹；当前只在根工作目录内活动",
        "strategy": "将原 Si-O 子项目按功能拆解到 integrated/origin-*，并把可运行能力迁入 backend、frontend、docs、scripts 的根项目体系。",
        "backend_integrated": [
            "backend/app/services/advanced_gaussian_builder.py",
            "backend/app/services/integrated_science.py",
            "backend/app/services/molecule_intelligence.py",
            "backend/app/services/ultra_science.py",
        ],
        "frontend_integrated": [
            "frontend/lib/advanced-science.ts",
            "frontend/lib/integrated-catalyst-database.ts",
            "frontend/components/modules/merged-ultra-panel.tsx",
        ],
        "dismantled_source_locations": {
            "frontend": "integrated/origin-frontend",
            "backend": "integrated/origin-backend",
            "docs": "integrated/origin-docs",
            "scripts": "integrated/origin-scripts",
            "deployment": "integrated/origin-deployment",
            "assets": "integrated/origin-assets",
        },
        "docs_integrated": [
            "docs/MERGE_REPORT.md",
            "docs/INTEGRATION_SOURCE_MAP.md",
            "docs/merged-from-si-o/",
        ],
        "active_rule": "后续开发只在根目录 D:\\codex2_cataSi-O 下运行、验证和启动；独立 Si-O 文件夹已移除。",
    }
