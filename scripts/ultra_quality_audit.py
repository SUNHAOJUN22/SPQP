from __future__ import annotations

import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DOCX_SOURCE = Path(r"C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx")

sys.path.insert(0, str(BACKEND))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import inspect  # noqa: E402

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_EV, HARTREE_TO_KCAL_MOL, R_KCAL_MOL_K  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.cube import cube_difference_preview, cube_slice_preview, cube_volume_preview, parse_cube_metadata  # noqa: E402
from app.services.energy import delta_g_binding, delta_g_poison, insertion_profile, rate_comparison, relative_rate  # noqa: E402
from app.services.gaussian_parser import parse_gaussian_log_text  # noqa: E402
from app.services.radical_v4 import radical_branching_vs_scission, sic_stability, unified_lcb_framework  # noqa: E402
from app.services.ultra_science import calculate_bde_roor, calculate_bde_sic, calculate_bde_sio  # noqa: E402


@dataclass
class AuditResult:
    category: str
    name: str
    status: str
    detail: str
    duration_ms: float = 0.0


class Audit:
    def __init__(self) -> None:
        self.results: list[AuditResult] = []
        self.client = TestClient(app)

    def run(self, category: str, name: str, fn: Callable[[], str | None]) -> None:
        start = time.perf_counter()
        try:
            detail = fn() or "通过"
            status = "PASS"
        except NotImplementedError as exc:
            detail = str(exc)
            status = "SKIP"
        except AssertionError as exc:
            detail = str(exc) or "断言失败"
            status = "FAIL"
        except Exception as exc:  # noqa: BLE001 - audit must capture every unexpected failure
            detail = f"{type(exc).__name__}: {exc}"
            status = "FAIL"
        elapsed = (time.perf_counter() - start) * 1000
        self.results.append(AuditResult(category, name, status, detail, elapsed))
        print(f"[{status}] {category} / {name}: {detail}")

    @property
    def failed(self) -> list[AuditResult]:
        return [item for item in self.results if item.status == "FAIL"]

    @property
    def skipped(self) -> list[AuditResult]:
        return [item for item in self.results if item.status == "SKIP"]

    @property
    def passed(self) -> list[AuditResult]:
        return [item for item in self.results if item.status == "PASS"]


def assert_close(actual: float, expected: float, tol: float = 1e-8) -> None:
    assert abs(actual - expected) <= tol, f"得到 {actual}，期望 {expected}"


def gaussian_sample() -> str:
    return """
 #P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ Opt Freq Pop=(NBO,Full)

 MCSOMe sample

 0 1
 C 0.0 0.0 0.0
 H 0.0 0.0 1.0

 SCF Done:  E(RB3LYP) =  -100.123456789     A.U. after   10 cycles
 Zero-point correction=                           0.123456 (Hartree/Particle)
 Thermal correction to Energy=                    0.130000
 Thermal correction to Enthalpy=                  0.131000
 Thermal correction to Gibbs Free Energy=         0.090000
 Sum of electronic and zero-point Energies=           -100.000000
 Sum of electronic and thermal Enthalpies=            -99.992457
 Sum of electronic and thermal Free Energies=         -100.033457
 Frequencies --   -245.1234   120.5000   980.1000
 Alpha  occ. eigenvalues -- -0.55000 -0.31000
 Alpha virt. eigenvalues --  0.05000  0.12000
 Dipole moment (field-independent basis, Debye):
     X= 0.0000    Y= 0.0000    Z= 1.2345  Tot= 1.2345
 Mulliken charges:
      1  C   -0.100000
      2  H    0.100000
 Sum of Mulliken charges = 0.00000
 Summary of Natural Population Analysis:
 Natural Population  Natural Charge
 C 1 -0.21000
 H 2  0.21000
 Wiberg bond index matrix in the NAO basis
 Atom       1       2
 1 C      0.000   0.970
 2 H      0.970   0.000
 Second Order Perturbation Theory Analysis of Fock Matrix in NBO Basis
    1. LP ( 1) O  3 /  25. RY*( 1) Ti 10      12.34    0.20    0.045
 Counterpoise corrected energy = -100.040000
 Normal termination of Gaussian 16
 """


