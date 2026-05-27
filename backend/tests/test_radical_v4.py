from fastapi.testclient import TestClient

from app.main import app
from app.services.radical_v4 import (
    carbonyl_taxonomy,
    experimental_design_matrix,
    peroxide_profile,
    radical_branching_vs_scission,
    residence_time_window,
    sic_stability,
    unified_lcb_framework,
)


client = TestClient(app)


def test_peroxide_profile_half_life_window_and_carbonyl_boundary() -> None:
    result = peroxide_profile(
        {
            "name": "BPO",
            "has_carbonyl": True,
            "half_life_min": 5.0,
            "residence_time_min": 5.0,
            "oxygen_level_percent": 1.0,
            "roor_bde_kcal_mol": 32.0,
        }
    )
    assert 49.0 < result["conversion_percent"] < 51.0
    assert "羰基" in result["carbonyl_note"]
    assert "不能作为真实工艺结论" in result["reliability_note"]


def test_radical_competition_responds_to_coagent_and_oxygen() -> None:
    no_coagent = radical_branching_vs_scission({"coagent_phr": 0.0, "oxygen_level_percent": 0.2})
    with_coagent = radical_branching_vs_scission({"coagent_phr": 0.6, "oxygen_level_percent": 0.2})
    assert with_coagent["fractions"]["branching"] > no_coagent["fractions"]["branching"]

    oxygen_rich = radical_branching_vs_scission({"coagent_phr": 0.0, "oxygen_level_percent": 12.0})
    assert oxygen_rich["fractions"]["oxidation"] > no_coagent["fractions"]["oxidation"]


def test_sic_stability_never_fabricates_missing_values() -> None:
    missing = sic_stability({})
    assert missing["label"] == "当前数据不足"
    assert "不会用示例值补全" in missing["reliability_note"]

    stable = sic_stability({"bde_sic_kcal_mol": 86.0, "bde_sio_kcal_mol": 105.0, "radical_attack_barrier_kcal_mol": 15.0})
    assert stable["label"] == "Si–C 键相对稳定"
    assert any("Si–C BDE 较高" in item for item in stable["interpretations"])


def test_residence_time_window_boundaries() -> None:
    short = residence_time_window({"half_life_min": 10.0, "residence_time_min": 1.0})
    assert short["status"] == "停留时间偏短"

    long = residence_time_window({"half_life_min": 1.0, "residence_time_min": 5.0})
    assert long["status"] == "停留时间偏长"


def test_unified_framework_and_carbonyl_taxonomy_boundaries() -> None:
    framework = unified_lcb_framework(
        {
            "chi_insert": 0.8,
            "chi_hydrolysis": 0.8,
            "chi_condensation": 0.7,
            "chi_radical_recombination": 0.5,
            "chi_beta_scission": 0.2,
            "chi_oxidation": 0.1,
            "chi_ti_poison": 0.1,
            "chi_over_gel": 0.1,
        }
    )
    assert framework["lcb_efficiency_formula"]["score_percent"] > 70
    assert "Si–O 路线" in framework["boss_summary"]

    taxonomy = carbonyl_taxonomy()
    assert len(taxonomy["items"]) == 3
    assert "不能仅凭含羰基" in taxonomy["items"][0]["boundary"]

    matrix = experimental_design_matrix()
    assert len(matrix["layers"]) == 3
    assert any("GPC" in item for item in matrix["required_characterization"])


def test_radical_v4_api_endpoints() -> None:
    library = client.get("/api/analysis/peroxide-library")
    assert library.status_code == 200
    assert library.json()["species"]

    profile = client.post(
        "/api/analysis/peroxide-profile",
        json={"name": "DCP", "half_life_min": 5.0, "residence_time_min": 5.0, "roor_bde_kcal_mol": 37.0},
    )
    assert profile.status_code == 200
    assert profile.json()["label"] == "停留时间窗口适中"

    competition = client.post("/api/analysis/radical-branching-vs-scission", json={"coagent_phr": 0.3})
    assert competition.status_code == 200
    assert "fractions" in competition.json()

    sic = client.post("/api/analysis/sic-stability", json={"bde_sic_kcal_mol": 86.0})
    assert sic.status_code == 200
    assert "Si–C" in sic.json()["label"]

    residence = client.post("/api/analysis/residence-time-window", json={"half_life_min": 5.0, "residence_time_min": 5.0})
    assert residence.status_code == 200
    assert residence.json()["status"] == "窗口适中"

    framework = client.post(
        "/api/analysis/unified-lcb-framework",
        json={"chi_insert": 0.8, "chi_hydrolysis": 0.8, "chi_beta_scission": 0.2},
    )
    assert framework.status_code == 200
    assert "route_comparison" in framework.json()

    carbonyl = client.get("/api/analysis/carbonyl-taxonomy")
    assert carbonyl.status_code == 200
    assert len(carbonyl.json()["items"]) == 3

    design = client.get("/api/analysis/peroxide-experimental-design")
    assert design.status_code == 200
    assert "required_characterization" in design.json()
