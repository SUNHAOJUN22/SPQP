import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.radical_v4 import PDF_GARBLED_WARNING, assess_text_quality


client = TestClient(app)


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
        + "".join(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>" for paragraph in paragraphs)
        + "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        archive.writestr("word/document.xml", xml)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seeded_molecules_are_available() -> None:
    response = client.get("/api/molecules")
    assert response.status_code == 200
    payload = response.json()
    keys = {row["key"] for row in payload}
    assert {"DCS", "MCSOMe", "DMOS", "TEA"}.issubset(keys)
    assert all("示例数据" in row["source"] for row in payload[:3])


def test_molecule_graph_endpoint_keeps_provenance() -> None:
    molecules = client.get("/api/molecules").json()
    molecule_id = next(row["id"] for row in molecules if row["key"] == "MCSOMe")
    graph = client.get(f"/api/molecules/{molecule_id}/graph")
    assert graph.status_code == 200
    payload = graph.json()
    assert payload["nodes"]
    assert "不能替代真实量子化学几何" in payload["provenance"]


def test_gaussian_input_generation_endpoint() -> None:
    response = client.post(
        "/api/gaussian/generate-input",
        json={
            "name": "MCSOMe",
            "job_type": "insertion TS",
            "method": "UPBE1PBE",
            "basis": "Def2SVP",
            "charge": 0,
            "multiplicity": 2,
            "coordinates": "C 0 0 0",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "Opt=(TS" in payload["content"]
    assert payload["provenance"] == "已生成输入文件；服务器未执行 Gaussian"


def test_ti_poisoning_endpoint() -> None:
    response = client.post(
        "/api/analysis/ti-poisoning",
        json={"o_ti_complex_g_hartree": -100.0, "pi_complex_g_hartree": -100.02},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["color"] == "green"
    assert payload["label"] == "生产性 C=C 插入占优"


def test_v2_literature_and_catalyst_endpoints() -> None:
    entities = client.get("/api/literature/entities")
    assert entities.status_code == 200
    assert "entities" in entities.json()

    catalysts = client.get("/api/catalyst-models")
    assert catalysts.status_code == 200
    names = {row["name"] for row in catalysts.json()["models"]}
    assert "MgCl2/TiCl4/Et" in names


def test_report_docx_import_and_report_knowledge_endpoint(tmp_path: Path) -> None:
    report_path = tmp_path / "report.docx"
    _write_minimal_docx(
        report_path,
        [
            "Si–O / Si–Cl 水解缩合形成 Si–O–Si 桥联，Si–C 连接臂需要用 BDE 与 29Si NMR 验证。",
            "Ziegler–Natta / TEA / Ti 体系中需要比较 Al←O、Al···Cl、O→Ti 毒化与 C=C productive π-complex。",
            "过氧化物 RO–OR 均裂产生自由基，PP β-scission 降解、长链支化 LCB、交联和氧化羰基副反应竞争。",
            "乙烯、等规度、结晶度、EPC 和 IPC 微相影响自由基扩散、停留时间窗口、MFR、GPC、SAOS 和介电损耗。",
        ],
    )
    imported = client.post(
        "/api/literature/import-report-docx",
        json={"path": str(report_path), "title": "测试 SiO/SiC/PP 报告"},
    )
    assert imported.status_code == 200
    payload = imported.json()
    assert payload["text_length"] > 100
    assert {item["evidence_level"] for item in payload["entities"]} == {"C"}
    assert any(item["chinese_name"] == "Si–C 侧链连接稳定性" for item in payload["entities"])
    assert "pp_scission_crosslinking" in payload["report_payload"]

    knowledge = client.get("/api/literature/report-knowledge")
    assert knowledge.status_code == 200
    knowledge_payload = knowledge.json()
    assert knowledge_payload["source_id"] is not None
    assert "顶尖科学家能力进化协议" == knowledge_payload["protocol"]["name"]
    assert any(item["paper_ready"] == "需要补充验证" for item in knowledge_payload["entities"])

    report = client.post(
        "/api/reports/generate",
        json={"project_title": "报告知识映射测试", "format": "markdown", "payload": {}},
    )
    assert report.status_code == 200
    content = report.json()["content"]
    assert "## 报告知识映射" in content
    assert "Si–C 连接稳定性" in content
    assert "羰基三分法" in content
    assert "软件化执行接口" in content
    assert "C" in content


def test_pdf_encoded_garbled_quality_detection() -> None:
    quality = assess_text_quality("\ue001\ue002\ue003\ue004\ue005\ue006\ue007\ue008\ue009\ue010", "pdf")
    assert quality["quality"] == "encoded-garbled"
    assert quality["warning"] == PDF_GARBLED_WARNING


def test_ocr_text_import_and_real_instance_summary() -> None:
    response = client.post(
        "/api/literature/import-ocr-text",
        json={
            "source_title": "PP 自由基综述 OCR 测试",
            "source_path": r"C:\Users\resj6\Desktop\Radical reactions on polypropylene in the solid state.pdf",
            "ocr_text": (
                "peroxide radical polypropylene beta-scission degradation branching crosslinking carbonyl "
                "ethylene isotacticity crystallinity Si-C Si-O Ziegler-Natta TEA Ti poisoning"
            ),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["parse_quality"] == "readable"
    assert payload["text_length"] > 80
    assert payload["keyword_counts"]["radical_keywords"]["peroxide_or_radical"] >= 2
    assert "证据等级为 C" in payload["provenance"]

    quality = client.get("/api/literature/source-quality")
    assert quality.status_code == 200
    assert any(row["source_type"] == "ocr-text" for row in quality.json()["sources"])

    summary = client.get("/api/literature/real-instance-summary")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert "instances" in summary_payload
    assert "C 级文献线索" in summary_payload["evidence_boundary"]

    report = client.post(
        "/api/reports/generate",
        json={"project_title": "真实文件实例测试", "format": "markdown", "payload": {}},
    )
    assert report.status_code == 200
    assert "## 真实文件实例测试" in report.json()["content"]
    assert "PDF 文本层疑似字体编码异常" in report.json()["content"]


def test_experiment_csv_import_and_correlation() -> None:
    response = client.post(
        "/api/experiments/import-csv",
        json={
            "dataset_name": "测试实验数据",
            "csv_text": "monomer,catalyst_system,polymerization,activity,insertion_ratio\nC6-DCS,MgCl2/TiCl4,乙烯共聚,80,60\n",
        },
    )
    assert response.status_code == 200
    assert response.json()["count"] == 1

    correlation = client.post(
        "/api/analysis/dft-experiment-correlation",
        json={
            "records": [
                {"delta_g_barrier_kcal_mol": 12.0, "activity": 90, "insertion_ratio": 72},
                {"delta_g_barrier_kcal_mol": 18.0, "activity": 40, "insertion_ratio": 28},
            ]
        },
    )
    assert correlation.status_code == 200
    assert correlation.json()["activity_barrier_pearson"] < 0


def test_mechanism_hypothesis_endpoint_adjusts_poisoning_confidence() -> None:
    response = client.post("/api/analysis/mechanism-hypotheses", json={"evidence": {"delta_g_poison_kcal_mol": -2.0}})
    assert response.status_code == 200
    poisoning = next(item for item in response.json()["hypotheses"] if item["key"] == "o-ti-poisoning")
    assert poisoning["confidence"] > 0.7


def test_cube_upload_metadata_endpoint() -> None:
    cube = (
        "comment line 1\n"
        "comment line 2\n"
        " 2 0.0 0.0 0.0\n"
        " 3 1.0 0.0 0.0\n"
        " 4 0.0 1.0 0.0\n"
        " 5 0.0 0.0 1.0\n"
        " 1 0.0 0.0 0.0 0.0\n"
        " 8 0.0 1.0 0.0 0.0\n"
    )
    response = client.post("/api/cube/upload", files={"file": ("HOMO_test.cube", cube, "text/plain")})
    assert response.status_code == 200
    payload = response.json()
    assert payload["cube_type"] == "HOMO 前线轨道"
    assert payload["atom_count"] == 2
    assert payload["metadata"]["data_stats"]["sampled_value_count"] == 0
    assert payload["metadata"]["atoms"][1]["atomic_number"] == 8


def test_cube_volume_and_slice_preview_are_read_only_scalar_samples() -> None:
    cube = (
        "density preview\n"
        "small real scalar field\n"
        " 1 0.0 0.0 0.0\n"
        " 2 1.0 0.0 0.0\n"
        " 2 0.0 1.0 0.0\n"
        " 2 0.0 0.0 1.0\n"
        " 8 0.0 0.0 0.0 0.0\n"
        " -0.4 -0.2 0.1 0.3 0.5 0.7 -0.1 0.0\n"
    )
    upload = client.post("/api/cubes/upload", files={"file": ("density_small.cube", cube, "text/plain")})
    assert upload.status_code == 200
    cube_id = upload.json()["id"]

    isosurface = client.get(f"/api/cubes/{cube_id}/isosurface")
    assert isosurface.status_code == 200
    preview = isosurface.json()
    assert preview["expected_value_count"] == 8
    assert preview["observed_value_count"] == 8
    assert preview["phase_counts"]["positive"] == 4
    assert "只读解析" in preview["provenance"]

    sliced = client.get(f"/api/cubes/{cube_id}/slice?axis=z&plane_index=1")
    assert sliced.status_code == 200
    slice_payload = sliced.json()
    assert slice_payload["shape"] == {"width": 2, "height": 2}
    assert slice_payload["values"] == [[-0.2, 0.7], [0.3, 0.0]]

    invalid_axis = client.get(f"/api/cubes/{cube_id}/slice?axis=q")
    assert invalid_axis.status_code == 400
    assert "剖切轴" in invalid_axis.json()["detail"]


def test_cube_difference_density_preview_requires_matching_uploaded_cubes() -> None:
    cube_a = (
        "density A\n"
        "small scalar field\n"
        " 1 0.0 0.0 0.0\n"
        " 2 1.0 0.0 0.0\n"
        " 2 0.0 1.0 0.0\n"
        " 1 0.0 0.0 1.0\n"
        " 8 0.0 0.0 0.0 0.0\n"
        " 0.4 0.2 0.0 -0.2\n"
    )
    cube_b = (
        "density B\n"
        "small scalar field\n"
        " 1 0.0 0.0 0.0\n"
        " 2 1.0 0.0 0.0\n"
        " 2 0.0 1.0 0.0\n"
        " 1 0.0 0.0 1.0\n"
        " 8 0.0 0.0 0.0 0.0\n"
        " 0.1 0.3 -0.1 -0.2\n"
    )
    first = client.post("/api/cubes/upload", files={"file": ("density_a.cube", cube_a, "text/plain")}).json()
    second = client.post("/api/cubes/upload", files={"file": ("density_b.cube", cube_b, "text/plain")}).json()
    diff = client.post("/api/cubes/difference-density", json={"cube_a_id": first["id"], "cube_b_id": second["id"]})
    assert diff.status_code == 200
    payload = diff.json()
    assert payload["formula"] == "Δρ(r) = ρ_A(r) - ρ_B(r)"
    assert abs(payload["min_delta"] - (-0.1)) < 1e-12
    assert abs(payload["max_delta"] - 0.3) < 1e-12
    assert "不执行 cubegen" in payload["provenance"]