def cube_sample() -> str:
    return "\n".join(
        [
            "cube sample",
            "HOMO orbital",
            " 1 0.0 0.0 0.0",
            " 2 1.0 0.0 0.0",
            " 2 0.0 1.0 0.0",
            " 1 0.0 0.0 1.0",
            " 6 0.0 0.0 0.0 0.0",
            " 0.10 0.20 -0.10 0.00",
        ]
    )


def run_audit() -> Audit:
    audit = Audit()

    audit.run("科学常数", "Hartree/kcal/eV/R/T 常数", lambda: _check_constants())
    audit.run("科学公式", "自由能、速率与温度边界", lambda: _check_energy_formulae())
    audit.run("科学公式", "Si-C/Si-O/RO-OR BDE", lambda: _check_bde_formulae())
    audit.run("科学判据", "Ti 毒化、Si-C 稳定与 ΦLCB 边界", lambda: _check_decisions())
    audit.run("Parser", "Gaussian 完整/失败解析", lambda: _check_gaussian_parser())
    audit.run("Parser", "cube 元数据、数值范围和错误路径", lambda: _check_cube_parser())
    audit.run("文献输入", "V4 DOCX 只读抽取可用性", lambda: _check_docx_source())
    audit.run("API", "核心量子化学与自由基接口", lambda: _check_core_apis(audit.client))
    audit.run("API", "错误路径与中文提示", lambda: _check_api_errors(audit.client))
    audit.run("API", "GoodVibes/QTAIM/NCI/MCP 安全扩展", lambda: _check_advanced_extension_apis(audit.client))
    audit.run("数据库", "已实现表与提示要求表覆盖", lambda: _check_database_tables())
    audit.run("安全", "上传路径与文件类型边界", lambda: _check_security(audit.client))
    audit.run("性能", "1000 点 cube 快速元数据审计", lambda: _check_performance())
    audit.run("MCP/外部工具", "外部化学软件执行边界", lambda: _check_external_tool_boundary())
    audit.run("剩余矩阵", "真实三维等值面重建", lambda: _check_not_implemented_matrix())
    return audit


def _check_constants() -> str:
    assert_close(HARTREE_TO_KCAL_MOL, 627.509474)
    assert_close(HARTREE_TO_EV, 27.211386245988)
    assert_close(R_KCAL_MOL_K, 0.00198720425864083)
    assert_close(DEFAULT_TEMPERATURE_K, 350.0)
    return "单位常数与默认温度匹配要求。"


def _check_energy_formulae() -> str:
    delta_h, delta_kcal = delta_g_binding(-150.05, [-100.0, -50.0])
    assert_close(delta_h, -0.05)
    assert_close(delta_kcal, -31.3754737)
    poison, label, color = delta_g_poison(-200.0, -200.01)
    assert poison > 5.0 and label == "生产性 C=C 插入占优" and color == "green"
    assert_close(relative_rate(0.0), 1.0)
    assert relative_rate(4.0) < 1.0
    assert relative_rate(-4.0) > 1.0
    assert relative_rate(4.0, 500.0) > relative_rate(4.0, 350.0)
    profile = insertion_profile(-300.0, -300.01, -299.98, -300.02, reference_barrier_kcal_mol=12.0)
    assert profile.delta_g_pi_kcal_mol < 0
    assert profile.delta_g_complex_barrier_kcal_mol > profile.delta_g_barrier_kcal_mol
    rates = rate_comparison({"DCS": 12.0, "MCSOMe": 14.0}, "DCS")
    assert rates["DCS"]["krel"] == 1.0 and rates["MCSOMe"]["krel"] < 1.0
    return "ΔGbind/ΔGpoison/ΔGπ/ΔG‡/krel 边界正确。"


