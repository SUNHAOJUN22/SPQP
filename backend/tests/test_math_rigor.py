from __future__ import annotations

import math

import pytest

from app.core.constants import DEFAULT_TEMPERATURE_K, HARTREE_TO_EV, HARTREE_TO_KCAL_MOL, R_KCAL_MOL_K
from app.services.energy import (
    delta_g_binding,
    delta_g_poison,
    hartree_to_kcal_mol,
    insertion_profile,
    rate_comparison,
    relative_rate,
)


def test_physical_constants_are_pinned() -> None:
    assert HARTREE_TO_KCAL_MOL == 627.509474
    assert HARTREE_TO_EV == 27.211386245988
    assert R_KCAL_MOL_K == 0.00198720425864083
    assert DEFAULT_TEMPERATURE_K == 350.0


def test_free_energy_formulae_are_consistent() -> None:
    delta_hartree, delta_kcal = delta_g_binding(-150.025, [-100.0, -50.0])
    assert math.isclose(delta_hartree, -0.025, abs_tol=1e-12)
    assert math.isclose(delta_kcal, -0.025 * HARTREE_TO_KCAL_MOL, abs_tol=1e-9)

    poison_delta, _, _ = delta_g_poison(-100.000, -100.010)
    assert math.isclose(poison_delta, 0.010 * HARTREE_TO_KCAL_MOL, abs_tol=1e-9)

    profile = insertion_profile(
        free_site_monomer_g_hartree=-500.000,
        pi_complex_g_hartree=-500.012,
        ts_g_hartree=-499.982,
        product_g_hartree=-500.040,
        reference_barrier_kcal_mol=10.0,
    )
    assert math.isclose(profile.delta_g_pi_kcal_mol, hartree_to_kcal_mol(-0.012), abs_tol=1e-9)
    assert math.isclose(profile.delta_g_barrier_kcal_mol, hartree_to_kcal_mol(0.018), abs_tol=1e-9)
    assert math.isclose(profile.delta_g_complex_barrier_kcal_mol, hartree_to_kcal_mol(0.030), abs_tol=1e-9)
    assert math.isclose(profile.delta_g_product_kcal_mol or 0.0, hartree_to_kcal_mol(-0.040), abs_tol=1e-9)
    assert profile.delta_delta_g_barrier_kcal_mol == pytest.approx(profile.delta_g_barrier_kcal_mol - 10.0)


def test_relative_rate_sign_temperature_and_extreme_bounds() -> None:
    assert relative_rate(0.0) == pytest.approx(1.0)
    assert relative_rate(3.0) < 1.0
    assert relative_rate(-3.0) > 1.0

    low_temperature = relative_rate(5.0, 300.0)
    high_temperature = relative_rate(5.0, 600.0)
    assert high_temperature > low_temperature
    assert high_temperature < 1.0

    very_fast = relative_rate(-1_000_000.0, 350.0)
    very_slow = relative_rate(1_000_000.0, 350.0)
    assert math.isfinite(very_fast)
    assert very_fast > 0
    assert very_slow == pytest.approx(math.exp(-50.0), rel=1e-5)

    with pytest.raises(ValueError, match="temperature_k 必须为正数"):
        relative_rate(1.0, 0.0)


def test_rate_comparison_reference_and_chinese_error() -> None:
    rates = rate_comparison({"DCS": 10.0, "MCSOMe": 13.0, "fast": 8.0}, "DCS")
    assert rates["DCS"]["krel"] == pytest.approx(1.0)
    assert rates["MCSOMe"]["krel"] < 1.0
    assert rates["fast"]["krel"] > 1.0

    with pytest.raises(ValueError, match="reference_key 必须存在"):
        rate_comparison({"DCS": 10.0}, "DMOS")
