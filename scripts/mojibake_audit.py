from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "MOJIBAKE_CLEANUP_REPORT.md"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".json",
    ".md",
    ".txt",
    ".css",
    ".html",
    ".yml",
    ".yaml",
    ".toml",
    ".csv",
    ".gjf",
    ".com",
}

EXCLUDED_PARTS = {
    ".git",
    ".next",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "tsconfig.tsbuildinfo",
}

ARCHIVE_PART_PREFIXES = ("integrated/origin-", "docs/merged-from-si-o")
GENERATED_REL_PATHS = {
    "docs/MOJIBAKE_CLEANUP_REPORT.md",
    "scripts/mojibake_audit.py",
}

MOJIBAKE_RE = re.compile(
    r"("
    r"Ã|Â|â|å|ç|æ|ä|é|è|î|ï|ð|þ|"
    r"Î|Ï|Ð|"
    r"鏂|璁|绀|姝|寮|鍙|鎻|鍚|鐢|鐨|涓|鍏|"
    r"鈥|鈫|螖|蟺|脜|馃|"
    r"�"
    r")"
)


@dataclass
class Finding:
    path: Path
    line_no: int
    snippet: str
    archived: bool


def markdown_safe_snippet(text: str) -> str:
    """Keep generated Markdown textual even when archive files contain NUL bytes."""
    safe = text.replace("\\", "\\\\").replace("`", "\\`")
    safe = safe.replace("\x00", "\\0")
    return "".join(
        char if char in ("\t",) or ord(char) >= 32 else f"\\x{ord(char):02x}"
        for char in safe
    )


def is_text_candidate(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in GENERATED_REL_PATHS:
        return False
    if path.name in EXCLUDED_PARTS:
        return False
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def is_archived(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel.startswith(ARCHIVE_PART_PREFIXES)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and is_text_candidate(path):
            files.append(path)
    return sorted(files)


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    archived = is_archived(path)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for index, line in enumerate(text.splitlines(), start=1):
        if MOJIBAKE_RE.search(line):
            snippet = line.strip()
            if len(snippet) > 180:
                snippet = snippet[:177] + "..."
            snippet = markdown_safe_snippet(snippet)
            findings.append(Finding(path=path, line_no=index, snippet=snippet, archived=archived))
    return findings


def write_report(findings: list[Finding], scanned_count: int) -> None:
    active = [item for item in findings if not item.archived]
    archived = [item for item in findings if item.archived]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 中文乱码清理审计报告",
        "",
        f"- 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 扫描根目录：`{ROOT}`",
        f"- 扫描文本文件数：{scanned_count}",
        f"- 活动文件疑似乱码行数：{len(active)}",
        f"- 归档/来源目录疑似乱码行数：{len(archived)}",
        "",
        "## 判定规则",
        "",
        "本审计查找常见 UTF-8/GBK 误解码痕迹，例如 `Ã`、`Â`、`â`、`Î`、`Ï`、`鏂`、`璁`、`鐢`、`鈥` 等。合法科研符号如 Δ、β、π、ρ、∇、Å、→、← 不计为乱码。",
        "",
        "## 活动文件待清理项",
        "",
    ]
    if active:
        for item in active:
            rel = item.path.relative_to(ROOT).as_posix()
            lines.append(f"- `{rel}:{item.line_no}`：`{item.snippet}`")
    else:
        lines.append("未发现活动文件中的疑似乱码。")
    lines.extend(["", "## 归档/来源目录记录", ""])
    if archived:
        for item in archived[:300]:
            rel = item.path.relative_to(ROOT).as_posix()
            lines.append(f"- `{rel}:{item.line_no}`：`{item.snippet}`")
        if len(archived) > 300:
            lines.append(f"- 归档目录剩余 {len(archived) - 300} 行已省略。")
    else:
        lines.append("归档/来源目录未发现疑似乱码。")
    lines.extend(
        [
            "",
            "## 清理边界",
            "",
            "- 活动源码、测试、脚本、README、CHANGELOG 和当前 docs 应优先修复。",
            "- `integrated/origin-*` 与 `docs/merged-from-si-o` 视为来源归档，默认只记录，不参与生产构建修复。",
            "- 若乱码出现在测试断言中，必须同步修复后端/API 返回文本，不能只改测试。",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan active project files for Chinese mojibake.")
    parser.add_argument("--fail-on-active", action="store_true", help="Return exit code 1 when active findings exist.")
    args = parser.parse_args()
    files = iter_files()
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path))
    write_report(findings, len(files))
    active_count = sum(1 for item in findings if not item.archived)
    archived_count = len(findings) - active_count
    print(f"扫描完成：文本文件 {len(files)} 个，活动乱码 {active_count} 行，归档记录 {archived_count} 行。")
    print(f"报告：{REPORT_PATH}")
    if args.fail_on_active and active_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
