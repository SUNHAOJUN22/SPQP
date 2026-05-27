from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.core.constants import HARTREE_TO_EV
from app.schemas.api import ParsedGaussianLog, UnitValue


FLOAT = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[DEde][-+]?\d+)?"


def _as_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace("D", "E").replace("d", "e"))
    except ValueError:
        return None


def _last_float(pattern: str, text: str, flags: int = 0) -> float | None:
    matches = re.findall(pattern, text, flags)
    if not matches:
        return None
    last = matches[-1]
    if isinstance(last, tuple):
        last = next((item for item in reversed(last) if item), None)
    return _as_float(str(last)) if last is not None else None


def _all_float_values(values: list[str]) -> list[float]:
    parsed: list[float] = []
    for value in values:
        number = _as_float(value)
        if number is not None:
            parsed.append(number)
    return parsed


def parse_frequencies(text: str) -> tuple[list[float], int | None, float | None]:
    values: list[float] = []
    for line in text.splitlines():
        if "Frequencies --" in line:
            values.extend(_all_float_values(re.findall(FLOAT, line.split("--", 1)[1])))
    if not values:
        return [], None, None
    return values, sum(1 for value in values if value < 0), min(values)


def parse_frontier_orbitals(text: str) -> tuple[float | None, float | None, float | None]:
    occ_values: list[float] = []
    virt_values: list[float] = []
    for line in text.splitlines():
        lower = line.lower()
        if "occ. eigenvalues --" in lower:
            occ_values.extend(_all_float_values(re.findall(FLOAT, line.split("--", 1)[1])))
        elif "virt. eigenvalues --" in lower:
            virt_values.extend(_all_float_values(re.findall(FLOAT, line.split("--", 1)[1])))
    homo = occ_values[-1] if occ_values else None
    lumo = virt_values[0] if virt_values else None
    gap_ev = (lumo - homo) * HARTREE_TO_EV if homo is not None and lumo is not None else None
    return homo, lumo, gap_ev


def parse_dipole(text: str) -> float | None:
    dipole_matches = re.findall(r"Tot=\s*(" + FLOAT + r")", text)
    return _as_float(dipole_matches[-1]) if dipole_matches else None


def parse_mulliken_charges(text: str) -> list[dict[str, Any]] | None:
    lines = text.splitlines()
    charges: list[dict[str, Any]] = []
    capture = False
    for line in lines:
        if "Mulliken charges:" in line:
            capture = True
            charges = []
            continue
        if capture:
            if "Sum of Mulliken charges" in line:
                break
            match = re.match(r"\s*(\d+)\s+([A-Za-z]{1,3})\s+(" + FLOAT + r")\s*$", line)
            if match:
                charges.append(
                    {
                        "atom_index": int(match.group(1)),
                        "element": match.group(2),
                        "charge": _as_float(match.group(3)),
                    }
                )
    return charges or None


def parse_npa_charges(text: str) -> list[dict[str, Any]] | None:
    lines = text.splitlines()
    charges: list[dict[str, Any]] = []
    capture = False
    for line in lines:
        if "Summary of Natural Population Analysis" in line:
            capture = True
            charges = []
            continue
        if capture and "Natural Population" in line and "Natural Charge" in line:
            continue
        if capture:
            if line.strip().startswith("=") or "NATURAL POPULATIONS" in line:
                if charges:
                    break
                continue
            match = re.match(r"\s*([A-Za-z]{1,3})\s+(\d+)\s+(" + FLOAT + r")", line)
            if match:
                charges.append(
                    {
                        "element": match.group(1),
                        "atom_index": int(match.group(2)),
                        "charge": _as_float(match.group(3)),
                    }
                )
            elif charges and not line.strip():
                break
    return charges or None


def parse_wiberg_summary(text: str) -> list[str] | None:
    lines = text.splitlines()
    snippets: list[str] = []
    capture = False
    for line in lines:
        if "Wiberg bond index" in line:
            capture = True
            snippets = [line.strip()]
            continue
        if capture:
            if not line.strip() and len(snippets) > 1:
                break
            if len(snippets) < 24:
                snippets.append(line.rstrip())
    return snippets or None


