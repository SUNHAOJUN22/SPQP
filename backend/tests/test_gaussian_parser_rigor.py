from __future__ import annotations

import pytest

from app.core.constants import HARTREE_TO_EV
from app.services.gaussian_parser import parse_gaussian_log_text


COMPLETE_LOG = """
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
     13. BD (   2) C  3 - C  4       / 51. LP*(   1) Ti 10             18.50    0.55    0.036
 Natural Bond Orbitals (Summary):
 Counterpoise corrected energy = -682.150000
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
"""


PARTIAL_LOG = """
 SCF Done:  E(RB3LYP) =  -100.000000     A.U. after   5 cycles
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
"""


def test_complete_parser_extracts_required_fields_and_units() -> None:
    parsed = parse_gaussian_log_text(COMPLETE_LOG, "complete.log")

    assert parsed.quality == "complete"
    assert parsed.normal_termination.value is True
    assert parsed.scf_hartree.value == -682.123456789
    assert parsed.zpe_correction_hartree.value == 0.123456
    assert parsed.thermal_correction_energy_hartree.value == 0.135790
    assert parsed.thermal_correction_enthalpy_hartree.value == 0.136734
    assert parsed.thermal_correction_gibbs_hartree.value == 0.091234
    assert parsed.gibbs_hartree.value == -682.032223
    assert parsed.frequencies_cm_1.value == [-321.45, 45.67, 80.12]
    assert parsed.n_imag.value == 1
    assert parsed.lowest_freq_cm_1.value == -321.45
    assert parsed.homo_hartree.value == -0.25
    assert parsed.lumo_hartree.value == 0.03
    assert parsed.gap_ev.value == pytest.approx((0.03 - (-0.25)) * HARTREE_TO_EV)
    assert parsed.dipole_debye.value == 0.3742
    assert parsed.mulliken_charges.unit == "e"
    assert parsed.mulliken_charges.value[1]["charge"] == -0.678
    assert parsed.npa_charges.value[1]["charge"] == -0.82
    assert parsed.wiberg_bond_indices.value["matrix"][0]["wbi"] == 0.742
    assert parsed.nbo_interactions.unit == "kcal/mol"
    assert parsed.nbo_interactions.value[0]["e2_kcal_mol"] == 14.25
    assert parsed.counterpoise_corrected_energy_hartree.value == -682.15
    assert parsed.units["frequency"] == "cm^-1"
    assert parsed.chinese_warnings == []


def test_partial_parser_marks_missing_fields_without_fabrication() -> None:
    parsed = parse_gaussian_log_text(PARTIAL_LOG, "partial.log")
    assert parsed.quality == "partial"
    assert parsed.normal_termination.value is True
    assert parsed.scf_hartree.value == -100.0
    assert parsed.gibbs_hartree.value is None
    assert parsed.homo_hartree.value is None
    assert parsed.nbo_interactions.value is None
    assert "当前文件中未找到吉布斯自由能。" in parsed.chinese_warnings
    assert "当前文件中未找到 NBO 二阶微扰分析结果。" in parsed.chinese_warnings


def test_failed_or_empty_parser_returns_nulls_and_chinese_warnings() -> None:
    parsed = parse_gaussian_log_text("", "empty.log")
    assert parsed.quality == "failed"
    assert parsed.normal_termination.value is False
    assert parsed.scf_hartree.value is None
    assert parsed.gibbs_hartree.value is None
    assert parsed.frequencies_cm_1.value is None
    assert "未检测到 Gaussian 正常终止标记。" in parsed.chinese_warnings
    assert "当前文件中未找到吉布斯自由能。" in parsed.chinese_warnings
    assert "当前文件中未找到 NBO 二阶微扰分析结果。" in parsed.chinese_warnings