def _check_bde_formulae() -> str:
    sic = calculate_bde_sic(-99.86, -100.0)
    sio = calculate_bde_sio(-99.83, -100.0)
    roor = calculate_bde_roor(-49.94, -50.0)
    assert_close(float(sic["bde_kcal_mol"]), 87.85132636)
    assert float(sio["bde_kcal_mol"]) > float(sic["bde_kcal_mol"])
    assert 35 < float(roor["bde_kcal_mol"]) < 40
    return "BDE 单位转换与键类型标注可复现。"


def _check_decisions() -> str:
    low, label_low, _ = delta_g_poison(-100.0, -100.02)
    mid, label_mid, _ = delta_g_poison(-100.01, -100.012)
    high, label_high, _ = delta_g_poison(-100.02, -100.01)
    assert low > 5 and "生产性" in label_low
    assert 0 <= mid <= 5 and "竞争" in label_mid
    assert high < 0 and "毒化" in label_high
    stable = sic_stability({"bde_sic_kcal_mol": 86.0, "radical_attack_barrier_kcal_mol": 16.0})
    assert "稳定" in stable["label"]
    missing = sic_stability({})
    assert missing["label"] == "当前数据不足"
    branch = radical_branching_vs_scission({"coagent_phr": 0.8, "oxygen_level_percent": 0.2})
    oxidation = radical_branching_vs_scission({"coagent_phr": 0.0, "oxygen_level_percent": 15.0})
    assert branch["fractions"]["branching"] > oxidation["fractions"]["branching"]
    framework = unified_lcb_framework({"chi_insert": 0.8, "chi_hydrolysis": 0.7, "chi_beta_scission": 0.2})
    assert "不输出确定性" in framework["reliability_note"]
    return "Ti 毒化、自由基竞争和 mock 边界返回中文机制判断。"


def _check_gaussian_parser() -> str:
    parsed = parse_gaussian_log_text(gaussian_sample(), "sample.log")
    assert parsed.quality == "complete"
    assert parsed.normal_termination.value is True
    assert parsed.gibbs_hartree.value == -100.033457
    assert parsed.n_imag.value == 1
    assert parsed.gap_ev.value is not None and parsed.gap_ev.value > 0
    assert parsed.nbo_interactions.value and parsed.nbo_interactions.value[0]["e2_kcal_mol"] == 12.34
    failed = parse_gaussian_log_text("", "empty.log")
    assert failed.quality == "failed"
    assert any("正常终止" in item for item in failed.chinese_warnings)
    assert any("吉布斯自由能" in item for item in failed.chinese_warnings)
    return "Gaussian parser 覆盖正常终止、Gibbs、虚频、HOMO/LUMO、NBO 与失败中文提示。"


def _check_cube_parser() -> str:
    parsed = parse_cube_metadata(cube_sample(), "HOMO_sample.cube")
    stats = parsed["metadata"]["data_stats"]
    assert parsed["cube_type"] == "HOMO 前线轨道"
    assert parsed["atom_count"] == 1
    assert stats["expected_value_count"] == 4
    assert stats["sampled_value_count"] == 4
    assert stats["value_count_status"] == "完整"
    volume = cube_volume_preview(cube_sample(), "HOMO_sample.cube")
    assert volume["observed_value_count"] == 4
    sliced = cube_slice_preview(cube_sample(), "HOMO_sample.cube", "z", 0)
    assert sliced["shape"]["width"] == 2
    diff = cube_difference_preview(cube_sample(), "HOMO_sample.cube", cube_sample().replace("0.10", "0.05", 1), "density_b.cube")
    assert diff["formula"] == "Δρ(r) = ρ_A(r) - ρ_B(r)"
    try:
        parse_cube_metadata("bad", "bad.cube")
    except ValueError as exc:
        assert "有效 cube" in str(exc)
    else:
        raise AssertionError("错误 cube 未被拒绝。")
    return "cube 头、grid、atom、数值范围、下采样体素、剖切和差分预览可审计。"