def parse_wiberg_matrix(text: str) -> list[dict[str, Any]] | None:
    lines = text.splitlines()
    entries: list[dict[str, Any]] = []
    start = None
    for index, line in enumerate(lines):
        if "Wiberg bond index matrix in the NAO basis" in line:
            start = index + 1
            break
    if start is None:
        return None

    current_columns: list[int] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            if entries:
                break
            continue
        if stripped.startswith("=") or "Atom" in stripped and "NAO" in stripped:
            continue
        parts = stripped.split()
        if not parts:
            continue
        if parts[0].lower() == "atom":
            current_columns = [int(value) for value in parts[1:] if value.isdigit()]
            continue
        if len(parts) < 3 or not parts[0].isdigit():
            if entries and ("NBO" in line or "Natural" in line):
                break
            continue
        row_atom = int(parts[0])
        values = parts[2:] if len(parts) > 2 and re.match(r"^[A-Za-z]{1,3}$", parts[1]) else parts[1:]
        for offset, raw_value in enumerate(values):
            if offset >= len(current_columns):
                continue
            value = _as_float(raw_value)
            if value is None:
                continue
            col_atom = current_columns[offset]
            if row_atom >= col_atom:
                continue
            entries.append({"atom_i": row_atom, "atom_j": col_atom, "wbi": value})
    return entries or None


def parse_spin_multiplicity(text: str) -> int | None:
    match = re.search(r"Multiplicity\s*=\s*(\d+)", text)
    return int(match.group(1)) if match else None


def parse_mulliken_spin_densities(text: str) -> list[dict[str, Any]] | None:
    lines = text.splitlines()
    densities: list[dict[str, Any]] = []
    capture = False
    for line in lines:
        if "Mulliken atomic spin densities" in line:
            capture = True
            densities = []
            continue
        if not capture:
            continue
        stripped = line.strip()
        if not stripped:
            if densities:
                break
            continue
        if "Sum of Mulliken" in line:
            break
        match = re.match(r"\s*(\d+)\s+([A-Za-z]{1,3})?\s*(" + FLOAT + r")\s*$", line)
        if match:
            densities.append(
                {
                    "atom_index": int(match.group(1)),
                    "element": match.group(2) or None,
                    "spin_density": _as_float(match.group(3)),
                }
            )
    return densities or None


def parse_nbo_interactions(text: str) -> list[dict[str, Any]] | None:
    interactions: list[dict[str, Any]] = []
    in_section = False
    for line in text.splitlines():
        if "Second Order Perturbation Theory Analysis" in line:
            in_section = True
            continue
        if in_section and "Natural Bond Orbitals" in line and interactions:
            break
        if not in_section:
            continue
        numbers = re.findall(FLOAT, line)
        if len(numbers) < 3:
            continue
        if "RY" not in line and "BD" not in line and "LP" not in line and "CR" not in line:
            continue
        e2 = _as_float(numbers[-3])
        if e2 is None:
            continue
        donor: str | None = None
        acceptor: str | None = None
        if "/" in line:
            donor_part, acceptor_part = line.split("/", 1)
            donor = re.sub(r"^\s*\d+\.\s*", "", donor_part).strip() or None
            acceptor_text = re.sub(r"\s+" + FLOAT + r"\s+" + FLOAT + r"\s+" + FLOAT + r"\s*$", "", acceptor_part).strip()
            acceptor = re.sub(r"^\s*\d+\.\s*", "", acceptor_text).strip() or None
        parts = re.split(r"\s{2,}", line.strip())
        interactions.append(
            {
                "raw": line.strip(),
                "donor": donor or (parts[1] if len(parts) > 1 else None),
                "acceptor": acceptor or (parts[2] if len(parts) > 2 else None),
                "e2_kcal_mol": e2,
            }
        )
    return interactions or None


def make_unit(value: Any, unit: str | None, source: str = "uploaded") -> UnitValue:
    return UnitValue(value=value, unit=unit, source=source)


