from __future__ import annotations

import math

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.energy import bond_dissociation_energy, classify_bde, hartree_to_ev


client = TestClient(app)


def test_bde_core_units_and_classification() -> None:
    result = bond_dissociation_energy(-199.86, -200.0)
    assert result["bde_hartree"] == pytest.approx(0.14)
    assert result["bde_kcal_mol"] == pytest.approx(87.85132636)
    assert result["bde_ev"] == pytest.approx(hartree_to_ev(0.14))
    assert classify_bde("Si-C", result["bde_kcal_mol"]) == "Si–C 侧链连接稳定"
    assert classify_bde("Si-C", 55.0) == "Si–C 连接臂存在失效风险"


def test_task_matrix_exposes_36_templates_and_safety_boundary() -> None:
    response = client.get("/api/scientific-computation/task-matrix")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_tasks"] == 36
    assert payload["evidence_grade"] == "D"
    assert "不执行 Gaussian" in payload["safety_boundaries"]
    flattened = [task for group in payload["groups"] for task in group["tasks"]]
    assert any(task["task_id"] == "sic_bde" for task in flattened)
    assert any(task["task_id"] == "pp_beta_ts" for task in flattened)
    assert all("safety_note" in task for task in flattened)


def test_energy_workbench_computes_formulas_and_reports_missing_paths() -> None:
    response = client.post(
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
            "temperature_k": 350.0,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["delta_g_bind"]["kcal_mol"] == pytest.approx(-0.025 * 627.509474)
    assert payload["delta_g_poison"]["label"] == "生产性 C=C 插入占优"
    assert payload["insertion_profile"]["delta_g_barrier_kcal_mol"] == pytest.approx(0.02 * 627.509474)
    assert math.isfinite(payload["insertion_profile"]["krel"])

    missing = client.post("/api/scientific-computation/energy-workbench", json={}).json()
    assert "缺少络合物或片段 Gibbs 自由能" in "\n".join(missing["warnings"])
    assert "缺少 π-complex 或 O→Ti complex" in "\n".join(missing["warnings"])
    assert "缺少 TS、π-complex 或参考态自由能" in "\n".join(missing["warnings"])


def test_bde_api_keeps_evidence_and_mock_boundaries() -> None:
    response = client.post(
        "/api/analysis/bde",
        json={
            "bond_type": "RO-OR",
            "g_fragments_hartree": -99.94,
            "g_molecule_hartree": -100.0,
            "evidence_grade": "D",
            "is_mock": True,
            "source": "示例数据",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["bde_kcal_mol"] == pytest.approx(0.06 * 627.509474)
    assert payload["evidence_grade"] == "D"
    assert payload["is_mock"] is True
    assert "示例数据不能作为真实科学结论" in payload["reliability_note"]
    assert payload["formula"] == "BDE(RO–OR) = G(2RO•) − G(RO–OR)"

    bad = client.post(
        "/api/analysis/bde",
        json={"bond_type": "Si-C", "g_fragments_hartree": "NaN", "g_molecule_hartree": -100.0},
    )
    assert bad.status_code in {400, 422}


def test_radical_kinetics_analysis_alias() -> None:
    response = client.post("/api/analysis/radical-kinetics", json={"t_end": 1.0, "steps": 4})
    assert response.status_code == 200
    payload = response.json()
    assert "formula" in payload
    assert "trajectory" in payload or "time" in payload or "series" in payload
    assert "不执行外部化学软件" in payload["provenance"]
