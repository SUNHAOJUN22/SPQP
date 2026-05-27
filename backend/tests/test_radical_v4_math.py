import pytest
import math
from app.services.radical_v4 import peroxide_profile, radical_branching_vs_scission, _clamp, _bounded

def test_peroxide_profile_extreme_half_life():
    # 极端小半衰期（如负值或趋于零），测试被 max(float(half_life_min), 1e-12) 拦截不报除零错误
    data = {
        "half_life_min": 0.0,
        "residence_time_min": 5.0
    }
    result = peroxide_profile(data)
    # 应 fallback 回保护的 1e-12 半衰期，因此完全分解 (100%)
    assert "conversion_percent" in result
    assert result["conversion_percent"] == 100.0

def test_radical_branching_vs_scission_extreme_residence():
    # 极端长停留时间，测试 math.exp(_clamp) 防止溢出
    data = {
        "residence_time_min": 999999.0
    }
    result = radical_branching_vs_scission(data)
    assert "fractions" in result
    assert "beta_scission" in result["fractions"]
    # _clamp 防止溢出，应平稳计算并得出数值，而不是 NaN
    assert not math.isnan(result["fractions"]["beta_scission"])
    assert result["fractions"]["beta_scission"] >= 0

def test_radical_branching_vs_scission_negative_values():
    # 极端负参数，测试边界截断
    data = {
        "oxygen_level_percent": -100.0,
        "coagent_phr": -50.0,
        "temperature_c": -273.15,
        "crystallinity_percent": -999.0
    }
    result = radical_branching_vs_scission(data)
    assert "dominant_path" in result
    assert not math.isnan(result["fractions"]["beta_scission"])
    
def test_clamp_and_bounded():
    assert _clamp(1e9) == 50.0
    assert _clamp(-1e9) == -50.0
    assert math.isnan(_clamp(float("inf"))) == False # isfinite falls back to max
    assert _bounded(1e9) == 100.0
    assert _bounded(-1e9) == 0.0
