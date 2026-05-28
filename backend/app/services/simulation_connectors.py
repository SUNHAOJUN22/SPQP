from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from app.services.advanced_parsers import parse_goodvibes_output, parse_nci_output, parse_qtaim_output
from app.services.cube import parse_cube_metadata
from app.services.gaussian_parser import parse_gaussian_log_text
from app.schemas.api import GaussianInputRequest
from app.services.gaussian_templates import generate_gaussian_input


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "tool_type": "gaussian16",
        "display_name": "Gaussian16",
        "default_mode": "template_only",
        "safety_level": "external-disabled",
        "allowed_extensions": [".gjf", ".com", ".log", ".out", ".chk", ".fchk"],
    },
    {
        "tool_type": "formchk",
        "display_name": "formchk",
        "default_mode": "template_only",
        "safety_level": "external-disabled",
        "allowed_extensions": [".chk", ".fchk"],
    },
    {
        "tool_type": "cubegen",
        "display_name": "cubegen",
        "default_mode": "template_only",
        "safety_level": "external-disabled",
        "allowed_extensions": [".fchk", ".cube", ".cub"],
    },
    {
        "tool_type": "multiwfn",
        "display_name": "Multiwfn",
        "default_mode": "template_only",
        "safety_level": "external-disabled",
        "allowed_extensions": [".fchk", ".wfn", ".wfx", ".cube", ".txt"],
    },
    {
        "tool_type": "goodvibes",
        "display_name": "GoodVibes",
        "default_mode": "parse_only",
        "safety_level": "parser-only",
        "allowed_extensions": [".out", ".txt", ".csv"],
    },
    {
        "tool_type": "rdkit",
        "display_name": "RDKit",
        "default_mode": "template_only",
        "safety_level": "local-library",
        "allowed_extensions": [".smi", ".mol", ".sdf", ".xyz"],
    },
    {
        "tool_type": "slurm",
        "display_name": "SLURM",
        "default_mode": "template_only",
        "safety_level": "template-only",
        "allowed_extensions": [".sh", ".gjf", ".com"],
    },
    {
        "tool_type": "local_queue",
        "display_name": "本地任务队列",
        "default_mode": "disabled",
        "safety_level": "disabled",
        "allowed_extensions": [],
    },
    {
        "tool_type": "parser_only",
        "display_name": "只读解析器",
        "default_mode": "parse_only",
        "safety_level": "parser-only",
        "allowed_extensions": [".log", ".out", ".cube", ".cub", ".txt", ".csv", ".json"],
    },
]


def default_simulation_tools() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(TOOL_DEFINITIONS, start=1):
        rows.append(
            {
                "id": -index,
                "project_id": None,
                "tool_type": item["tool_type"],
                "display_name": item["display_name"],
                "executable_path": None,
                "is_configured": False,
                "can_execute": False,
                "default_mode": item["default_mode"],
                "safety_level": item["safety_level"],
                "allowed_extensions": item["allowed_extensions"],
                "working_directory": None,
                "validation_status": "missing",
                "warnings": ["当前未配置外部程序；默认仅生成模板和只读解析，不执行科学计算程序。"],
                "created_at": None,
                "updated_at": None,
            }
        )
    return rows