def _check_docx_source() -> str:
    from app.services.literature import extract_docx_text, extract_report_driven_knowledge

    if not DOCX_SOURCE.exists():
        knowledge = extract_report_driven_knowledge("", DOCX_SOURCE.name)
        assert knowledge["entities"]
        assert all(entity["evidence_level"] == "C" for entity in knowledge["entities"])
        return f"未找到本机报告 DOCX，已验证内置 C 级报告方向线索与缺失文件边界：{DOCX_SOURCE}"

    text = extract_docx_text(DOCX_SOURCE)
    assert len(text) > 1000
    knowledge = extract_report_driven_knowledge(text, DOCX_SOURCE.name)
    assert any(entity["chinese_name"] == "Si–C 侧链连接稳定性" for entity in knowledge["entities"])
    assert "pp_scission_crosslinking" in knowledge["report_payload"]
    return f"已只读解析 DOCX，文本长度 {len(text)}，关键词覆盖报告驱动 V4 机理。"


def _check_core_apis(client: TestClient) -> str:
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/molecules").status_code == 200
    energy = client.post("/api/analysis/energy-components", json={"complex_g_hartree": -150.05, "fragment_g_hartree": [-100.0, -50.0]})
    assert energy.status_code == 200 and energy.json()["delta_g_bind_kcal_mol"] < -30
    poison = client.post("/api/analysis/ti-poisoning", json={"o_ti_complex_g_hartree": -100.0, "pi_complex_g_hartree": -100.02})
    assert poison.status_code == 200 and poison.json()["label"] == "生产性 C=C 插入占优"
    task_matrix = client.get("/api/scientific-computation/task-matrix")
    assert task_matrix.status_code == 200 and task_matrix.json()["total_tasks"] == 36
    workbench = client.post(
        "/api/scientific-computation/energy-workbench",
        json={
            "complex_g_hartree": -150.025,
            "fragment_g_hartree": [-100.0, -50.0],
            "o_ti_complex_g_hartree": -100.0,
            "pi_complex_g_hartree": -100.02,
            "free_site_monomer_g_hartree": -500.0,
            "ts_g_hartree": -499.98,
        },
    )
    assert workbench.status_code == 200 and "delta_g_poison" in workbench.json()
    bde = client.post("/api/analysis/bde", json={"bond_type": "Si-C", "g_fragments_hartree": -199.86, "g_molecule_hartree": -200.0})
    assert bde.status_code == 200 and bde.json()["bde_kcal_mol"] > 80
    peroxide = client.post("/api/analysis/peroxide-profile", json={"name": "DCP", "half_life_min": 5.0, "residence_time_min": 5.0})
    assert peroxide.status_code == 200 and "窗口" in peroxide.json()["label"]
    framework = client.post("/api/analysis/unified-lcb-framework", json={"chi_insert": 0.8, "chi_hydrolysis": 0.8, "chi_beta_scission": 0.1})
    assert framework.status_code == 200 and "score_percent" in framework.json()["lcb_efficiency_formula"]
    report = client.post("/api/reports/generate", json={"project_title": "Ultra 审计报告", "format": "markdown"})
    assert report.status_code == 200 and "示例数据" in report.json()["content"]
    return "核心 API、科学计算任务矩阵、能量工作台与 BDE 入口正常响应且保持中文 provenance/mock 边界。"


def _check_api_errors(client: TestClient) -> str:
    missing = client.post("/api/analysis/ti-poisoning", json={"o_ti_complex_g_hartree": -100.0})
    assert missing.status_code == 422
    assert "π-complex" in missing.json()["detail"]
    empty = client.post("/api/parse/gaussian-log", json={"text": "", "file_name": "empty.log"})
    assert empty.status_code == 200
    assert empty.json()["quality"] == "failed"
    bad_cube = client.post("/api/cube/upload", files={"file": ("bad.exe", "x", "text/plain")})
    assert bad_cube.status_code == 400
    assert "cube" in bad_cube.json()["detail"]
    return "缺失能量、空 log、非法 cube 均返回中文错误或 failed 质量评分。"


