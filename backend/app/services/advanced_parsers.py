from __future__ import annotations

import re
from pathlib import Path
from typing import Any


FLOAT = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[DEde][-+]?\d+)?"


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace("D", "E").replace("d", "e"))
    except ValueError:
        return None


def parse_goodvibes_output(text: str, file_name: str = "goodvibes.out") -> dict[str, Any]:
    """Read-only GoodVibes table parser.

    The parser extracts common quasi-harmonic thermochemistry rows without executing
    GoodVibes. Missing values remain None and are reported in Chinese warnings.
    """

    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ".log" not in line and ".out" not in line:
            continue
        parts = line.split()
        name_index = next((idx for idx, part in enumerate(parts) if part.lower().endswith((".log", ".out"))), None)
        if name_index is None:
            continue
        numbers = [_to_float(value) for value in re.findall(FLOAT, line)]
        numbers = [value for value in numbers if value is not None]
        rows.append(
            {
                "file": Path(parts[name_index]).name,
                "temperature_k": numbers[0] if len(numbers) >= 5 and 250 <= numbers[0] <= 500 else None,
                "qh_gibbs_hartree": numbers[-1] if numbers else None,
                "raw": line.strip(),
            }
        )

    warnings: list[str] = []
    if not rows:
        warnings.append("当前文件中未找到 GoodVibes 热化学校正表。")
    return {
        "file": Path(file_name).name,
        "quality": "partial" if rows else "failed",
        "entries": rows,
        "units": {"energy": "hartree", "temperature": "K"},
        "warnings": warnings,
        "provenance": "GoodVibes 输出只读解析；服务器未执行 GoodVibes 或 Gaussian。",
    }


def parse_qtaim_output(text: str, file_name: str = "qtaim.txt") -> dict[str, Any]:
    points: list[dict[str, Any]] = []
    for line in text.splitlines():
        lower = line.lower()
        if "bcp" not in lower and "bond critical point" not in lower:
            continue
        label_match = re.search(r"([A-Za-z]{1,3}\d*\s*[-–]\s*[A-Za-z]{1,3}\d*)", line)
        rho = _first_after(["rho", "ρ"], line)
        lap = _first_after(["laplacian", "del2", "∇²", "nabla"], line)
        h_bcp = _first_after(["h=", "h_bcp", "hbcp"], line)
        v_bcp = _first_after(["v=", "v_bcp", "vbcp"], line)
        g_bcp = _first_after(["g=", "g_bcp", "gbcp"], line)
        ellip = _first_after(["ellipticity", "eps", "ε"], line)
        points.append(
            {
                "label": label_match.group(1).replace(" ", "") if label_match else line.strip()[:80],
                "rho_bcp": rho,
                "laplacian_rho_bcp": lap,
                "h_bcp": h_bcp,
                "v_bcp": v_bcp,
                "g_bcp": g_bcp,
                "ellipticity": ellip,
                "raw": line.strip(),
            }
        )

    warnings: list[str] = []
    if not points:
        warnings.append("当前文件中未找到 QTAIM 键临界点数据。")
    return {
        "file": Path(file_name).name,
        "quality": "partial" if points else "failed",
        "bond_critical_points": points,
        "units": {"rho_bcp": "a.u.", "laplacian": "a.u.", "energy_density": "a.u."},
        "warnings": warnings,
        "provenance": "QTAIM 文本只读解析；结果需与 Multiwfn/AIMAll 原始输出核验。",
    }


def parse_nci_output(text: str, file_name: str = "nci.txt") -> dict[str, Any]:
    regions: list[dict[str, Any]] = []
    for line in text.splitlines():
        lower = line.lower()
        if "lambda2" not in lower and "λ2" not in lower and "rdg" not in lower and "sign" not in lower:
            continue
        sign_l2rho = _first_after(["sign(lambda2)rho", "sign(λ2)ρ", "lambda2rho", "λ2rho"], line)
        rdg = _first_after(["rdg"], line)
        interaction, color = classify_nci_region(sign_l2rho)
        regions.append(
            {
                "sign_lambda2_rho": sign_l2rho,
                "rdg": rdg,
                "interaction_type": interaction,
                "color": color,
                "raw": line.strip(),
            }
        )

    warnings: list[str] = []
    if not regions:
        warnings.append("当前文件中未找到 NCI/RDG 区域数据。")
    return {
        "file": Path(file_name).name,
        "quality": "partial" if regions else "failed",
        "regions": regions,
        "legend": {
            "blue": "强吸引",
            "green": "弱范德华",
            "red": "空间排斥",
        },
        "warnings": warnings,
        "provenance": "NCI/RDG 文本只读解析；不执行 Multiwfn，不生成真实等值面。",
    }


def classify_nci_region(sign_lambda2_rho: float | None) -> tuple[str, str]:
    if sign_lambda2_rho is None:
        return "数据缺失", "gray"
    if sign_lambda2_rho < -0.02:
        return "强吸引", "blue"
    if sign_lambda2_rho > 0.02:
        return "空间排斥", "red"
    return "弱范德华", "green"


def _first_after(labels: list[str], line: str) -> float | None:
    for label in labels:
        pattern = re.escape(label) + r"\s*[:=]?\s*(" + FLOAT + r")"
        match = re.search(pattern, line, flags=re.IGNORECASE)
        if match:
            return _to_float(match.group(1))
    return None