def validate_tool_template(tool: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    executable_path = str(tool.get("executable_path") or "").strip()
    working_directory = str(tool.get("working_directory") or "").strip()
    if not executable_path:
        warnings.append("当前未配置可执行文件路径。")
        validation_status = "missing"
    elif _has_path_traversal(executable_path):
        warnings.append("检测到非法路径，禁止登记。")
        validation_status = "invalid-path"
    else:
        validation_status = "template-valid"
        warnings.append("仅完成路径格式检查；未执行 version command。")

    if working_directory and _has_path_traversal(working_directory):
        validation_status = "invalid-path"
        warnings.append("工作目录包含非法路径片段。")

    default_mode = str(tool.get("default_mode") or "template_only")
    can_execute = default_mode == "confirmed_execute" and validation_status == "template-valid"
    if can_execute:
        warnings.append("即使工具标记为可确认执行，默认 API 仍不会运行外部程序；需要独立二次确认工作流。")

    return {
        "validation_status": validation_status,
        "warnings": warnings,
        "is_configured": validation_status == "template-valid",
        "can_execute": can_execute,
        "safety_note": "本验证不执行 Gaussian、cubegen、Multiwfn、GoodVibes、version command 或用户上传文件。",
    }


def build_simulation_job_template(payload: Any) -> dict[str, Any]:
    job_type = str(getattr(payload, "job_type", "gaussian_input"))
    tool_type = str(getattr(payload, "tool_type", "gaussian16"))
    molecule_name = str(getattr(payload, "molecule_name", "MCSOMe"))
    coordinates = str(getattr(payload, "coordinates", "") or "")
    command_template = ""
    generated_text = ""
    expected = list(getattr(payload, "output_files_expected", []) or [])

    if job_type in {"gaussian_input", "isolated_monomer_opt", "insertion_ts"}:
        gaussian = generate_gaussian_input(
            GaussianInputRequest(
                name=molecule_name,
                job_type="insertion TS" if job_type == "insertion_ts" else "isolated monomer opt/freq/NBO",
                method=str(getattr(payload, "method", "B3LYP")),
                basis=str(getattr(payload, "basis", "Def2SVP")),
                charge=int(getattr(payload, "charge", 0)),
                multiplicity=int(getattr(payload, "multiplicity", 1)),
                coordinates=coordinates,
            )
        )
        generated_text = gaussian.content
        command_template = f"g16 < {gaussian.file_name} > {Path(gaussian.file_name).stem}.log"
        expected = expected or [f"{Path(gaussian.file_name).stem}.log"]
    elif job_type == "cubegen_density":
        command_template = "cubegen 0 density=scf input.fchk density.cube 0 h"
        generated_text = "# cubegen 电子密度命令模板；未执行。"
        expected = expected or ["density.cube"]
    elif job_type == "cubegen_esp":
        command_template = "cubegen 0 potential=scf input.fchk esp.cube 0 h"
        generated_text = "# cubegen ESP 静电势命令模板；未执行。"
        expected = expected or ["esp.cube"]
    elif job_type == "cubegen_homo_lumo":
        command_template = "cubegen 0 MO=HOMO input.fchk homo.cube 0 h\ncubegen 0 MO=LUMO input.fchk lumo.cube 0 h"
        generated_text = "# cubegen HOMO/LUMO 命令模板；未执行。"
        expected = expected or ["homo.cube", "lumo.cube"]
    elif job_type == "multiwfn_qtaim":
        command_template = "Multiwfn input.fchk < multiwfn_qtaim.inp > qtaim.txt"
        generated_text = "2\n2\n0\n# Multiwfn QTAIM 脚本模板；未执行。"
        expected = expected or ["qtaim.txt"]
    elif job_type == "multiwfn_nci":
        command_template = "Multiwfn input.fchk < multiwfn_nci.inp > nci.txt"
        generated_text = "20\n4\n0\n# Multiwfn NCI/RDG 脚本模板；未执行。"
        expected = expected or ["nci.txt"]
    elif job_type == "goodvibes_parse":
        command_template = "goodvibes *.log --qs grimme"
        generated_text = "# GoodVibes 解析任务模板；平台默认只解析用户提供的 GoodVibes 输出文本。"
        expected = expected or ["GoodVibes output text"]
    elif job_type == "slurm_template":
        command_template = "sbatch gaussian_job.slurm"
        generated_text = _slurm_template(molecule_name)
        expected = expected or [f"{molecule_name}.log"]
    else:
        generated_text = f"# {job_type} 任务草稿；当前仅保存模板，不执行外部程序。"
        command_template = f"# {tool_type} command template for {job_type}; not executed"

    requires_confirmation = tool_type in {"gaussian16", "formchk", "cubegen", "multiwfn", "goodvibes", "slurm"}
    return {
        "job_type": job_type,
        "tool_type": tool_type,
        "execution_mode": str(getattr(payload, "execution_mode", "template_only")),
        "status": "draft",
        "input_files": list(getattr(payload, "input_files", []) or []),
        "output_files_expected": expected,
        "generated_text": generated_text,
        "command_template": command_template,
        "will_execute": False,
        "requires_user_confirmation": requires_confirmation,
        "evidence_grade": "D",
        "provenance": {
            "policy": "任务仅为模板或解析草稿；未执行外部科学计算程序。",
            "safety_boundary": "will_execute = false；外部执行需要显式配置和二次确认。",
        },
        "warnings": ["模板任务不能作为真实计算结果；上传真实输出并解析后才可能升级为 A 级计算证据。"],
    }


def parse_simulation_text(parser_name: str, text: str, file_name: str, is_mock: bool = False) -> dict[str, Any]:
    normalized_parser = parser_name.replace("-", "_").lower()
    if normalized_parser in {"gaussian", "gaussian_log", "parse_gaussian_log"}:
        parsed = parse_gaussian_log_text(text, file_name).model_dump(by_alias=True)
        quality = parsed.get("quality", "partial")
        units = parsed.get("units", {})
        warnings = parsed.get("chinese_warnings", [])
    elif normalized_parser in {"cube", "parse_cube"}:
        try:
            parsed = parse_cube_metadata(text, file_name)
            quality = "complete" if parsed.get("atom_count", 0) > 0 else "partial"
            units = {"grid": "bohr or angstrom from cube header", "scalar": "a.u."}
            warnings = parsed.get("warnings", [])
        except ValueError as exc:
            parsed = {"file": Path(file_name).name, "quality": "failed", "error": str(exc)}
            quality = "failed"
            units = {}
            warnings = [str(exc)]
    elif normalized_parser in {"nbo", "parse_nbo"}:
        parsed = parse_nbo_output(text, file_name)
        quality = parsed["quality"]
        units = parsed["units"]
        warnings = parsed["warnings"]
    elif normalized_parser in {"qtaim", "parse_qtaim"}:
        parsed = parse_qtaim_output(text, file_name)
        quality = parsed["quality"]
        units = parsed["units"]
        warnings = parsed["warnings"]
    elif normalized_parser in {"nci", "parse_nci"}:
        parsed = parse_nci_output(text, file_name)
        quality = parsed["quality"]
        units = {"sign_lambda2_rho": "a.u.", "rdg": "dimensionless"}
        warnings = parsed["warnings"]
    elif normalized_parser in {"goodvibes", "parse_goodvibes"}:
        parsed = parse_goodvibes_output(text, file_name)
        quality = parsed["quality"]
        units = parsed["units"]
        warnings = parsed["warnings"]
    else:
        parsed = {"file": Path(file_name).name, "quality": "failed", "error": "未知 parser。"}
        quality = "failed"
        units = {}
        warnings = ["未知 parser，无法解析。"]

    evidence_grade = "D" if is_mock or quality == "failed" else "A"
    return {
        "parser_name": normalized_parser,
        "source_file": Path(file_name).name,
        "source_type": "text",
        "quality": quality,
        "normalized_json": parsed,
        "units": units,
        "warnings": warnings,
        "errors": [str(parsed.get("error"))] if isinstance(parsed, dict) and parsed.get("error") else [],
        "evidence_grade": evidence_grade,
        "is_mock": is_mock,
        "provenance": {
            "policy": "只读解析用户提供文本；未执行外部科学计算程序。",
            "paper_ready": "需要人工核验计算设置、收敛、频率/TS/IRC 和原始文件来源。",
        },
    }


def parse_nbo_output(text: str, file_name: str = "nbo.txt") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if "->" not in line and "→" not in line:
            continue
        e2_match = re.search(r"E\(2\)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)", line, flags=re.IGNORECASE)
        gap_match = re.search(r"(?:gap|energy\s+gap)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)", line, flags=re.IGNORECASE)
        fock_match = re.search(r"(?:F\(i,j\)|Fock)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)", line, flags=re.IGNORECASE)
        arrow = "→" if "→" in line else "->"
        donor, acceptor = [part.strip() for part in line.split(arrow, 1)]
        rows.append(
            {
                "donor": donor[:120],
                "acceptor": acceptor.split()[0] if acceptor else None,
                "e2_kcal_mol": float(e2_match.group(1)) if e2_match else None,
                "energy_gap_au": float(gap_match.group(1)) if gap_match else None,
                "fock_matrix_element_au": float(fock_match.group(1)) if fock_match else None,
                "raw": line.strip(),
            }
        )
    warnings = [] if rows else ["当前文件中未找到 NBO 二阶微扰给体-受体相互作用。"]
    return {
        "file": Path(file_name).name,
        "quality": "partial" if rows else "failed",
        "nbo_interactions": rows,
        "units": {"e2": "kcal/mol", "energy_gap": "a.u.", "fock": "a.u."},
        "warnings": warnings,
        "provenance": "NBO 文本只读解析；未执行 Gaussian 或 NBO 程序。",
    }


def _slurm_template(name: str) -> str:
    return "\n".join(
        [
            "#!/bin/bash",
            f"#SBATCH --job-name={name}_gaussian",
            "#SBATCH --nodes=1",
            "#SBATCH --ntasks=16",
            "#SBATCH --time=24:00:00",
            "#SBATCH --mem=48G",
            "",
            "module load gaussian",
            f"g16 < {name}.gjf > {name}.log",
            "",
            "# 该 SLURM 文件仅为模板，平台未提交任务。",
        ]
    )


def _has_path_traversal(value: str) -> bool:
    if "\x00" in value or ".." in value:
        return True
    try:
        if PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute():
            return False
    except ValueError:
        return True
    return False
