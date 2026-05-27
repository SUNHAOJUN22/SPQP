"""Gaussian Input (.gjf) Builder for SiO Catalyst Quantum Studio Pro Max.

Covers all 36 task types from the specification:
  A. Monomer & Bond (7 tasks)
  B. Catalyst & Co-catalyst (7 tasks)
  C. Insertion Reaction (6 tasks)
  D. Post-reaction (4 tasks)
  E. Radical (7 tasks)
  F. Visualization (5 tasks)
"""

from typing import List, Optional, Dict, Any

class GaussianBuilder:
    """Generates Gaussian input files for various catalytic and radical states."""

    TASK_TEMPLATES: Dict[str, Dict[str, Any]] = {
        # === A. Monomer & Bond ===
        "monomer_opt": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm",
            "title": "Isolated Monomer Opt/Freq/NBO",
            "group": "A", "mem": "96GB", "nproc": 32, "charge": 0, "mult": 1,
        },
        "monomer_sp": {
            "keywords": "#P M062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Pop=(NBO,Full) NoSymm",
            "title": "Monomer High-Level Single Point",
            "group": "A", "mem": "96GB", "nproc": 32,
        },
        "si_nmr": {
            "keywords": "#P B3LYP/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) NMR=GIAO Pop=Full NoSymm",
            "title": "29Si GIAO NMR Calculation",
            "group": "A", "mem": "96GB", "nproc": 32,
        },
        "sio_bde": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Si-O Bond Dissociation Energy",
            "group": "A", "mem": "96GB", "nproc": 32,
        },
        "sic_bde": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Si-C Bond Dissociation Energy",
            "group": "A", "mem": "96GB", "nproc": 32,
        },
        "si_cl_hydrolysis": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Si-Cl Hydrolysis Model",
            "group": "A", "mem": "96GB", "nproc": 32,
        },
        "si_ome_hydrolysis": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Si-OMe Hydrolysis Model",
            "group": "A", "mem": "96GB", "nproc": 32,
        },

        # === B. Catalyst & Co-catalyst ===
        "tea_cp": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ Counterpoise=2 SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm",
            "title": "TEA Complex Counterpoise",
            "group": "B", "mem": "96GB", "nproc": 32,
        },
        "al_o_complex": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm",
            "title": "Al<-O Complex Optimization",
            "group": "B", "mem": "96GB", "nproc": 32,
        },
        "al_cl_complex": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Al...Cl Complex Optimization",
            "group": "B", "mem": "96GB", "nproc": 32,
        },
        "al_cc_complex": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Al...C=C Complex Optimization",
            "group": "B", "mem": "96GB", "nproc": 32,
        },
        "ti_pi_complex": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Ti Productive C=C pi-Complex",
            "group": "B", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "oti_poison": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "O->Ti Nonproductive Poison Complex",
            "group": "B", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "folded_pi_o": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Folded pi+O Bifunctional Complex",
            "group": "B", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },

        # === C. Insertion Reaction ===
        "insert_ts": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "Insertion Transition State",
            "group": "C", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "insert_irc": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix IRC=(Forward,Reverse,MaxPoints=20,StepSize=10) NoSymm",
            "title": "Insertion IRC Validation",
            "group": "C", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "product_opt": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Insertion Product Optimization",
            "group": "C", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "distortion_sp": {
            "keywords": "#P UPBE1PBE/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) NoSymm",
            "title": "Fragment Distortion Single Point",
            "group": "C", "mem": "128GB", "nproc": 32,
        },
        "seq_silane_after_hex": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "Sequence Insertion: Silane after 1-Hexene",
            "group": "C", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "seq_hex_after_silane": {
            "keywords": "#P UPBE1PBE/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "Sequence Insertion: 1-Hexene after Silane",
            "group": "C", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },

        # === D. Post-reaction ===
        "hydrolysis_ts": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "Si-Cl/Si-OMe Hydrolysis TS",
            "group": "D", "mem": "96GB", "nproc": 32,
        },
        "condensation_ts": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "Si-OH Condensation TS (Si-O-Si Formation)",
            "group": "D", "mem": "96GB", "nproc": 32,
        },
        "sio_si_bridge": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Si-O-Si Bridge Model Optimization",
            "group": "D", "mem": "96GB", "nproc": 32,
        },
        "hcl_elim": {
            "keywords": "#P B3LYP/Def2SVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "HCl / MeOH Elimination Model",
            "group": "D", "mem": "96GB", "nproc": 32,
        },

        # === E. Radical ===
        "perox_homolysis": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Peroxide RO-OR Homolysis",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 1,
        },
        "h_abstract": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "RO. H-Abstraction from PP-H TS",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "pp_beta_ts": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "PP Radical beta-Scission TS",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "pp_recomb": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "PP Radical Recombination Model",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 1,
        },
        "pp_coagent_graft": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "PP Radical + Coagent Grafting TS",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "pp_silane_reaction": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm",
            "title": "PP Radical + Silane Side-chain Reaction TS",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },
        "oxidation_side": {
            "keywords": "#P UM062X/Def2TZVP EmpiricalDispersion=GD3BJ SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(CalcFC,MaxCycles=300) Freq NoSymm",
            "title": "Oxidation Side Reaction Model",
            "group": "E", "mem": "128GB", "nproc": 32, "charge": 0, "mult": 2,
        },

        # === F. Visualization ===
        "formchk": {
            "keywords": "formchk {name}.chk {name}.fchk",
            "title": "FormChk Command",
            "group": "F", "is_utility": True,
        },
        "cubegen_dens": {
            "keywords": "cubegen 0 density=SCF {name}.fchk {name}_density.cube -3 h",
            "title": "Cubegen Electron Density",
            "group": "F", "is_utility": True,
        },
        "cubegen_esp": {
            "keywords": "cubegen 0 potential=SCF {name}.fchk {name}_esp.cube -3 h",
            "title": "Cubegen ESP",
            "group": "F", "is_utility": True,
        },
        "cubegen_homo_lumo": {
            "keywords": "cubegen 0 MO={homo_idx} {name}.fchk {name}_HOMO.cube -3 h\ncubegen 0 MO={lumo_idx} {name}.fchk {name}_LUMO.cube -3 h",
            "title": "Cubegen HOMO/LUMO",
            "group": "F", "is_utility": True,
        },
        "multiwfn_script": {
            "keywords": "# Multiwfn batch script placeholder\n# Load: {name}.fchk\n# 2  -> Topology analysis\n# 12 -> QTAIM analysis\n# 20 -> NCI analysis",
            "title": "Multiwfn Script Generation",
            "group": "F", "is_utility": True,
        },
    }

    @staticmethod
    def generate_gjf(
        title: str,
        method: str = "B3LYP",
        basis: str = "def2-TZVP",
        extra_keywords: str = "opt freq em=GD3BJ",
        charge: int = 0,
        multiplicity: int = 1,
        coordinates: List[str] = None,
        nbo: bool = False,
        scrf: Optional[str] = None,
        mem: str = "48GB",
        nproc: int = 24,
    ) -> str:
        keywords = f"# {method}/{basis} {extra_keywords}"
        if nbo and "pop=nbo" not in keywords.lower():
            keywords += " pop=nbo7"
        if scrf:
            keywords += f" scrf=({scrf})"
        
        lines = [
            f"%mem={mem}",
            f"%nprocshared={nproc}",
            f"%chk={title.replace(' ', '_').replace(':', '')}.chk",
            keywords,
            "",
            title,
            "",
            f"{charge} {multiplicity}"
        ]
        
        if coordinates:
            lines.extend(coordinates)
        else:
            lines.append("! [Insert Coordinates Here]")
            
        lines.append("")
        if "nbo" in keywords.lower():
            lines.append("$NBO BNDIDX $END")
            lines.append("")
        
        return "\n".join(lines)

    @classmethod
    def build_task(cls, task_id: str, molecule_name: str, coordinates: List[str] = None, **kwargs) -> str:
        """Build a GJF from a predefined task ID."""
        template = cls.TASK_TEMPLATES.get(task_id, {"keywords": "opt freq", "title": "Custom Task"})
        
        # For utility commands, return command directly
        if template.get("is_utility"):
            return template["keywords"].replace("{name}", molecule_name)
        
        method = kwargs.get("method", "B3LYP")
        basis = kwargs.get("basis", "def2-TZVP")
        charge = kwargs.get("charge", template.get("charge", 0))
        multiplicity = kwargs.get("multiplicity", template.get("mult", 1))
        mem = kwargs.get("mem", template.get("mem", "48GB"))
        nproc = kwargs.get("nproc", template.get("nproc", 24))
        
        # Use template route section directly if it contains #P
        if template["keywords"].startswith("#"):
            full_title = f"{template['title']}: {molecule_name}"
            lines = [
                f"%mem={mem}",
                f"%nprocshared={nproc}",
                f"%chk={molecule_name}_{task_id}.chk",
                template["keywords"],
                "",
                full_title,
                "",
                f"{charge} {multiplicity}",
            ]
            if coordinates:
                lines.extend(coordinates)
            else:
                lines.append("! [Insert Coordinates Here]")
            lines.append("")
            if "nbo" in template["keywords"].lower():
                lines.append("$NBO BNDIDX $END")
                lines.append("")
            return "\n".join(lines)
        
        return cls.generate_gjf(
            title=f"{template['title']}: {molecule_name}",
            method=method,
            basis=basis,
            extra_keywords=template["keywords"] + " em=GD3BJ",
            charge=charge,
            multiplicity=multiplicity,
            coordinates=coordinates,
            mem=mem,
            nproc=nproc,
        )

    # Legacy method support
    @classmethod
    def monomer_template(cls, molecule_name: str, coordinates: List[str] = None) -> str:
        return cls.build_task("monomer_opt", molecule_name, coordinates)

    @classmethod
    def transition_state_template(cls, molecule_name: str, coordinates: List[str] = None) -> str:
        return cls.build_task("insert_ts", molecule_name, coordinates)

    @classmethod
    def get_task_groups(cls) -> Dict[str, List[Dict[str, str]]]:
        """Return tasks organized by group for UI rendering."""
        groups: Dict[str, List[Dict[str, str]]] = {
            "A": [], "B": [], "C": [], "D": [], "E": [], "F": []
        }
        for tid, tmpl in cls.TASK_TEMPLATES.items():
            g = tmpl.get("group", "A")
            groups[g].append({"id": tid, "title": tmpl["title"]})
        return groups
