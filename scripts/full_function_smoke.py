from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


client = TestClient(app)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


SAMPLE_LOG = """
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
 Mulliken atomic spin densities:
      1  Si   0.112
      2  O   -0.044
 Sum of Mulliken spin densities =   0.06800
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
 Counterpoise corrected energy = -682.150000
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
"""


SAMPLE_CUBE = (
    "density preview\n"
    "mock small cube\n"
    " 2 0.0 0.0 0.0\n"
    " 2 1.0 0.0 0.0\n"
    " 2 0.0 1.0 0.0\n"
    " 2 0.0 0.0 1.0\n"
    " 1 0.0 0.0 0.0 0.0\n"
    " 8 0.0 1.0 0.0 0.0\n"
    " 0.10 -0.20 0.30 -0.40 0.50 -0.60 0.70 -0.80\n"
)


def check(name: str, method: str, path: str, **kwargs) -> dict:
    start = perf_counter()
    response = getattr(client, method.lower())(path, **kwargs)
    elapsed = (perf_counter() - start) * 1000
    if response.status_code >= 400:
        raise AssertionError(f"{name} failed: {response.status_code} {response.text[:500]}")
    payload = response.json()
    print(f"[PASS] {name:<34} {response.status_code:>3} {elapsed:7.1f} ms")
    return payload


def check_error(name: str, method: str, path: str, expected_status: int, expected_detail: str | None = None, **kwargs) -> dict:
    start = perf_counter()
    response = getattr(client, method.lower())(path, **kwargs)
    elapsed = (perf_counter() - start) * 1000
    if response.status_code != expected_status:
        raise AssertionError(f"{name} expected {expected_status}, got {response.status_code}: {response.text[:500]}")
    payload = response.json()
    if expected_detail is not None and expected_detail not in json.dumps(payload, ensure_ascii=False):
        raise AssertionError(f"{name} did not include expected Chinese error: {expected_detail}; payload={payload}")
    print(f"[PASS] {name:<34} {response.status_code:>3} {elapsed:7.1f} ms")
    return payload


