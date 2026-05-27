from __future__ import annotations

from typing import Any

from app.services.chemistry import describe_molecule, xyz_from_smiles


def analyze_molecule_intelligence(smiles: str) -> dict[str, Any]:
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        from rdkit.Chem import AllChem
    except Exception:
        return {
            "descriptors": describe_molecule(smiles),
            "sites": _fallback_sites(smiles),
            "graph": _fallback_graph(smiles),
            "xyz": "0\nRDKit 不可用；未生成 XYZ\n",
            "provenance": "RDKit 不可用，返回字符串规则识别结果。",
        }

    RDLogger.DisableLog("rdApp.*")
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        return {
            "error": "SMILES 无效。",
            "descriptors": describe_molecule(smiles),
            "sites": _fallback_sites(smiles),
            "graph": _fallback_graph(smiles),
            "xyz": "",
            "provenance": "无法解析 SMILES，未生成真实图结构。",
        }

    with_h = Chem.AddHs(molecule)
    try:
        AllChem.EmbedMolecule(with_h, AllChem.ETKDG())
        AllChem.UFFOptimizeMolecule(with_h, maxIters=250)
    except Exception:
        pass

    return {
        "descriptors": describe_molecule(smiles),
        "sites": _identify_sites(molecule),
        "graph": _molecular_graph(molecule),
        "xyz": xyz_from_smiles(smiles),
        "provenance": "分子位点识别合并自 Si-O 子项目并适配根项目；RDKit 构象不是量子化学优化结构。",
    }


def _identify_sites(molecule: Any) -> list[dict[str, Any]]:
    from rdkit import Chem

    sites: list[dict[str, Any]] = []
    for atom in molecule.GetAtoms():
        symbol = atom.GetSymbol()
        index = atom.GetIdx()
        if symbol == "Si":
            sites.append({"atom_index": index, "element": symbol, "label": "Si 活性中心", "type": "Core"})
        if symbol == "O":
            neighbors = [neighbor.GetSymbol() for neighbor in atom.GetNeighbors()]
            if "Si" in neighbors and "C" in neighbors:
                sites.append({"atom_index": index, "element": symbol, "label": "OMe 氧 Lewis 给体", "type": "LewisDonor"})
        if symbol == "Cl":
            neighbors = [neighbor.GetSymbol() for neighbor in atom.GetNeighbors()]
            if "Si" in neighbors:
                sites.append({"atom_index": index, "element": symbol, "label": "Si–Cl 助剂导向位点", "type": "LewisDonor"})
        if symbol == "Al":
            sites.append({"atom_index": index, "element": symbol, "label": "TEA Al Lewis 酸中心", "type": "LewisAcid"})
        if symbol == "Ti":
            sites.append({"atom_index": index, "element": symbol, "label": "Ti 活性中心", "type": "CatalystActiveSite"})
        if symbol == "C":
            for bond in atom.GetBonds():
                if bond.GetBondType() == Chem.rdchem.BondType.DOUBLE:
                    sites.append({"atom_index": index, "element": symbol, "label": "C=C 生产性配位碳", "type": "ProductivePiSite"})
                    break
    return sites


def _molecular_graph(molecule: Any) -> dict[str, Any]:
    return {
        "nodes": [
            {
                "id": atom.GetIdx(),
                "element": atom.GetSymbol(),
                "atomic_number": atom.GetAtomicNum(),
                "degree": atom.GetDegree(),
            }
            for atom in molecule.GetAtoms()
        ],
        "edges": [
            {
                "source": bond.GetBeginAtomIdx(),
                "target": bond.GetEndAtomIdx(),
                "bond_type": str(bond.GetBondType()),
            }
            for bond in molecule.GetBonds()
        ],
    }


def _fallback_sites(smiles: str) -> list[dict[str, Any]]:
    sites: list[dict[str, Any]] = []
    if "Si" in smiles or "[Si" in smiles:
        sites.append({"atom_index": None, "element": "Si", "label": "Si 活性中心", "type": "Core"})
    if "OC" in smiles:
        sites.append({"atom_index": None, "element": "O", "label": "OMe 氧 Lewis 给体", "type": "LewisDonor"})
    if "Cl" in smiles:
        sites.append({"atom_index": None, "element": "Cl", "label": "Si–Cl 助剂导向位点", "type": "LewisDonor"})
    if "C=C" in smiles:
        sites.append({"atom_index": None, "element": "C", "label": "C=C 生产性配位碳", "type": "ProductivePiSite"})
    if "[Al" in smiles:
        sites.append({"atom_index": None, "element": "Al", "label": "TEA Al Lewis 酸中心", "type": "LewisAcid"})
    if "Ti" in smiles:
        sites.append({"atom_index": None, "element": "Ti", "label": "Ti 活性中心", "type": "CatalystActiveSite"})
    return sites


def _fallback_graph(smiles: str) -> dict[str, Any]:
    return {
        "nodes": [{"id": index, "element": char} for index, char in enumerate(smiles) if char.isalpha()],
        "edges": [],
        "note": "RDKit 不可用，未构建真实分子图。",
    }
