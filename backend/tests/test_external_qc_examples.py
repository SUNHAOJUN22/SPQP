from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_external_qc_examples_check_only(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "run_external_qc_examples.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--check-only",
            "--workdir",
            str(tmp_path / "external-qc-check"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "未执行外部程序" in result.stdout
    assert (tmp_path / "external-qc-check" / "water_opt_freq_nbo.gjf").exists()
    assert (tmp_path / "external-qc-check" / "EXTERNAL_QC_RUN_REPORT.md").exists()


def test_external_qc_examples_list_command() -> None:
    script = ROOT / "scripts" / "run_external_qc_examples.py"
    result = subprocess.run(
        [sys.executable, str(script), "--list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Gaussian: water_opt_freq_nbo.gjf" in result.stdout
    assert "cubegen" in result.stdout
    assert "Multiwfn" in result.stdout