def parse_gaussian_log_text(text: str, file_name: str = "uploaded.log") -> ParsedGaussianLog:
    normal_termination = "Normal termination of Gaussian" in text
    scf = _last_float(r"SCF Done:\s+E\([^)]+\)\s+=\s+(" + FLOAT + r")", text)
    zpe = _last_float(r"Zero-point correction=\s+(" + FLOAT + r")", text)
    thermal_energy = _last_float(r"Thermal correction to Energy=\s+(" + FLOAT + r")", text)
    thermal_enthalpy = _last_float(r"Thermal correction to Enthalpy=\s+(" + FLOAT + r")", text)
    thermal_gibbs = _last_float(r"Thermal correction to Gibbs Free Energy=\s+(" + FLOAT + r")", text)
    sum_zpe = _last_float(r"Sum of electronic and zero-point Energies=\s+(" + FLOAT + r")", text)
    sum_enthalpy = _last_float(r"Sum of electronic and thermal Enthalpies=\s+(" + FLOAT + r")", text)
    sum_free = _last_float(r"Sum of electronic and thermal Free Energies=\s+(" + FLOAT + r")", text)
    counterpoise = _last_float(r"Counterpoise corrected energy\s*=\s*(" + FLOAT + r")", text, re.IGNORECASE)
    frequencies, n_imag, lowest_frequency = parse_frequencies(text)
    homo, lumo, gap_ev = parse_frontier_orbitals(text)
    dipole = parse_dipole(text)
    mulliken = parse_mulliken_charges(text)
    npa = parse_npa_charges(text)
    wiberg = {"snippets": parse_wiberg_summary(text), "matrix": parse_wiberg_matrix(text)}
    if wiberg["snippets"] is None and wiberg["matrix"] is None:
        wiberg = None  # type: ignore[assignment]
    spin_multiplicity = parse_spin_multiplicity(text)
    spin_densities = parse_mulliken_spin_densities(text)
    nbo_interactions = parse_nbo_interactions(text)

    field_values = {
        "normal_termination": normal_termination,
        "scf_hartree": scf,
        "gibbs_hartree": sum_free,
        "n_imag": n_imag,
        "lowest_freq_cm-1": lowest_frequency,
        "homo_hartree": homo,
        "lumo_hartree": lumo,
        "gap_ev": gap_ev,
        "dipole_debye": dipole,
    }
    missing = [key for key, value in field_values.items() if value is None]
    chinese_warnings: list[str] = []
    if not normal_termination:
        chinese_warnings.append("未检测到 Gaussian 正常终止标记。")
    if sum_free is None:
        chinese_warnings.append("当前文件中未找到吉布斯自由能。")
    if nbo_interactions is None:
        chinese_warnings.append("当前文件中未找到 NBO 二阶微扰分析结果。")
    core_count = sum(value is not None for value in [scf, sum_free, n_imag, homo, lumo])
    if core_count >= 4 and normal_termination:
        quality = "complete"
    elif core_count > 0 or normal_termination:
        quality = "partial"
    else:
        quality = "failed"

    return ParsedGaussianLog(
        file=Path(file_name).name,
        normal_termination=make_unit(normal_termination, None),
        scf_hartree=make_unit(scf, "hartree"),
        zpe_correction_hartree=make_unit(zpe, "hartree"),
        thermal_correction_energy_hartree=make_unit(thermal_energy, "hartree"),
        thermal_correction_enthalpy_hartree=make_unit(thermal_enthalpy, "hartree"),
        thermal_correction_gibbs_hartree=make_unit(thermal_gibbs, "hartree"),
        sum_electronic_zpe_hartree=make_unit(sum_zpe, "hartree"),
        sum_electronic_thermal_enthalpy_hartree=make_unit(sum_enthalpy, "hartree"),
        sum_electronic_thermal_free_hartree=make_unit(sum_free, "hartree"),
        gibbs_hartree=make_unit(sum_free, "hartree"),
        frequencies_cm_1=make_unit(frequencies if frequencies else None, "cm^-1"),
        n_imag=make_unit(n_imag, "count"),
        lowest_freq_cm_1=make_unit(lowest_frequency, "cm^-1"),
        homo_hartree=make_unit(homo, "hartree"),
        lumo_hartree=make_unit(lumo, "hartree"),
        gap_ev=make_unit(gap_ev, "eV"),
        dipole_debye=make_unit(dipole, "Debye"),
        mulliken_charges=make_unit(mulliken, "e"),
        npa_charges=make_unit(npa, "e"),
        wiberg_bond_indices=make_unit(wiberg, None),
        spin_multiplicity=make_unit(spin_multiplicity, "count"),
        mulliken_spin_densities=make_unit(spin_densities, "e"),
        nbo_interactions=make_unit(nbo_interactions, "kcal/mol"),
        counterpoise_corrected_energy_hartree=make_unit(counterpoise, "hartree"),
        quality=quality,  # type: ignore[arg-type]
        missing_fields=missing,
        chinese_warnings=chinese_warnings,
        units={
            "energy": "hartree",
            "relative_energy": "kcal/mol",
            "frequency": "cm^-1",
            "orbital_gap": "eV",
            "dipole": "Debye",
            "charge": "e",
        },
    )
