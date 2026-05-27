from __future__ import annotations

from math import pi
from typing import Any


def _fallback_descriptors(smiles: str) -> dict[str, Any]:
    atom_tokens = []
    i = 0
    while i < len(smiles):
        char = smiles[i]
        if char.isalpha():
            if i + 1 < len(smiles) and smiles[i + 1].islower():
                atom_tokens.append(smiles[i : i + 2])
                i += 2
                continue
            atom_tokens.append(char)
        i += 1
    heavy = [token for token in atom_tokens if token != "H"]
    o_count = sum(token == "O" for token in heavy)
    cl_count = sum(token == "Cl" for token in heavy)
    si_count = sum(token == "Si" for token in heavy)
    polar_site_count = o_count + cl_count + smiles.count("[Al]") + smiles.count("[Ti]")
    return {
        "source": "由 SMILES 字符串估算；生产级描述符建议安装 RDKit",
        "molecular_weight": None,
        "atom_count": len(atom_tokens),
        "heavy_atom_count": len(heavy),
        "rotatable_bonds": max(smiles.count("C") - 3, 0),
        "approx_vdw_volume_angstrom3": round(len(heavy) * 17.5 + o_count * 3.5 + cl_count * 9.0 + si_count * 15.0, 2),
        "si_centered_radius_angstrom": round((max(len(heavy), 1) * 17.5 * 3 / (4 * pi)) ** (1 / 3), 2),
        "o_count": o_count,
        "cl_count": cl_count,
        "polar_site_count": polar_site_count,
        "recognized_sites": recognize_sites(smiles),
    }


def describe_molecule(smiles: str) -> dict[str, Any]:
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
    except Exception:
        return _fallback_descriptors(smiles)

    RDLogger.DisableLog("rdApp.*")
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        return _fallback_descriptors(smiles)

    with_h = Chem.AddHs(molecule)
    try:
        AllChem.EmbedMolecule(with_h, randomSeed=42)
        AllChem.UFFOptimizeMolecule(with_h, maxIters=200)
    except Exception:
        pass

    heavy_atom_count = molecule.GetNumHeavyAtoms()
    atom_count = with_h.GetNumAtoms()
    o_count = sum(1 for atom in molecule.GetAtoms() if atom.GetSymbol() == "O")
    cl_count = sum(1 for atom in molecule.GetAtoms() if atom.GetSymbol() == "Cl")
    si_atom_indices = [atom.GetIdx() for atom in molecule.GetAtoms() if atom.GetSymbol() == "Si"]
    volume = heavy_atom_count * 17.5 + o_count * 3.5 + cl_count * 9.0 + len(si_atom_indices) * 15.0
    return {
        "source": "RDKit 计算描述符；构象为局部估计，不是量子化学结果",
        "molecular_weight": round(float(Descriptors.MolWt(molecule)), 4),
        "atom_count": atom_count,
        "heavy_atom_count": heavy_atom_count,
        "rotatable_bonds": int(rdMolDescriptors.CalcNumRotatableBonds(molecule)),
        "approx_vdw_volume_angstrom3": round(volume, 2),
        "si_centered_radius_angstrom": round((max(volume, 1.0) * 3 / (4 * pi)) ** (1 / 3), 2),
        "o_count": o_count,
        "cl_count": cl_count,
        "polar_site_count": o_count + cl_count + sum(1 for atom in molecule.GetAtoms() if atom.GetSymbol() in {"Al", "Ti"}),
        "recognized_sites": recognize_sites(smiles),
    }


def recognize_sites(smiles: str) -> dict[str, Any]:
    return {
        "si_atom": "Si" in smiles or "[Si" in smiles,
        "ome_oxygen_count": smiles.count("OC") + smiles.count("(OC)"),
        "chlorine_atoms": smiles.count("Cl"),
        "alkene_c_alpha_c_beta": "present" if "C=C" in smiles else None,
        "tea_al": "[Al]" in smiles,
        "active_ti": "[Ti" in smiles or "Ti" in smiles,
    }


def xyz_from_smiles(smiles: str) -> str:
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        from rdkit.Chem import AllChem
    except Exception:
        return "0\nRDKit 不可用；未生成 XYZ\n"
    RDLogger.DisableLog("rdApp.*")
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    if mol is None:
        return "0\nSMILES 无效\n"
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.UFFOptimizeMolecule(mol, maxIters=250)
    conf = mol.GetConformer()
    lines = [str(mol.GetNumAtoms()), "由 RDKit 生成；不是量子化学优化结构"]
    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        lines.append(f"{atom.GetSymbol():2s} {pos.x: .6f} {pos.y: .6f} {pos.z: .6f}")
    return "\n".join(lines)
