"""Root pytest launcher compatibility for Windows developer shells.

The backend test suite lives under ``backend/`` and its dependencies are
installed in ``backend/.venv``.  The project scripts already use that
interpreter, but the engineering acceptance checklist also calls raw
``pytest`` and ``pytest --cov`` from the repository root.  This root conftest
keeps those commands reproducible without changing any test assertions.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys


def _venv_python() -> Path:
    root = Path(__file__).resolve().parent
    if os.name == "nt":
        return root / "backend" / ".venv" / "Scripts" / "python.exe"
    return root / "backend" / ".venv" / "bin" / "python"


def pytest_addoption(parser) -> None:
    """Accept coverage flags when the outer pytest lacks pytest-cov.

    The command is re-executed inside the backend venv during configure; this
    shim only lets argument parsing reach that point in a bare Python shell.
    """

    if importlib.util.find_spec("pytest_cov") is not None:
        return
    group = parser.getgroup("sio root compatibility")
    group.addoption("--cov", action="append", nargs="?", default=[], help="转交给后端 venv 的 pytest-cov")
    group.addoption("--cov-report", action="append", default=[], help="转交给后端 venv 的 pytest-cov")


def pytest_configure(config) -> None:
    if os.environ.get("SIO_BACKEND_PYTEST_REEXEC") == "1":
        return

    venv_python = _venv_python()
    if not venv_python.exists():
        return

    current = Path(sys.executable).resolve()
    if current == venv_python.resolve():
        return

    env = os.environ.copy()
    env["SIO_BACKEND_PYTEST_REEXEC"] = "1"
    completed = subprocess.run(
        [str(venv_python), "-m", "pytest", *sys.argv[1:]],
        cwd=Path(__file__).resolve().parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.stdout:
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(completed.returncode)
