from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "external-qc"
DEFAULT_RUN_ROOT = ROOT / "storage" / "external-qc-runs"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


@dataclass(frozen=True)
class ToolPaths:
    gaussian: Path | None
    formchk: Path | None
    cubegen: Path | None
    multiwfn: Path | None


def resolve_tool(explicit: str | None, env_names: list[str], candidates: list[str]) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.exists() else None
    for name in env_names:
        value = os.environ.get(name)
        if value:
            path = Path(value).expanduser()
            if path.exists():
                return path
    for candidate in candidates:
        located = shutil.which(candidate)
        if located:
            return Path(located)
    return None


def discover_tools(args: argparse.Namespace) -> ToolPaths:
    return ToolPaths(
        gaussian=resolve_tool(args.gaussian, ["GAUSSIAN_EXE", "GAUSSIAN_CMD", "G16_EXE", "G09_EXE"], ["g16", "g16.exe", "g09", "g09.exe", "gaussian"]),
        formchk=resolve_tool(args.formchk, ["FORMCHK_EXE"], ["formchk", "formchk.exe"]),
        cubegen=resolve_tool(args.cubegen, ["CUBEGEN_EXE"], ["cubegen", "cubegen.exe"]),
        multiwfn=resolve_tool(args.multiwfn, ["MULTIWFN_EXE", "MULTIWFN"], ["Multiwfn", "Multiwfn.exe", "multiwfn"]),
    )


def print_tools(tools: ToolPaths) -> None:
    print("外部工具探测结果：")
    for name, path in [
        ("Gaussian", tools.gaussian),
        ("formchk", tools.formchk),
        ("cubegen", tools.cubegen),
        ("Multiwfn", tools.multiwfn),
    ]:
        print(f"  - {name}: {path if path else '未检测到'}")


def validate_examples() -> list[Path]:
    required = [
        EXAMPLES / "gaussian" / "water_opt_freq_nbo.gjf",
        EXAMPLES / "gaussian" / "ethylene_sp_pop.gjf",
        EXAMPLES / "gaussian" / "mcsome_fast_sp.gjf",
        EXAMPLES / "multiwfn" / "load_and_quit.inp",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("缺少示例文件：" + ", ".join(str(path) for path in missing))
    return required


def list_examples() -> None:
    validate_examples()
    print("可运行示例：")
    print("  1. Gaussian: water_opt_freq_nbo.gjf -> water_opt_freq_nbo.log/chk")
    print("  2. Gaussian: ethylene_sp_pop.gjf -> ethylene_sp_pop.log/chk")
    print("  3. Gaussian: mcsome_fast_sp.gjf -> mcsome_fast_sp.log/chk")
    print("  4. formchk: water_opt_freq_nbo.chk -> water_opt_freq_nbo.fchk")
    print("  5. cubegen: water_opt_freq_nbo.fchk -> water_density.cube / water_homo.cube")
    print("  6. Multiwfn: Multiwfn water_opt_freq_nbo.fchk < load_and_quit.inp")


def command_text(command: list[str]) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in command)


