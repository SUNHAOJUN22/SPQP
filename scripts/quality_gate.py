from __future__ import annotations

import subprocess
import sys
import time


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


def safe_print(text: str) -> None:
    print(text.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


def run_command(command: str, name: str) -> bool:
    safe_print(f"--- [RUNNING] {name} ---")
    start = time.time()
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, encoding="utf-8", errors="ignore")
        safe_print(result.stdout[-1200:])
        safe_print(f"[PASS] {name} ({time.time() - start:.2f}s)")
        return True
    except subprocess.CalledProcessError as exc:
        safe_print(f"[FAIL] {name} ({time.time() - start:.2f}s)")
        safe_print((exc.stderr or exc.stdout or "")[-2000:])
        return False


def main() -> int:
    print("=" * 72)
    print("硅氧键催化量子研究平台 - 根工作目录质量门禁")
    print("=" * 72)
    stages = [
        ("后端单元测试", "npm run test:backend"),
        ("全功能 API 烟测", r"backend\.venv\Scripts\python.exe scripts\full_function_smoke.py"),
        ("Pro Max Ultra 自动化质量审计", r"backend\.venv\Scripts\python.exe scripts\ultra_quality_audit.py"),
        ("中文乱码活动文件审计", "npm run audit:mojibake"),
        ("前端 Vitest 单元测试", "npm --prefix frontend run test"),
        ("前端 TypeScript strict 检查", "npm --prefix frontend run typecheck"),
        ("前端 ESLint", "npm --prefix frontend run lint"),
        ("前端生产构建", "npm --prefix frontend run build"),
    ]
    failed: list[str] = []
    for name, command in stages:
        if not run_command(command, name):
            failed.append(name)
            break
    print("=" * 72)
    if failed:
        print("质量门禁失败：", ", ".join(failed))
        return 1
    print("质量门禁通过：当前根工作目录可启动、可构建、可测试。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
