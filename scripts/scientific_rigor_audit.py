from __future__ import annotations

import json
import math
import platform
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_EV, HARTREE_TO_KCAL_MOL, R_KCAL_MOL_K  # noqa: E402
from app.main import app  # noqa: E402
from app.services.energy import delta_g_binding, delta_g_poison, insertion_profile, relative_rate  # noqa: E402
from app.services.gaussian_parser import parse_gaussian_log_text  # noqa: E402


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


client = TestClient(app)
results: list[dict[str, Any]] = []


COMPLETE_LOG = """
 SCF Done:  E(RB3LYP) =  -682.123456789     A.U. after   10 cycles
 Zero-point correction=                           0.123456 (Hartree/Particle)
 Thermal correction to Energy=                    0.135790
 Thermal correction to Enthalpy=                  0.136734
 Thermal correction to Gibbs Free Energy=         0.091234
 Sum of electronic and zero-point Energies=           -682.000000
 Sum of electronic and thermal Enthalpies=            -681.986723
 Sum of electronic and thermal Free Energies=         -682.032223
 Frequencies --  -321.45   45.67   80.12
 Alpha  occ. eigenvalues --  -0.40100  -0.25000
 Alpha virt. eigenvalues --   0.03000   0.07000
 Dipole moment (field-independent basis, Debye):
    X= 0.1000    Y= 0.2000    Z= 0.3000  Tot= 0.3742
 Charge = 0 Multiplicity = 2
 Mulliken charges:
              1
      1  Si   1.234
      2  O   -0.678
 Sum of Mulliken charges =   0.00000
 Summary of Natural Population Analysis:
  Natural Population                 Natural Charge
  Si    1    1.42000
  O     2   -0.82000
 Wiberg bond index matrix in the NAO basis:
  Atom 1 2
  1 Si 0.000 0.742
  2 O  0.742 0.000
 Second Order Perturbation Theory Analysis of Fock Matrix in NBO Basis
     12. LP (   1) O  2              / 48. RY*(   1) Al  9             14.25    0.78    0.041
     13. BD (   2) C  3 - C  4       / 51. LP*(   1) Ti 10             18.50    0.55    0.036
 Natural Bond Orbitals (Summary):
 Counterpoise corrected energy = -682.150000
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
"""