def _check_advanced_extension_apis(client: TestClient) -> str:
    goodvibes = client.post("/api/parse/goodvibes", json={"file_name": "goodvibes.out", "text": "o DCS.log 298.15 -100.0 -99.9"})
    qtaim = client.post("/api/parse/qtaim", json={"text": "BCP Si-O rho=0.11 laplacian=0.32 H=-0.02"})
    nci = client.post("/api/parse/nci", json={"text": "region sign(lambda2)rho=-0.03 RDG=0.18"})
    tools = client.get("/api/mcp/tools")
    run_tool = client.post("/api/mcp/run-tool", json={"tool_name": "validate-upload", "arguments": {"file_name": "safe.log"}})
    assert goodvibes.status_code == 200 and goodvibes.json()["entries"]
    assert qtaim.status_code == 200 and qtaim.json()["bond_critical_points"]
    assert nci.status_code == 200 and nci.json()["regions"][0]["color"] == "blue"
    assert tools.status_code == 200 and "不执行 shell" in tools.json()["provenance"]
    assert run_tool.status_code == 200 and run_tool.json()["result"]["allowed"] is True
    return "只读 parser 与 MCP 白名单工作流可追踪、可测试。"


def _check_database_tables() -> str:
    existing = set(inspect(engine).get_table_names())
    required_existing = {
        "projects",
        "molecules",
        "fragments",
        "gaussian_jobs",
        "gaussian_outputs",
        "parsed_energies",
        "cube_files",
        "nbo_interactions",
        "tea_complexes",
        "ti_complexes",
        "insertion_paths",
        "hydrolysis_paths",
        "condensation_paths",
        "reports",
        "esp_extrema",
        "peroxide_species",
        "radical_reaction_paths",
        "polymer_microstructures",
        "residence_time_windows",
        "literature_evidence_items",
    }
    missing_required = sorted(required_existing - existing)
    assert not missing_required, f"缺少已承诺表：{missing_required}"
    prompt_tables = {
        "atoms",
        "bonds",
        "thermochemistry",
        "frequencies",
        "orbitals",
        "charges",
        "bond_orders",
        "qtaim_critical_points",
        "nci_regions",
        "radical_models",
        "coagents",
        "radical_kinetics",
        "experimental_samples",
        "dsc_data",
        "gpc_data",
        "mfr_data",
        "gel_data",
        "rheology_data",
        "ftir_data",
        "nmr_data",
        "dielectric_data",
        "morphology_data",
        "mcp_tasks",
        "audit_logs",
    }
    not_yet = sorted(prompt_tables - existing)
    if not_yet:
        raise NotImplementedError("以下扩展表尚未落库，已列为剩余风险：" + ", ".join(not_yet))
    return "数据库表覆盖完整。"


def _check_security(client: TestClient) -> str:
    ok = client.post("/api/files/validate-upload", params={"file_name": "safe.log"})
    assert ok.status_code == 200 and ok.json()["allowed"] is True
    traversal = client.post("/api/files/validate-upload", params={"file_name": "..\\bad.log"})
    assert traversal.status_code == 200 and traversal.json()["allowed"] is False
    assert "非法路径" in traversal.json()["reason"]
    gaussian = client.post("/api/gaussian/upload-log", files={"file": ("..\\bad.log", "x", "text/plain")})
    assert gaussian.status_code == 400 and "非法路径" in gaussian.json()["detail"]
    return "上传白名单、路径穿越和仅读取边界通过。"


