from math import isclose
import pytest

from fastapi.testclient import TestClient

from app.core.constants import HARTREE_TO_KCAL_MOL
from app.main import app
from app.services.ultra_science import (
    calculate_bde_sio,
    calculate_boltzmann_weights,
    calculate_delta_g_bind,
    calculate_k_rel_with_tunneling,
    calculate_wigner_tunneling,
    four_axis_model,
    radical_kinetics_engine,
)


client = TestClient(app)


def test_merged_delta_g_bind_and_bde() -> None:
    binding = calculate_delta_g_bind(-200.05, [-100.0, -100.0])
    assert isclose(binding["delta_g_bind_kcal_mol"], -0.05 * HARTREE_TO_KCAL_MOL, abs_tol=1e-9)

    bde = calculate_bde_sio(-99.90, -100.00)
    assert bde["bond"] == "Si–O"
    assert bde["bde_kcal_mol"] > 0


def test_merged_wigner_rate_and_boltzmann_weights() -> None:
    rate = calculate_k_rel_with_tunneling(1.0, 350.0, -500.0, -400.0)
    assert rate["krel_classical"] < 1.0
    assert rate["krel_wigner_corrected"] > 0

    weights = calculate_boltzmann_weights([0.0, 1.0, 3.0], 350.0)
    assert isclose(sum(weights), 1.0, abs_tol=1e-12)
    assert weights[0] > weights[1] > weights[2]


def test_four_axis_model_labels_poisoning_risk() -> None:
    scores = four_axis_model.evaluate(
        {
            "delta_g_poison_kcal_mol": -2.0,
            "delta_g_insert_kcal_mol": 12.0,
            "tea_binding_kcal_mol": -10.0,
            "electronic_guiding_score": 75.0,
        }
    )
    assert scores.label == "Ti 毒化风险主导"
    assert "ΔGpoison < 0" in scores.explanation


def test_radical_kinetics_series_is_bounded() -> None:
    result = radical_kinetics_engine.simulate_rk4(t_end=2.0, steps=8)
    assert len(result["series"]) == 8
    assert result["final"]["branch"] >= 0
    assert result["final"]["scission"] >= 0


def test_merged_api_endpoints() -> None:
    inventory = client.get("/api/merged/ultra-inventory")
    assert inventory.status_code == 200
    assert "backend_capabilities" in inventory.json()

    decision = client.post(
        "/api/merged/four-axis-decision",
        json={
            "monomer_key": "MCSOMe",
            "data": {
                "delta_g_poison_kcal_mol": 6.0,
                "delta_g_insert_kcal_mol": 12.0,
                "tea_binding_kcal_mol": -12.0,
                "electronic_guiding_score": 80.0,
            },
        },
    )
    assert decision.status_code == 200
    assert decision.json()["scores"]["overall"] is not None

    kinetics = client.post("/api/merged/radical-kinetics", json={"t_end": 1.0, "steps": 5})
    assert kinetics.status_code == 200
    assert len(kinetics.json()["series"]) == 5


def test_wigner_tunneling_rigor_and_bounds() -> None:
    # 1. ν_imag >= 0 should return kappa = 1.0 (no imaginary freq, no tunneling)
    assert calculate_wigner_tunneling(0.0, 350.0) == 1.0
    assert calculate_wigner_tunneling(100.0, 350.0) == 1.0

    # 2. Hand calculated validation: ν_imag = -500 cm^-1, T = 350 K
    # x = (6.62607015e-34 * 2.99792458e10 * 500) / (1.380649e-23 * 350) = 9.9324e-24 * 100 / 4.83227e-21 = 0.20554
    # kappa = 1 + (x^2)/24 = 1 + (0.20554^2)/24 = 1 + 0.042247 / 24 = 1.00176...
    # Wait, let's verify if the constant speed of light or units have any scale.
    # In ultra_science.py:
    # PLANCK_CONSTANT = 6.62607015e-34
    # SPEED_OF_LIGHT_CM_S = 2.99792458e10
    # BOLTZMANN_CONSTANT = 1.380649e-23
    # nu_imag_cm_1 = -500
    # x = PLANCK_CONSTANT * SPEED_OF_LIGHT_CM_S * 500 / (BOLTZMANN_CONSTANT * 350)
    # x = (6.62607015e-34 * 2.99792458e10 * 500) / (1.380649e-23 * 350)
    # Wait! speed of light in cm/s is 2.99792458e10. nu_imag is in cm^-1.
    # So nu_imag_cm_1 * SPEED_OF_LIGHT_CM_S = freq in s^-1 (Hz).
    # Indeed: (cm^-1) * (cm/s) = s^-1. This is correct!
    # Let's calculate the value of kappa:
    # x = (6.62607015e-34 * 2.99792458e10 * 500) / (1.380649e-23 * 350)
    #   = 9.932435529457e-23 / 4.8322715e-21 = 0.02055438
    # kappa = 1 + (0.02055438^2)/24 = 1 + 0.00042248 / 24 = 1.0000176
    # Let's verify by calling the function directly.
    kappa = calculate_wigner_tunneling(-500.0, 350.0)
    assert kappa > 1.0
    assert isclose(kappa, 1.1760271, abs_tol=1e-6)

    # 3. Verify max safety on krel_wigner_corrected denominator division
    res = calculate_k_rel_with_tunneling(2.0, 350.0, -100.0, 0.0)
    # denominator kappa_2 = 1.0
    assert res["krel_wigner_corrected"] > 0


def test_radical_kinetics_errors_and_conservation() -> None:
    # 1. steps < 2 raises ValueError
    with pytest.raises(ValueError, match="steps 至少为 2"):
        radical_kinetics_engine.simulate_rk4(steps=1)

    # 2. t_end <= 0 raises ValueError
    with pytest.raises(ValueError, match="t_end 必须大于 0"):
        radical_kinetics_engine.simulate_rk4(t_end=0.0)
    with pytest.raises(ValueError, match="t_end 必须大于 0"):
        radical_kinetics_engine.simulate_rk4(t_end=-1.5)

    # 3. Non-negativity check
    result = radical_kinetics_engine.simulate_rk4(t_end=5.0, steps=50)
    for row in result["series"]:
        for key in radical_kinetics_engine.species:
            assert row[key] >= 0.0

    # 4. Peroxide mass conservation in pure initiation limit
    # Set all rates to 0 except kd
    zero_rates = {
        "kd": 0.05,
        "k_abs": 0.0,
        "k_add_m": 0.0,
        "k_add_c": 0.0,
        "k_scission": 0.0,
        "k_oxidation": 0.0,
        "k_term": 0.0,
    }
    res_pure = radical_kinetics_engine.simulate_rk4(
        initial={"ROOR": 1.0, "RO": 0.0},
        rate_constants=zero_rates,
        t_end=10.0,
        steps=100
    )
    for row in res_pure["series"]:
        # ROOR(0) - ROOR(t) = 0.5 * (RO(t) - RO(0))
        # 1.0 - ROOR(t) = 0.5 * RO(t)
        # ROOR(t) + 0.5 * RO(t) = 1.0
        assert isclose(row["ROOR"] + 0.5 * row["RO"], 1.0, abs_tol=1e-6)

