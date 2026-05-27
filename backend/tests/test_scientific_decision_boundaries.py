from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_delta_g_poison_boundary_labels_are_exact() -> None:
    productive = client.post(
        "/api/analysis/ti-poisoning",
        json={"o_ti_complex_g_hartree": -100.0, "pi_complex_g_hartree": -100.010},
    )
    assert productive.status_code == 200
    assert productive.json()["label"] == "生产性 C=C 插入占优"
    assert productive.json()["color"] == "green"

    competitive = client.post(
        "/api/analysis/ti-poisoning",
        json={"o_ti_complex_g_hartree": -100.0, "pi_complex_g_hartree": -100.0},
    )
    assert competitive.status_code == 200
    assert competitive.json()["label"] == "O→Ti 与 C=C 配位竞争"
    assert competitive.json()["color"] == "yellow"

    poisoned = client.post(
        "/api/analysis/ti-poisoning",
        json={"o_ti_complex_g_hartree": -100.010, "pi_complex_g_hartree": -100.0},
    )
    assert poisoned.status_code == 200
    assert poisoned.json()["label"] == "Ti 活性中心存在甲氧基毒化风险"
    assert poisoned.json()["color"] == "red"


def test_missing_pi_or_o_ti_energy_returns_chinese_error() -> None:
    missing_pi = client.post("/api/analysis/ti-poisoning", json={"o_ti_complex_g_hartree": -100.0})
    assert missing_pi.status_code == 422
    assert "缺少 π-complex 的自由能" in missing_pi.text

    missing_o_ti = client.post("/api/analysis/ti-poisoning", json={"pi_complex_g_hartree": -100.0})
    assert missing_o_ti.status_code == 422
    assert "缺少 O→Ti complex 的自由能" in missing_o_ti.text


def test_tea_capture_boundaries_and_nbo_guiding() -> None:
    response = client.post(
        "/api/analysis/tea-binding",
        json={
            "molecule_key": "MCSOMe",
            "mode": "Al<-O",
            "monomer_g_hartree": -100.0,
            "tea_g_hartree": -50.0,
            "complex_g_hartree": -150.020,
            "n_o_to_al_e2_kcal_mol": 18.0,
            "n_cl_to_al_e2_kcal_mol": 4.0,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["label"] == "甲氧基主导捕获"
    assert "服务器未执行 Gaussian" in payload["source"]

    over_capture = client.post(
        "/api/analysis/tea-binding",
        json={
            "molecule_key": "DMOS",
            "mode": "Al<-O",
            "monomer_g_hartree": -100.0,
            "tea_g_hartree": -50.0,
            "complex_g_hartree": -150.050,
        },
    )
    assert over_capture.status_code == 200
    assert over_capture.json()["label"] == "过度捕获"


def test_bond_descriptor_interpretations_are_falsifiable() -> None:
    weakened = client.post(
        "/api/analysis/bond-descriptors",
        json={
            "molecule_key": "MCSOMe",
            "descriptors": {
                "r_si_o_delta": 0.04,
                "nu_si_o_delta": -35.0,
                "wbi_si_o_delta": -0.08,
                "rho_bcp_delta": -0.02,
                "q_o": -0.74,
                "n_o_to_al_e2": 12.0,
                "n_o_to_ti_e2": 16.0,
                "delta_g_poison": -1.0,
            },
        },
    )
    assert weakened.status_code == 200
    text = " ".join(weakened.json()["interpretations"])
    assert "Si–O 键被 Lewis 酸配位削弱" in text
    assert "Al 捕获潜力" in text
    assert "O→Ti 毒化风险" in text

    missing = client.post("/api/analysis/bond-descriptors", json={"molecule_key": "MCSOMe", "descriptors": {}})
    assert missing.status_code == 200
    assert "未触发明确机制判据" in missing.json()["interpretations"][0]


def test_decision_engine_is_reproducible_and_preserves_source() -> None:
    payload = {
        "candidates": [
            {"molecule_key": "DCS", "e_insert": 9.0, "e_ti_poison": 8.0, "e_al_capture": -8.0, "e_post": -20.0, "e_intrinsic": 3.0, "source": "MOCK / EXAMPLE"},
            {"molecule_key": "MCSOMe", "e_insert": 11.0, "e_ti_poison": 6.0, "e_al_capture": -12.0, "e_post": -4.0, "e_intrinsic": 6.0, "source": "MOCK / EXAMPLE"},
            {"molecule_key": "DMOS", "e_insert": 19.0, "e_ti_poison": -1.0, "e_al_capture": -28.0, "e_post": -2.0, "e_intrinsic": 12.0, "source": "MOCK / EXAMPLE"},
        ]
    }
    first = client.post("/api/analysis/decision-engine", json=payload)
    second = client.post("/api/analysis/decision-engine", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["candidates"] == second.json()["candidates"]
    assert {row["source"] for row in first.json()["candidates"]} == {"MOCK / EXAMPLE"}
    assert "模板" in first.json()["reliability_note"]
    assert "真实科学结论" not in first.json()["conclusion_template"]


def test_mock_report_keeps_reliability_boundary() -> None:
    report = client.post(
        "/api/reports/generate",
        json={"project_title": "mock 边界报告", "format": "markdown", "payload": {"project_summary": "示例数据，不能作为真实结论。"}},
    )
    assert report.status_code == 200
    content = report.json()["content"]
    assert "示例数据仅用于界面演示，不能作为真实量子化学结论" in content
    assert "当前文件未提供" in content
    assert "## 证据等级系统" in content
    assert "A级为真实收敛计算" in content
    assert "## 最小可证伪任务" in content
    assert "## 软件化执行映射" in content
    assert "## 软件化执行接口" in content
    assert "## Si–C 连接稳定性" in content
    assert "## 羰基三分法" in content
    assert "## 乙烯/等规度/结晶度影响" in content
    assert "## 量子化学任务设计要求" in content
    assert "insertion TS" in content
    assert "## 波函数与电子结构分析要求" in content
    assert "## 过氧化物比较维度" in content
    assert "DCP" in content
    assert "## 实验表征逻辑" in content
    assert "## 顶尖 PI 工作标准" in content