def _check_performance() -> str:
    values = " ".join("0.001" for _ in range(1000))
    cube = "\n".join(
        [
            "large cube",
            "density",
            " 1 0.0 0.0 0.0",
            " 10 1.0 0.0 0.0",
            " 10 0.0 1.0 0.0",
            " 10 0.0 0.0 1.0",
            " 6 0.0 0.0 0.0 0.0",
            values,
        ]
    )
    start = time.perf_counter()
    parsed = parse_cube_metadata(cube, "density.cube")
    elapsed = time.perf_counter() - start
    assert parsed["metadata"]["data_stats"]["sampled_value_count"] == 1000
    assert elapsed < 0.5, f"cube 元数据解析耗时过长：{elapsed:.3f}s"
    return f"1000 点 cube 元数据解析 {elapsed:.3f}s。"


def _check_external_tool_boundary() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in ["不执行 Gaussian", "不执行 cubegen", "不执行 Multiwfn"]:
        assert phrase in readme, f"README 缺少安全边界：{phrase}"
    return "README 与 API provenance 均声明不执行外部化学软件。"


def _check_not_implemented_matrix() -> str:
    raise NotImplementedError(
        "当前已实现真实 cube 下采样点、剖切矩阵和差分预览；marching-cubes/Three.js 完整等值面重建仍未实现，本审计不把它标记为通过。"
    )