def main() -> int:
    print("=" * 86)
    print("硅氧键催化量子研究平台 - 全功能 API 烟测")
    print("=" * 86)

    health = check("健康检查", "GET", "/api/health")
    assert health["status"] == "ok"

    molecules = check("分子库列表", "GET", "/api/molecules")
    assert any(item["key"] == "MCSOMe" for item in molecules)
    first_id = molecules[0]["id"]
    xyz = check("分子 XYZ 导出", "GET", f"/api/molecules/{first_id}/xyz")
    assert "content" in xyz
    graph = check("分子图谱导出", "GET", f"/api/molecules/{first_id}/graph")
    assert "不能替代真实量子化学几何" in graph["provenance"]
    smoke_key = f"SMOKE-ALKENE-{uuid.uuid4().hex[:8]}"
    created = check(
        "新建分子",
        "POST",
        "/api/molecules",
        json={"key": smoke_key, "name": "smoke test alkene", "smiles": "C=C", "source": "用户输入"},
    )
    assert created["key"] == smoke_key
    check("RDKit 构象占位", "POST", f"/api/molecules/{first_id}/conformers")

    check("论文实体列表", "GET", "/api/literature/entities")
    check("催化剂模型列表", "GET", "/api/catalyst-models")
    thesis_path = Path(r"C:\Users\resj6\Desktop\pri\博士学位论文.docx")
    if thesis_path.exists():
        thesis = check("博士论文 DOCX 导入", "POST", "/api/literature/import-thesis", json={"path": str(thesis_path), "title": "博士论文烟测导入"})
        assert thesis["text_length"] > 1000
    check("报告知识库读取", "GET", "/api/literature/report-knowledge")
    ocr_import = check(
        "OCR 文本导入",
        "POST",
        "/api/literature/import-ocr-text",
        json={
            "source_title": "烟测 PP 自由基综述 OCR 文本",
            "source_path": r"C:\Users\resj6\Desktop\Radical reactions on polypropylene in the solid state.pdf",
            "ocr_text": "peroxide radical PP beta-scission degradation branching crosslinking carbonyl ethylene isotacticity crystallinity Si-C Si-O TEA Ti",
        },
    )
    assert ocr_import["parse_quality"] == "readable"
    source_quality = check("文献解析质量列表", "GET", "/api/literature/source-quality")
    assert "sources" in source_quality
    real_instances = check("真实文件实例摘要", "GET", "/api/literature/real-instance-summary")
    assert "instances" in real_instances
    report_docx = Path(r"C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx")
    if report_docx.exists():
        report_import = check(
            "SiO/SiC/PP 报告 DOCX 导入",
            "POST",
            "/api/literature/import-report-docx",
            json={"path": str(report_docx), "title": "烟测 SiO/SiC/PP 报告"},
        )
        assert report_import["entities"]

    experiment = check(
        "实验 CSV 导入",
        "POST",
        "/api/experiments/import-csv",
        json={
            "dataset_name": "全功能烟测实验",
            "csv_text": "monomer,catalyst_system,polymerization,activity,insertion_ratio\nC6-DCS,MgCl2/TiCl4,乙烯共聚,80,60\n",
        },
    )
    assert experiment["count"] == 1
    check("实验数据列表", "GET", "/api/experiments")

    generated = check(
        "Gaussian 标准输入生成",
        "POST",
        "/api/gaussian/generate-input",
        json={"name": "MCSOMe", "job_type": "insertion TS", "coordinates": "C 0 0 0", "multiplicity": 2},
    )
    assert "Opt=(TS" in generated["content"]
    parsed = check("Gaussian 文本解析", "POST", "/api/parse/gaussian-log", json={"file_name": "smoke.log", "text": SAMPLE_LOG})
    assert parsed["normal_termination"]["value"] is True
    assert parsed["spin_multiplicity"]["value"] == 2
    check("Gaussian 解析别名", "POST", "/api/gaussian/parse-log", json={"file_name": "smoke.log", "text": SAMPLE_LOG})
    check("GoodVibes 只读解析", "POST", "/api/parse/goodvibes", json={"file_name": "goodvibes.out", "text": "o MCSOMe.log 298.15 -100.0 -99.91"})
    check("QTAIM 只读解析", "POST", "/api/parse/qtaim", json={"file_name": "qtaim.txt", "text": "BCP Si-O rho=0.11 laplacian=0.32 H=-0.02"})
    check("NCI 只读解析", "POST", "/api/parse/nci", json={"file_name": "nci.txt", "text": "sign(lambda2)rho=-0.03 RDG=0.18"})
    uploaded_log = check("Gaussian 文件上传解析", "POST", "/api/gaussian/upload-log", files={"file": ("smoke.log", SAMPLE_LOG, "text/plain")})
    assert uploaded_log["quality"] == "complete"
    check_error("拒绝非法 Gaussian 文件", "POST", "/api/gaussian/upload-log", 400, "该接口仅接受 .log 和 .out 文件", files={"file": ("bad.txt", "not a log", "text/plain")})
    check("Gaussian 任务列表", "GET", "/api/gaussian/jobs")

    check("能量组分 ΔGbind", "POST", "/api/analysis/energy-components", json={"complex_g_hartree": -200.05, "fragment_g_hartree": [-100.0, -100.0]})
    check(
        "TEA 助剂结合",
        "POST",
        "/api/analysis/tea-binding",
        json={"molecule_key": "MCSOMe", "mode": "Al<-O", "monomer_g_hartree": -100.0, "tea_g_hartree": -50.0, "complex_g_hartree": -150.02},
    )
    check("Ti 毒化判据", "POST", "/api/analysis/ti-poisoning", json={"o_ti_complex_g_hartree": -100.0, "pi_complex_g_hartree": -100.02})
    check(
        "插入反应剖面",
        "POST",
        "/api/analysis/insertion-profile",
        json={"free_site_monomer_g_hartree": -500.0, "pi_complex_g_hartree": -500.01, "ts_g_hartree": -499.98, "product_g_hartree": -500.04, "reference_barrier_kcal_mol": 10.0},
    )
    check("相对速率", "POST", "/api/analysis/rate-comparison", json={"barriers_kcal_mol": {"DCS": 10.0, "MCSOMe": 11.0}, "reference_key": "DCS"})
    check(
        "硅氧键描述符",
        "POST",
        "/api/analysis/bond-descriptors",
        json={"molecule_key": "MCSOMe", "descriptors": {"r_si_o_delta": 0.04, "nu_si_o_delta": -35, "wbi_si_o_delta": -0.08, "rho_bcp_delta": -0.02}},
    )
    check("Si-O 键分析别名", "POST", "/api/analysis/sio-bond", json={"molecule_key": "MCSOMe", "descriptors": {"r_si_o_delta": 0.02}})
    check("Si-C 键分析别名", "POST", "/api/analysis/sic-bond", json={"bde_sic_kcal_mol": 86.0})
    check("水解缩合分析", "POST", "/api/analysis/hydrolysis-condensation", json={"delta_g_hydrolysis_kcal_mol": 3.0, "delta_g_condensation_kcal_mol": 1.0})
    check(
        "量子判据引擎",
        "POST",
        "/api/analysis/decision-engine",
        json={"candidates": [{"molecule_key": "MCSOMe", "e_insert": 12, "e_ti_poison": 6, "e_al_capture": -12, "e_post": -4, "e_intrinsic": 6}]},
    )
    check("实验-DFT 相关性", "POST", "/api/analysis/dft-experiment-correlation", json={"records": [{"delta_g_barrier_kcal_mol": 12, "activity": 90}, {"delta_g_barrier_kcal_mol": 18, "activity": 30}]})
    check("可证伪机制假说", "POST", "/api/analysis/mechanism-hypotheses", json={"evidence": {"delta_g_poison_kcal_mol": -1.5}})
    check("示例判据矩阵", "GET", "/api/analysis/mock-decision-matrix")
    task_matrix = check("科学计算任务矩阵", "GET", "/api/scientific-computation/task-matrix")
    assert task_matrix["total_tasks"] == 36
    check(
        "科学能量公式工作台",
        "POST",
        "/api/scientific-computation/energy-workbench",
        json={
            "complex_g_hartree": -150.025,
            "fragment_g_hartree": [-100.0, -50.0],
            "o_ti_complex_g_hartree": -100.0,
            "pi_complex_g_hartree": -100.02,
            "free_site_monomer_g_hartree": -500.0,
            "ts_g_hartree": -499.98,
            "product_g_hartree": -500.04,
            "reference_barrier_kcal_mol": 10.0,
        },
    )
    check(
        "BDE 键解离能计算",
        "POST",
        "/api/analysis/bde",
        json={"bond_type": "Si-C", "g_fragments_hartree": -199.86, "g_molecule_hartree": -200.0, "evidence_grade": "C"},
    )
    check("自由基动力学分析别名", "POST", "/api/analysis/radical-kinetics", json={"t_end": 1.0, "steps": 4})

    report = check("中文报告生成", "POST", "/api/reports/generate", json={"project_title": "全功能烟测报告", "format": "markdown", "payload": {"note": "smoke"}})
    assert "content" in report
    check("中文报告读取", "GET", f"/api/reports/{report['id']}")

    cube = check("cube 文件上传", "POST", "/api/cube/upload", files={"file": ("smoke_density.cube", SAMPLE_CUBE, "text/plain")})
    assert cube["metadata"]["data_stats"]["sampled_value_count"] == 8
    check("cube 元数据读取", "GET", f"/api/cube/{cube['id']}/metadata")
    isosurface = check("cube 下采样体素预览", "GET", f"/api/cubes/{cube['id']}/isosurface")
    assert isosurface["observed_value_count"] == 8
    slice_preview = check("cube 剖切矩阵预览", "GET", f"/api/cubes/{cube['id']}/slice?axis=z")
    assert slice_preview["shape"]["width"] == 2
    cube_b = check("第二个 cube 文件上传", "POST", "/api/cube/upload", files={"file": ("smoke_density_b.cube", SAMPLE_CUBE.replace("0.10", "0.05", 1), "text/plain")})
    difference = check("cube 差分电子密度", "POST", "/api/cubes/difference-density", json={"cube_a_id": cube["id"], "cube_b_id": cube_b["id"]})
    assert difference["formula"] == "Δρ(r) = ρ_A(r) - ρ_B(r)"
    check_error("拒绝非法 cube 文件", "POST", "/api/cube/upload", 400, "当前文件不是有效 cube 文件", files={"file": ("bad.txt", "not a cube", "text/plain")})
    check("上传文件名校验", "POST", "/api/files/validate-upload?file_name=smoke.log")

    check("整合源图", "GET", "/api/integration/source-map")
    task_groups = check("Gaussian 36 任务组", "GET", "/api/integration/gaussian-task-groups")
    assert task_groups["total_tasks"] == 36
    check("高级 Gaussian 任务模板", "POST", "/api/integration/build-gaussian-task", json={"task_id": "ti_pi_complex", "molecule_name": "MCSOMe_Ti", "coordinates": ["C 0 0 0"]})
    check("分子智能识别", "POST", "/api/integration/molecule-intelligence", json={"smiles": "C=CCCCC[Si](C)(OC)Cl"})
    check(
        "反应能量剖面分析",
        "POST",
        "/api/integration/reaction-profile",
        json={"states": [{"name": "free", "energy_hartree": -100.0}, {"name": "TS", "energy_hartree": -99.98}, {"name": "product", "energy_hartree": -100.03}]},
    )
    check_error(
        "缺少反应能量中文错误",
        "POST",
        "/api/integration/reaction-profile",
        400,
        "至少需要一个反应态",
        json={"states": []},
    )

    check("Ultra 合并清单", "GET", "/api/merged/ultra-inventory")
    check("四轴判据模型", "POST", "/api/merged/four-axis-decision", json={"monomer_key": "MCSOMe", "data": {"delta_g_poison_kcal_mol": 6, "delta_g_insert_kcal_mol": 12, "tea_binding_kcal_mol": -12}})
    check("后反应动力学", "POST", "/api/merged/radical-kinetics", json={"t_end": 2.0, "steps": 10})
    check("Boltzmann 权重", "POST", "/api/merged/boltzmann-weights", json={"energies_kcal_mol": [0, 1, 3], "temperature_k": 350})
    check("Wigner 速率修正", "POST", "/api/merged/wigner-rate", json={"delta_delta_g_kcal_mol": 1, "nu_imag_1_cm_1": -500, "nu_imag_2_cm_1": -400})
    check("V4 过氧化物结构库", "GET", "/api/analysis/peroxide-library")
    check(
        "V4 过氧化物画像",
        "POST",
        "/api/analysis/peroxide-profile",
        json={"name": "DCP", "half_life_min": 5.0, "residence_time_min": 5.0, "roor_bde_kcal_mol": 37.0},
    )
    check(
        "V4 降解-交联竞争",
        "POST",
        "/api/analysis/radical-branching-vs-scission",
        json={"coagent_phr": 0.35, "oxygen_level_percent": 0.3, "ethylene_mol_percent": 4.0},
    )
    check("V4 Si-C 稳定性", "POST", "/api/analysis/sic-stability", json={"bde_sic_kcal_mol": 86.0, "bde_sio_kcal_mol": 105.0})
    check("V4 停留时间窗口", "POST", "/api/analysis/residence-time-window", json={"half_life_min": 5.0, "residence_time_min": 5.0})
    check(
        "V4 统一 LCB 框架",
        "POST",
        "/api/analysis/unified-lcb-framework",
        json={"chi_insert": 0.8, "chi_hydrolysis": 0.7, "chi_beta_scission": 0.2, "chi_oxidation": 0.1},
    )
    check("V4 羰基效应三分法", "GET", "/api/analysis/carbonyl-taxonomy")
    check("V4 过氧化物实验矩阵", "GET", "/api/analysis/peroxide-experimental-design")
    check("自由基 β-scission 别名", "POST", "/api/analysis/radical-beta-scission", json={"oxygen_level_percent": 0.2})
    check("过氧化物选择别名", "POST", "/api/analysis/peroxide-selection", json={"name": "DCP", "half_life_min": 5.0})
    check("实验 GPC 导入占位", "POST", "/api/experimental/import-gpc", json={"records": [{"sample_key": "SMOKE", "mw": 200000}]})
    check("MCP 工具清单", "GET", "/api/mcp/tools")
    check("MCP 资源索引", "GET", "/api/mcp/resources")
    check("MCP prompt 生成", "POST", "/api/mcp/generate-prompt", json={"topic": "Si-C 与 PP β-scission"})
    check("顶尖科学家协议", "GET", "/api/research/top-scientist-protocol")
    check("顶尖科学家 Prompt", "POST", "/api/research/top-scientist-prompt", json={"topic": "Si-C 与 PP β-scission"})
    check("MCP 安全工具执行", "POST", "/api/mcp/run-tool", json={"tool_name": "validate-upload", "arguments": {"file_name": "smoke.log"}})
    check("MCP 顶尖科学家工具执行", "POST", "/api/mcp/run-tool", json={"tool_name": "generate-top-scientist-prompt", "arguments": {"topic": "MCSOMe 平衡候选"}})
    radical_pdf = Path(r"C:\Users\resj6\Desktop\Radical reactions on polypropylene in the solid state.pdf")
    if radical_pdf.exists():
        imported = check(
            "V4 聚丙烯自由基综述导入",
            "POST",
            "/api/literature/import-polypropylene-radical-review",
            json={"path": str(radical_pdf), "title": "Radical reactions on polypropylene in the solid state"},
        )
        assert "entities" in imported

    print("=" * 86)
    print("全功能 API 烟测通过。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("[FAIL]", exc)
        raise
