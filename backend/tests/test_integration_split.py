from fastapi.testclient import TestClient

from app.main import app
from app.services.integrated_science import analyze_reaction_profile
from app.services.molecule_intelligence import analyze_molecule_intelligence


client = TestClient(app)


def test_advanced_gaussian_task_groups_are_integrated() -> None:
    response = client.get("/api/integration/gaussian-task-groups")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_tasks"] == 36
    assert "A" in payload["groups"]


def test_advanced_gaussian_build_task_is_read_only() -> None:
    response = client.post(
        "/api/integration/build-gaussian-task",
        json={"task_id": "ti_pi_complex", "molecule_name": "MCSOMe_Ti", "coordinates": ["C 0 0 0"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "UPBE1PBE" in payload["content"]
    assert "0 2" in payload["content"]
    assert "不会在服务器执行" in payload["warning"]


def test_molecule_intelligence_identifies_sites() -> None:
    result = analyze_molecule_intelligence("C=CCCCC[Si](C)(OC)Cl")
    labels = {site["label"] for site in result["sites"]}
    assert "Si 活性中心" in labels
    assert "OMe 氧 Lewis 给体" in labels
    assert "Si–Cl 助剂导向位点" in labels


def test_reaction_profile_analysis() -> None:
    result = analyze_reaction_profile(
        [
            {"name": "free active site + monomer", "energy_hartree": -100.0},
            {"name": "pi-complex", "energy_hartree": -100.01},
            {"name": "TS", "energy_hartree": -99.98},
            {"name": "product", "energy_hartree": -100.03},
        ]
    )
    assert len(result["profile"]) == 4
    assert result["barriers"][0]["ts_name"] == "TS"
    assert result["reaction_energy_kcal_mol"] < 0


def test_integration_source_map_endpoint() -> None:
    response = client.get("/api/integration/source-map")
    assert response.status_code == 200
    assert "根工作目录" in response.json()["status"]