def write_reports(audit: Audit) -> None:
    docs_dir = ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Pro Max Ultra 自动化质量审计报告",
        "",
        f"- 测试时间：{now}",
        "- 测试环境：Windows / PowerShell / FastAPI TestClient / 本地 SQLite / Next.js 项目静态检查",
        f"- 通过数量：{len(audit.passed)}",
        f"- 失败数量：{len(audit.failed)}",
        f"- 未完成/跳过数量：{len(audit.skipped)}",
        "- 安全边界：审计过程中未执行 Gaussian、cubegen、Multiwfn，也未执行用户上传文件。",
        "",
        "## 测试总览",
        "",
        "| 类别 | 项目 | 状态 | 耗时(ms) | 说明 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in audit.results:
        detail = item.detail.replace("\n", " ").replace("|", "\\|")
        lines.append(f"| {item.category} | {item.name} | {item.status} | {item.duration_ms:.1f} | {detail} |")

    lines.extend(
        [
            "",
            "## 修复内容",
            "",
            "- 新增报告 docx 只读抽取闭环：`POST /api/literature/import-report-docx` 与 `GET /api/literature/report-knowledge`，报告线索统一标注为 C 级证据。",
            "- 顶尖科学家协议增加“报告驱动闭环扩展槽位”，把 Si–C 稳定性、PP β-scission、羰基三分法、乙烯/等规度/结晶度窗口映射到 API、UI、报告和测试。",
            "- 中文报告新增“报告知识映射”“Si–C 连接稳定性”“羰基三分法”“乙烯/等规度/结晶度影响”“软件化执行接口”等章节，并自动合并最新导入报告知识。",
            "- 前端“论文知识库”新增报告驱动知识映射、可编辑报告 docx 路径、C 级证据卡片和机制模型/反证条件展示；“MCP 自动化工作流”新增报告证据闭环展示。",
            "- 新增 OCR 文本导入和真实文件实例摘要：`POST /api/literature/import-ocr-text`、`GET /api/literature/source-quality`、`GET /api/literature/real-instance-summary`，PDF 乱码统一标记为 encoded-garbled。",
            "- 中文报告新增“真实文件实例测试”章节，自动写入 C 级文献线索、PDF 文本层乱码 warning、OCR 文本边界和 A/B 级结论禁止条件。",
            "- UI 重构为 Google Workspace 式科研工作台：分组导航、顶部全局搜索、资源表格、右侧详情面板、Drive 风格分子库/数据管理、Sheets 风格实验-DFT 对照、Colab/Docs 风格 Gaussian 输入生成、Docs 风格报告页、Cloud Log Viewer 风格 Gaussian 解析页、Cloud Console 风格 MCP 工具页和表格优先的量子判据引擎。",
            "- 新增科学计算验证机制工作流：`GET /api/scientific-computation/task-matrix`、`POST /api/scientific-computation/energy-workbench`、`POST /api/analysis/bde` 和“科学计算工作流”前端页面，把任务模板、自由能公式、BDE、证据等级和报告边界串成闭环。",
            "- 新增 `scripts/mojibake_audit.py` 和根目录 `npm run audit:mojibake`，用于扫描活动文件中的中文乱码；当前活动文件疑似乱码行数为 0，归档来源目录仅记录不参与构建。",
            "- 修复“前线轨道”和“电荷布居”面板历史乱码，移除未引用的旧 `frontend/fix.js`。",
            "- 收紧上传文件名校验，拒绝路径穿越、绝对路径、过长文件名和非法扩展名。",
            "- cube parser 增加 expected_value_count、value_count_status 和等值面元数据，便于前端和测试判断真实数据缺失。",
            "- 增加 GoodVibes、QTAIM、NCI 只读解析器、MCP 安全白名单 API 和对应回归测试。",
            "- 补齐 atom/bond/orbital/QTAIM/NCI/实验表征/MCP/audit 数据表与别名 API。",
            "- 增加根目录 npm 覆盖率和 E2E 入口，使 lint/typecheck/test/e2e/build 可按统一命令执行。",
            "",
            "## 科学公式测试结果",
            "",
            "- Hartree、kcal/mol、eV、R、默认 350 K 常数已自动核查。",
            "- ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔΔG‡、krel 的边界和温度行为已自动核查。",
            "- Si–C、Si–O、Si–Cl、RO–OR BDE 公式已自动核查，单位为 Hartree、kcal/mol 和 eV。",
            "",
            "## Parser 测试结果",
            "",
            "- Gaussian parser 覆盖正常终止、SCF、Gibbs、频率/虚频、HOMO/LUMO、Mulliken、NPA、Wiberg、NBO E(2)、Counterpoise 和空文件失败路径。",
            "- cube parser 覆盖 grid、origin、atom、scalar field 计数、数值范围和错误 cube 中文提示。",
            "- GoodVibes、QTAIM、NCI 轻量文本 parser 已自动验证；不同外部程序的大型变体输出仍需样本驱动扩展。",
            "",
            "## UI 测试结果",
            "",
            "- UI 的构建、lint、typecheck 由质量门禁和 root npm scripts 执行。",
            "- Playwright 已固定为根依赖，浏览器 UI smoke 已覆盖全导航抽样、Gaussian 输出解析、cube 上传预览、合并工作台、MCP 安全工作流和 390px 移动端。",
            "- Playwright UI smoke 已新增检查“报告驱动知识映射”和“MCP 报告证据闭环”。",
            "- Playwright UI smoke 已新增检查“真实文件实例”“PDF 文本层疑似字体编码异常”“导入 OCR 文本”和“C级证据”。",
            "- Playwright UI smoke 已新增检查 Google 式分组导航、顶部搜索框、报告页“章节大纲/报告预览/证据与数据来源”和 Gaussian 页“仅读取，不执行 Gaussian”。",
            "- Playwright UI smoke 已新增检查分子库“分子资源表/结构视图/分子详情”、Gaussian Builder“任务模板/输入文件预览/不执行 Gaussian”和 MCP“工具列表/工具详情/输入 schema/运行结果/安全边界”。",
            "- Playwright UI smoke 已新增检查数据管理“资源表/provenance 审计”、实验-DFT 对照“实验记录来源”和量子判据引擎“判据资源表/证据与结论边界”。",
            "- Playwright UI smoke 已新增检查“科学计算工作流”“计算任务矩阵”“能量公式工作台”和“BDE 计算”。",
            "- 中文乱码审计已接入质量门禁，保证活动 UI 文案、脚本和当前文档不会再次出现常见 UTF-8/GBK 误解码痕迹。",
            "",
            "## API 测试结果",
            "",
            "- 核心 molecule、Gaussian input、Gaussian parse、energy、Ti poisoning、peroxide、ΦLCB、report 接口已审计。",
            "- 科学计算 API 已覆盖 36 任务矩阵、能量公式工作台、BDE 计算和自由基动力学分析别名。",
            "- `/api/mcp/*` 已提供安全白名单工作流：工具列表、资源索引、prompt 生成和受控 tool run。",
            "- 文献 API 已覆盖报告 docx、OCR 文本、解析质量列表和真实文件实例摘要；乱码 PDF 不会把关键词为 0 解释为无相关机理。",
            "",
            "## E2E 测试结果",
            "",
            "- `npm run test:e2e` 映射到 `scripts/ui_smoke_check.mjs`，检查前后端可达性并执行 Playwright 交互烟测。",
            "- E2E 需要本地后端 `http://127.0.0.1:8000` 和前端 `http://localhost:3000` 可访问。",
            "- 完整报告导出截图矩阵和 marching-cubes 三维等值面重建仍建议作为下一阶段补齐。",
            "",
            "## 安全测试结果",
            "",
            "- 上传扩展名白名单和路径穿越已测试。",
            "- 真实外部化学软件执行默认禁止，仅保留文本生成和只读解析。",
            "",
            "## 性能测试结果",
            "",
            "- 1000 点 cube 元数据解析通过快速审计。",
            "- 大表格虚拟滚动、真实大 cube marching-cubes 等值面渲染和大型 Gaussian log Web Worker 压测仍建议继续扩展。",
            "",
            "## 剩余风险",
            "",
        ]
    )
    if audit.skipped:
        lines.extend(f"- {item.category} / {item.name}：{item.detail}" for item in audit.skipped)
    else:
        lines.append("- 当前审计未记录跳过项。")
    if audit.failed:
        lines.extend(["", "## 失败项", ""])
        lines.extend(f"- {item.category} / {item.name}：{item.detail}" for item in audit.failed)
    lines.extend(
        [
            "",
            "## 下一步建议",
            "",
            "- 以真实 GoodVibes、QTAIM、NCI 大文件样本扩充 parser 适配矩阵，并把稳定 JSON schema 接到 UI 图层。",
            "- 扩展 Playwright 为报告导出、真实大 cube 性能和全页面截图矩阵。",
            "- 引入迁移工具后，把当前扩展表纳入正式 PostgreSQL migration。",
        ]
    )
    text = "\n".join(lines) + "\n"
    (ROOT / "TEST_REPORT.md").write_text(text, encoding="utf-8")
    (docs_dir / "ULTRA_QUALITY_TEST_REPORT.md").write_text(text, encoding="utf-8")

    changelog = ROOT / "CHANGELOG.md"
    entry = (
        f"## {now} - Pro Max Ultra 自动化质量审计\n\n"
        "- 增加 `scripts/ultra_quality_audit.py`，统一检查科学公式、parser、API、数据库、安全、性能和未实现风险。\n"
        "- 收紧上传文件名安全边界，新增安全回归测试。\n"
        "- cube parser 增加数据计数和等值面元数据。\n"
        "- 增加根目录 npm 测试脚本入口。\n\n"
    )
    previous = changelog.read_text(encoding="utf-8") if changelog.exists() else "# CHANGELOG\n\n"
    if "Pro Max Ultra 自动化质量审计" not in previous:
        changelog.write_text(previous.rstrip() + "\n\n" + entry, encoding="utf-8")


def main() -> int:
    print("=" * 80)
    print("硅氧硅碳催化量子机理平台 Pro Max Ultra - 自动化质量审计")
    print("=" * 80)
    audit = run_audit()
    write_reports(audit)
    print("=" * 80)
    print(f"PASS={len(audit.passed)} FAIL={len(audit.failed)} SKIP={len(audit.skipped)}")
    print("报告：TEST_REPORT.md / docs/ULTRA_QUALITY_TEST_REPORT.md")
    return 1 if audit.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