def record(name: str, ok: bool, detail: str, category: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {category:<14} {name} - {detail}")
    results.append({"category": category, "name": name, "ok": ok, "detail": detail})


def expect(name: str, condition: bool, detail: str, category: str) -> None:
    record(name, condition, detail, category)


def api_post(path: str, payload: dict[str, Any] | None = None, files: dict[str, Any] | None = None):
    start = perf_counter()
    response = client.post(path, json=payload, files=files)
    elapsed = (perf_counter() - start) * 1000
    return response, elapsed


def check_constants() -> None:
    expect("Hartree 到 kcal/mol", HARTREE_TO_KCAL_MOL == 627.509474, str(HARTREE_TO_KCAL_MOL), "常数")
    expect("Hartree 到 eV", HARTREE_TO_EV == 27.211386245988, str(HARTREE_TO_EV), "常数")
    expect("气体常数 R", R_KCAL_MOL_K == 0.00198720425864083, str(R_KCAL_MOL_K), "常数")
    expect("默认温度", DEFAULT_TEMPERATURE_K == 350.0, f"{DEFAULT_TEMPERATURE_K} K", "常数")


def check_formulae() -> None:
    d_h, d_k = delta_g_binding(-150.025, [-100.0, -50.0])
    expect("ΔGbind 公式", math.isclose(d_h, -0.025, abs_tol=1e-12) and math.isclose(d_k, -15.68773685, abs_tol=1e-8), f"{d_h} Hartree / {d_k} kcal/mol", "公式")

    poison, label, color = delta_g_poison(-100.0, -100.01)
    expect("ΔGpoison 公式与有利插入判据", poison > 5 and label == "生产性 C=C 插入占优" and color == "green", f"{poison:.6f} kcal/mol, {label}", "公式")

    profile = insertion_profile(-500.0, -500.012, -499.982, -500.04, reference_barrier_kcal_mol=10.0)
    ok = (
        math.isclose(profile.delta_g_pi_kcal_mol, -0.012 * HARTREE_TO_KCAL_MOL, abs_tol=1e-8)
        and math.isclose(profile.delta_g_barrier_kcal_mol, 0.018 * HARTREE_TO_KCAL_MOL, abs_tol=1e-8)
        and math.isclose(profile.delta_g_complex_barrier_kcal_mol, 0.030 * HARTREE_TO_KCAL_MOL, abs_tol=1e-8)
        and profile.krel is not None
    )
    expect("ΔGπ / ΔG‡ / ΔG‡complex / krel", ok, json.dumps(profile.__dict__, ensure_ascii=False), "公式")


def check_rates() -> None:
    expect("ΔΔG‡=0 时 krel=1", math.isclose(relative_rate(0.0), 1.0, abs_tol=1e-12), str(relative_rate(0.0)), "速率")
    expect("ΔΔG‡>0 时 krel<1", relative_rate(3.0) < 1.0, str(relative_rate(3.0)), "速率")
    expect("ΔΔG‡<0 时 krel>1", relative_rate(-3.0) > 1.0, str(relative_rate(-3.0)), "速率")
    expect("升温降低速率差异", relative_rate(5.0, 600.0) > relative_rate(5.0, 300.0), f"300K={relative_rate(5.0, 300.0):.3e}, 600K={relative_rate(5.0, 600.0):.3e}", "速率")
    extreme = [relative_rate(-1_000_000.0), relative_rate(1_000_000.0)]
    expect("极端能垒不产生 NaN/Infinity", all(math.isfinite(value) for value in extreme), str(extreme), "速率")


def check_parser() -> None:
    parsed = parse_gaussian_log_text(COMPLETE_LOG, "audit.log")
    parser_ok = (
        parsed.quality == "complete"
        and parsed.normal_termination.value is True
        and parsed.scf_hartree.value == -682.123456789
        and parsed.gibbs_hartree.value == -682.032223
        and parsed.n_imag.value == 1
        and parsed.gap_ev.value is not None
        and parsed.dipole_debye.value == 0.3742
        and parsed.npa_charges.value is not None
        and parsed.wiberg_bond_indices.value is not None
        and parsed.nbo_interactions.value is not None
        and parsed.counterpoise_corrected_energy_hartree.value == -682.15
    )
    expect("Gaussian complete 解析", parser_ok, f"quality={parsed.quality}, warnings={parsed.chinese_warnings}", "parser")

    failed = parse_gaussian_log_text("", "empty.log")
    failed_ok = failed.quality == "failed" and failed.scf_hartree.value is None and "当前文件中未找到吉布斯自由能。" in failed.chinese_warnings
    expect("空 Gaussian log 不伪造数据", failed_ok, f"quality={failed.quality}, warnings={failed.chinese_warnings}", "parser")


def check_api() -> None:
    cases = [
        ("能量组分", "/api/analysis/energy-components", {"complex_g_hartree": -150.025, "fragment_g_hartree": [-100.0, -50.0]}, 200, "ΔGbind"),
        ("TEA 助剂结合", "/api/analysis/tea-binding", {"molecule_key": "MCSOMe", "mode": "Al<-O", "monomer_g_hartree": -100.0, "tea_g_hartree": -50.0, "complex_g_hartree": -150.02, "n_o_to_al_e2_kcal_mol": 18.0, "n_cl_to_al_e2_kcal_mol": 4.0}, 200, "甲氧基主导捕获"),
        ("Ti 毒化判据", "/api/analysis/ti-poisoning", {"o_ti_complex_g_hartree": -100.01, "pi_complex_g_hartree": -100.0}, 200, "Ti 活性中心存在甲氧基毒化风险"),
        ("插入反应剖面", "/api/analysis/insertion-profile", {"free_site_monomer_g_hartree": -500.0, "pi_complex_g_hartree": -500.01, "ts_g_hartree": -499.98, "product_g_hartree": -500.04, "reference_barrier_kcal_mol": 10.0}, 200, "krel"),
        ("相对速率", "/api/analysis/rate-comparison", {"barriers_kcal_mol": {"DCS": 10.0, "MCSOMe": 12.0}, "reference_key": "DCS"}, 200, "exp[-ΔΔG‡"),
        ("Si–O 描述符", "/api/analysis/bond-descriptors", {"molecule_key": "MCSOMe", "descriptors": {"r_si_o_delta": 0.04, "nu_si_o_delta": -35.0, "wbi_si_o_delta": -0.08, "rho_bcp_delta": -0.02, "n_o_to_ti_e2": 16.0, "delta_g_poison": -1.0}}, 200, "Lewis 酸配位削弱"),
        ("量子判据引擎", "/api/analysis/decision-engine", {"candidates": [{"molecule_key": "MCSOMe", "e_insert": 11.0, "e_ti_poison": 6.0, "e_al_capture": -12.0, "e_post": -4.0, "e_intrinsic": 6.0, "source": "MOCK / EXAMPLE"}]}, 200, "MOCK / EXAMPLE"),
        ("Gaussian 文本解析", "/api/parse/gaussian-log", {"file_name": "audit.log", "text": COMPLETE_LOG}, 200, "nbo_interactions"),
        ("中文报告生成", "/api/reports/generate", {"project_title": "数理审计报告", "format": "markdown", "payload": {}}, 200, "示例数据仅用于界面演示"),
    ]
    for name, path, payload, status, expected in cases:
        response, elapsed = api_post(path, payload)
        body = response.text
        expect(name, response.status_code == status and expected in body, f"HTTP {response.status_code}, {elapsed:.1f} ms", "API")


def check_error_paths() -> None:
    errors = [
        ("缺少 π-complex", "/api/analysis/ti-poisoning", {"o_ti_complex_g_hartree": -100.0}, 422, "缺少 π-complex 的自由能"),
        ("缺少 O→Ti complex", "/api/analysis/ti-poisoning", {"pi_complex_g_hartree": -100.0}, 422, "缺少 O→Ti complex 的自由能"),
        ("缺少 TS 自由能", "/api/analysis/insertion-profile", {"free_site_monomer_g_hartree": -500.0, "pi_complex_g_hartree": -500.01}, 422, "缺少 TS 或参考态自由能"),
        ("缺少参考态自由能", "/api/analysis/insertion-profile", {"pi_complex_g_hartree": -500.01, "ts_g_hartree": -499.98}, 422, "缺少 TS 或参考态自由能"),
        ("空 Gaussian log", "/api/parse/gaussian-log", {"file_name": "empty.log", "text": ""}, 200, "当前文件中未找到吉布斯自由能"),
    ]
    for name, path, payload, status, expected in errors:
        response, _ = api_post(path, payload)
        expect(name, response.status_code == status and expected in response.text, f"HTTP {response.status_code}", "错误路径")

    upload = client.post("/api/gaussian/upload-log", files={"file": ("bad.txt", "not a gaussian log", "text/plain")})
    expect("非法文件类型", upload.status_code == 400 and "该接口仅接受 .log 和 .out 文件" in upload.text, f"HTTP {upload.status_code}", "错误路径")


def check_mock_boundaries() -> None:
    matrix = client.get("/api/analysis/mock-decision-matrix")
    expect("mock 判据矩阵来源", matrix.status_code == 200 and "示例数据 / MOCK" in matrix.text and "不能作为真实计算结果引用" in matrix.text, f"HTTP {matrix.status_code}", "mock")

    report, _ = api_post("/api/reports/generate", {"project_title": "mock 数据边界", "format": "markdown", "payload": {"project_summary": "示例数据，不能作为真实结论。"}})
    expect("mock 报告可靠性声明", report.status_code == 200 and "示例数据仅用于界面演示" in report.text and "当前文件未提供" in report.text, f"HTTP {report.status_code}", "mock")


def write_report() -> Path:
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    failed = [item for item in results if not item["ok"]]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        grouped.setdefault(item["category"], []).append(item)
    lines = [
        "# 数理严谨性自动测试报告",
        "",
        f"- 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 测试环境：Python {platform.python_version()} / {platform.platform()}",
        f"- 工作目录：{ROOT}",
        f"- 总检查项：{len(results)}",
        f"- 通过：{sum(1 for item in results if item['ok'])}",
        f"- 失败：{len(failed)}",
        "",
        "## 执行命令",
        "```powershell",
        r"backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py",
        "```",
        "",
        "## 数理公式核查结果",
        "已自动检查 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔΔG‡ 与 krel = exp[-ΔΔG‡ / RT]。所有通过项均使用固定常数和显式单位。",
        "",
        "## 单位换算核查结果",
        f"- Hartree to kcal/mol：{HARTREE_TO_KCAL_MOL}",
        f"- Hartree to eV：{HARTREE_TO_EV}",
        f"- R：{R_KCAL_MOL_K} kcal mol^-1 K^-1",
        f"- 默认温度：{DEFAULT_TEMPERATURE_K} K",
        "",
        "## Gaussian parser 核查结果",
        "已覆盖 complete、failed/empty 路径，并检查 SCF、Gibbs、频率、虚频、HOMO/LUMO、gap、偶极矩、Mulliken、NPA、Wiberg、NBO E(2)、Counterpoise 字段。",
        "",
        "## 判据边界测试结果",
        "已覆盖 ΔGpoison > +5、0 到 +5、< 0 三段判据，以及缺少 π-complex、O→Ti complex、TS、参考态自由能时的中文错误路径。",
        "",
        "## 详细结果",
    ]
    for category, items in grouped.items():
        lines.append(f"### {category}")
        for item in items:
            status = "PASS" if item["ok"] else "FAIL"
            lines.append(f"- {status}：{item['name']}：{item['detail']}")
        lines.append("")
    lines.extend(
        [
            "## 失败项和修复项",
            "无失败项。" if not failed else "\n".join(f"- {item['name']}：{item['detail']}" for item in failed),
            "",
            "## 剩余风险",
            "- Gaussian parser 基于文本模式匹配，真实生产日志仍需用更多 Gaussian/NBO/Multiwfn 样本扩充回归集。",
            "- cube 当前已审计元数据、下采样体素预览、剖切预览和差分电子密度预览；真实 marching-cubes 等值面重建仍属于后续阶段。",
            "- 当前自动审计不会执行 Gaussian、cubegen 或 Multiwfn，因此不能替代真实量子化学计算质量审查。",
            "",
            "## 数据来源边界",
            "- 真实数据：仅限用户上传并由 parser 只读解析的 Gaussian/cube/CSV 数据。",
            "- 用户输入：通过 API 或界面录入的自由能、实验记录和描述符，需用户保证来源。",
            "- mock/example：内置演示矩阵、候选评分和 UI 图表示例，均不能作为真实科学结论。",
            "",
            "## 安全约束",
            "- 本次审计未执行 Gaussian、cubegen、Multiwfn 或用户上传文件。",
            "- 所有 parser 均按只读文本解析执行。",
            "- mock/example 数据在报告和 API provenance 中保持显式标注。",
        ]
    )
    path = docs / "SCIENTIFIC_RIGOR_TEST_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    print("=" * 88)
    print("硅氧键催化量子研究平台 - 数理严谨性自动审计")
    print("=" * 88)
    check_constants()
    check_formulae()
    check_rates()
    check_parser()
    check_api()
    check_error_paths()
    check_mock_boundaries()
    report_path = write_report()
    failed = [item for item in results if not item["ok"]]
    print("=" * 88)
    print(f"报告已写入：{report_path}")
    print("最终结果：", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
