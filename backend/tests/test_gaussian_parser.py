from app.services.gaussian_parser import parse_gaussian_log_text


SAMPLE_LOG = """
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
 Mulliken atomic spin densities:
      1  Si   0.112
      2  O   -0.044
 Sum of Mulliken spin densities =   0.06800
 Counterpoise corrected energy = -682.150000
 Normal termination of Gaussian 16 at Tue Apr 28 12:00:00 2026.
"""


def test_parser_extracts_core_fields() -> None:
    parsed = parse_gaussian_log_text(SAMPLE_LOG, "sample.log")
    assert parsed.file == "sample.log"
    assert parsed.normal_termination.value is True
    assert parsed.scf_hartree.value == -682.123456789
    assert parsed.gibbs_hartree.value == -682.032223
    assert parsed.n_imag.value == 1
    assert parsed.lowest_freq_cm_1.value == -321.45
    assert parsed.homo_hartree.value == -0.25
    assert parsed.lumo_hartree.value == 0.03
    assert parsed.gap_ev.value > 7.6
    assert parsed.dipole_debye.value == 0.3742
    assert parsed.counterpoise_corrected_energy_hartree.value == -682.15
    assert parsed.mulliken_charges.value[1]["element"] == "O"
    assert parsed.spin_multiplicity.value == 2
    assert parsed.mulliken_spin_densities.value[0]["spin_density"] == 0.112
    assert parsed.quality == "complete"


def test_parser_failed_log_does_not_fabricate_values() -> None:
    parsed = parse_gaussian_log_text("Error termination without useful fields", "bad.log")
    assert parsed.quality == "failed"
    assert parsed.scf_hartree.value is None
    assert parsed.gibbs_hartree.value is None
    assert parsed.n_imag.value is None


def test_parser_extracts_npa_wiberg_and_nbo_terms() -> None:
    log = SAMPLE_LOG + """
 Summary of Natural Population Analysis:
  Natural Population                 Natural Charge
  Si    1    1.42000
  O     2   -0.82000

 Wiberg bond index matrix in the NAO basis:
  Atom 1  Atom 2  0.742

 Second Order Perturbation Theory Analysis of Fock Matrix in NBO Basis
     12. LP (   1) O  2              / 48. RY*(   1) Al  9             14.25    0.78    0.041
     13. BD (   2) C  3 - C  4       / 51. LP*(   1) Ti 10             18.50    0.55    0.036
 Natural Bond Orbitals (Summary):
"""
    parsed = parse_gaussian_log_text(log, "nbo.log")
    assert parsed.npa_charges.value[1]["charge"] == -0.82
    assert parsed.wiberg_bond_indices.value is not None
    interactions = parsed.nbo_interactions.value
    assert interactions[0]["e2_kcal_mol"] == 14.25
    assert "LP" in interactions[0]["donor"]
    assert "Al" in interactions[0]["acceptor"]
    assert parsed.chinese_warnings == []