def run_command(command: list[str], cwd: Path, timeout: int, stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    print(f"[RUN] {command_text(command)}")
    return subprocess.run(
        command,
        cwd=cwd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def write_process_log(workdir: Path, name: str, result: subprocess.CompletedProcess[str]) -> None:
    (workdir / f"{name}.stdout.txt").write_text(result.stdout or "", encoding="utf-8")
    (workdir / f"{name}.stderr.txt").write_text(result.stderr or "", encoding="utf-8")


def require_tool(path: Path | None, name: str) -> Path:
    if path is None:
        raise RuntimeError(f"未检测到 {name}。请通过命令行参数或环境变量显式提供路径。")
    return path


def prepare_workdir(workdir: Path) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    for input_file in (EXAMPLES / "gaussian").glob("*.gjf"):
        shutil.copy2(input_file, workdir / input_file.name)
    shutil.copy2(EXAMPLES / "multiwfn" / "load_and_quit.inp", workdir / "multiwfn_load_and_quit.inp")


def run_gaussian(gaussian: Path, gjf_name: str, workdir: Path, timeout: int, style: str) -> Path:
    gjf = workdir / gjf_name
    log = workdir / f"{gjf.stem}.log"
    if style == "stdin":
        result = run_command([str(gaussian)], workdir, timeout, stdin_text=gjf.read_text(encoding="utf-8"))
        if not log.exists():
            log.write_text(result.stdout or "", encoding="utf-8")
    else:
        result = run_command([str(gaussian), gjf.name], workdir, timeout)
    write_process_log(workdir, f"gaussian_{gjf.stem}", result)
    if result.returncode != 0:
        raise RuntimeError(f"Gaussian 示例 {gjf_name} 失败，退出码 {result.returncode}。请查看 {workdir}")
    if not log.exists():
        possible_logs = sorted(workdir.glob(f"{gjf.stem}*.log"))
        if possible_logs:
            log = possible_logs[0]
    if not log.exists():
        raise RuntimeError(f"Gaussian 示例 {gjf_name} 未生成 log 文件。")
    text = log.read_text(encoding="utf-8", errors="replace")
    if "Normal termination of Gaussian" not in text:
        raise RuntimeError(f"Gaussian 示例 {gjf_name} 未检测到 Normal termination。")
    print(f"[PASS] Gaussian 正常终止：{log.name}")
    return log


def run_formchk(formchk: Path, chk_name: str, fchk_name: str, workdir: Path, timeout: int) -> Path:
    chk = workdir / chk_name
    if not chk.exists():
        raise RuntimeError(f"缺少 {chk_name}，无法运行 formchk。")
    result = run_command([str(formchk), chk.name, fchk_name], workdir, timeout)
    write_process_log(workdir, "formchk_water", result)
    if result.returncode != 0:
        raise RuntimeError(f"formchk 失败，退出码 {result.returncode}。")
    fchk = workdir / fchk_name
    if not fchk.exists() or fchk.stat().st_size == 0:
        raise RuntimeError("formchk 未生成有效 fchk 文件。")
    print(f"[PASS] formchk 输出：{fchk.name}")
    return fchk


def run_cubegen(cubegen: Path, fchk_name: str, workdir: Path, timeout: int) -> list[Path]:
    outputs = []
    for kind, output in [
        ("Density=SCF", "water_density.cube"),
        ("MO=HOMO", "water_homo.cube"),
    ]:
        result = run_command([str(cubegen), "0", kind, fchk_name, output, "0", "h"], workdir, timeout)
        write_process_log(workdir, f"cubegen_{output}", result)
        if result.returncode != 0:
            raise RuntimeError(f"cubegen {kind} 失败，退出码 {result.returncode}。")
        cube = workdir / output
        if not cube.exists() or cube.stat().st_size == 0:
            raise RuntimeError(f"cubegen 未生成有效文件：{output}")
        outputs.append(cube)
        print(f"[PASS] cubegen 输出：{cube.name}")
    return outputs


def run_multiwfn(multiwfn: Path, fchk_name: str, workdir: Path, timeout: int) -> None:
    inp = workdir / "multiwfn_load_and_quit.inp"
    result = run_command([str(multiwfn), fchk_name], workdir, timeout, stdin_text=inp.read_text(encoding="utf-8"))
    write_process_log(workdir, "multiwfn_load_and_quit", result)
    if result.returncode != 0:
        raise RuntimeError(f"Multiwfn 批处理失败，退出码 {result.returncode}。")
    print("[PASS] Multiwfn 加载 fchk 并正常退出")


def write_report(workdir: Path, tools: ToolPaths, executed: bool, ok: bool, message: str) -> Path:
    report = workdir / "EXTERNAL_QC_RUN_REPORT.md"
    lines = [
        "# 外部量子化学工具示例运行报告",
        "",
        f"- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 系统：{platform.platform()}",
        f"- 工作目录：{workdir}",
        f"- 是否执行外部程序：{'是' if executed else '否'}",
        f"- 结果：{'PASS' if ok else 'FAIL'}",
        f"- 信息：{message}",
        "",
        "## 工具路径",
        f"- Gaussian：{tools.gaussian or '未检测到'}",
        f"- formchk：{tools.formchk or '未检测到'}",
        f"- cubegen：{tools.cubegen or '未检测到'}",
        f"- Multiwfn：{tools.multiwfn or '未检测到'}",
        "",
        "## 安全说明",
        "- runner 默认不执行外部程序。",
        "- 只有显式传入 --execute-external-tools 才会调用 Gaussian/formchk/cubegen/Multiwfn。",
        "- 示例输出仅用于链路烟测，不能作为真实研究结论。",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行或检查 Gaussian/cubegen/Multiwfn 受控示例。")
    parser.add_argument("--list", action="store_true", help="列出示例，不执行外部程序。")
    parser.add_argument("--check-only", action="store_true", help="只检查示例文件和工具路径，不执行外部程序。")
    parser.add_argument("--execute-external-tools", action="store_true", help="显式允许执行 Gaussian/formchk/cubegen/Multiwfn。")
    parser.add_argument("--gaussian", help="Gaussian 可执行文件路径，如 C:\\G16W\\g16.exe。")
    parser.add_argument("--formchk", help="formchk 可执行文件路径。")
    parser.add_argument("--cubegen", help="cubegen 可执行文件路径。")
    parser.add_argument("--multiwfn", help="Multiwfn 可执行文件路径。")
    parser.add_argument("--workdir", help="运行输出目录。")
    parser.add_argument("--timeout", type=int, default=1800, help="单个外部命令超时时间，秒。")
    parser.add_argument("--gaussian-style", choices=["direct", "stdin"], default="direct" if os.name == "nt" else "stdin")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tools = discover_tools(args)
    validate_examples()
    if args.list:
        list_examples()
        print_tools(tools)
        return 0

    workdir = Path(args.workdir).expanduser() if args.workdir else DEFAULT_RUN_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
    prepare_workdir(workdir)
    print_tools(tools)
    print(f"运行目录：{workdir}")

    if args.check_only or not args.execute_external_tools:
        message = "检查完成：示例文件已复制；未执行外部程序。"
        report = write_report(workdir, tools, executed=False, ok=True, message=message)
        print(f"[PASS] {message}")
        print(f"报告：{report}")
        if not args.execute_external_tools:
            print("提示：真实执行请添加 --execute-external-tools 并提供工具路径。")
        return 0

    try:
        gaussian = require_tool(tools.gaussian, "Gaussian")
        formchk = require_tool(tools.formchk, "formchk")
        cubegen = require_tool(tools.cubegen, "cubegen")
        multiwfn = require_tool(tools.multiwfn, "Multiwfn")

        run_gaussian(gaussian, "water_opt_freq_nbo.gjf", workdir, args.timeout, args.gaussian_style)
        run_gaussian(gaussian, "ethylene_sp_pop.gjf", workdir, args.timeout, args.gaussian_style)
        run_gaussian(gaussian, "mcsome_fast_sp.gjf", workdir, args.timeout, args.gaussian_style)
        run_formchk(formchk, "water_opt_freq_nbo.chk", "water_opt_freq_nbo.fchk", workdir, args.timeout)
        run_cubegen(cubegen, "water_opt_freq_nbo.fchk", workdir, args.timeout)
        run_multiwfn(multiwfn, "water_opt_freq_nbo.fchk", workdir, args.timeout)
    except Exception as exc:
        report = write_report(workdir, tools, executed=True, ok=False, message=str(exc))
        print(f"[FAIL] {exc}")
        print(f"报告：{report}")
        return 1

    report = write_report(workdir, tools, executed=True, ok=True, message="Gaussian、formchk、cubegen、Multiwfn 示例链全部运行成功。")
    print(f"[PASS] 外部量子化学工具示例链全部运行成功。")
    print(f"报告：{report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
