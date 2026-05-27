from math import isclose

from app.core.constants import HARTREE_TO_KCAL_MOL
from app.services.energy import delta_g_binding, delta_g_poison, insertion_profile, rate_comparison, relative_rate


def test_delta_g_binding_hartree_to_kcal() -> None:
    delta_hartree, delta_kcal = delta_g_binding(-200.050, [-100.000, -100.000])
    assert isclose(delta_hartree, -0.050, abs_tol=1e-12)
    assert isclose(delta_kcal, -0.050 * HARTREE_TO_KCAL_MOL, abs_tol=1e-9)


def test_poisoning_thresholds() -> None:
    delta, label, color = delta_g_poison(-100.000, -100.020)
    assert delta > 5
    assert label == "生产性 C=C 插入占优"
    assert color == "green"

    delta, label, color = delta_g_poison(-100.020, -100.000)
    assert delta < 0
    assert label == "Ti 活性中心存在甲氧基毒化风险"
    assert color == "red"


def test_insertion_profile_and_relative_rate() -> None:
    profile = insertion_profile(
        free_site_monomer_g_hartree=-500.000,
        pi_complex_g_hartree=-500.010,
        ts_g_hartree=-499.980,
        product_g_hartree=-500.040,
        reference_barrier_kcal_mol=10.0,
        temperature_k=350.0,
    )
    assert profile.delta_g_pi_kcal_mol < 0
    assert profile.delta_g_barrier_kcal_mol > 0
    assert profile.delta_g_complex_barrier_kcal_mol > profile.delta_g_barrier_kcal_mol
    assert profile.krel is not None
    assert profile.krel < 1.0

    rates = rate_comparison({"DCS": 10.0, "MCSOMe": 11.0}, "DCS")
    assert rates["DCS"]["krel"] == 1.0
    assert rates["MCSOMe"]["krel"] == relative_rate(1.0)
