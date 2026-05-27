from __future__ import annotations

from textwrap import dedent

from app.schemas.api import GaussianInputRequest, GaussianInputResponse


DEFAULT_COORDINATES = """C     0.000000    0.000000    0.000000
C     1.337000    0.000000    0.000000
H    -0.540000    0.935000    0.000000
H    -0.540000   -0.935000    0.000000
H     1.877000    0.935000    0.000000
H     1.877000   -0.935000    0.000000"""


TASK_ALIASES = {
    "isolated monomer opt/freq/NBO": "isolated",
    "monomer single point refinement": "single_point",
    "29Si GIAO NMR": "nmr",
    "TEA complex counterpoise": "tea_complex",
    "productive C=C π-complex": "pi_complex",
    "productive C=C pi-complex": "pi_complex",
    "nonproductive O→Ti poison complex": "o_ti_complex",
    "nonproductive O-to-Ti poison complex": "o_ti_complex",
    "insertion TS": "insertion_ts",
    "IRC from TS": "irc",
    "hydrolysis TS": "hydrolysis_ts",
    "condensation TS": "condensation_ts",
    "fragment distortion single point": "fragment_distortion",
}


def route_line(req: GaussianInputRequest, route: str) -> str:
    method_basis = f"{req.method}/{req.basis}"
    dispersion = f" EmpiricalDispersion={req.dispersion}" if req.dispersion else ""
    return f"#P {method_basis}{dispersion} {route}"


def _header(req: GaussianInputRequest, chk_suffix: str, nproc: int | None = None, memory: str | None = None) -> str:
    chk = req.checkpoint_name or f"{req.name}_{chk_suffix}.chk"
    return f"%NProcShared={nproc or req.nproc}\n%Mem={memory or req.memory}\n%Chk={chk}"


def _coords(req: GaussianInputRequest) -> str:
    return req.coordinates.strip() or DEFAULT_COORDINATES


def generate_gaussian_input(req: GaussianInputRequest) -> GaussianInputResponse:
    kind = TASK_ALIASES.get(req.job_type, "isolated")
    warnings: list[str] = []
    if not req.coordinates.strip() and kind != "irc":
        warnings.append("未提供坐标；已插入示例坐标，正式计算前必须替换。")

    title = req.title or f"{req.name} {req.job_type}"
    if kind == "isolated":
        content = f"""{_header(req, "opt", 16, "48GB")}
{route_line(req, "SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm")}

{title}

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "single_point":
        content = f"""{_header(req, "sp")}
{route_line(req, "SCF=(XQC,MaxCycle=512) Pop=(NBO,Full) NoSymm")}

{title}

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "nmr":
        content = f"""{_header(req, "29Si_GIAO")}
{route_line(req, "SCF=(XQC,MaxCycle=512) NMR=GIAO NoSymm")}

{title}

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "tea_complex":
        fragments = req.fragment_coordinates.strip() if req.fragment_coordinates else _coords(req)
        if not req.fragment_coordinates:
            warnings.append("Counterpoise 正式计算需要在坐标中提供片段编号。")
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "96GB"}
%Chk={req.checkpoint_name or f"{req.name}_TEA_CP.chk"}
{route_line(req, "Counterpoise=2 SCF=(XQC,MaxCycle=512) Opt=(CalcFC,MaxCycles=300) Freq Pop=(NBO,Full) NoSymm")}

{req.name} TEA complex. Fragment 1 = monomer, fragment 2 = TEA.

{req.charge} {req.multiplicity} {req.charge} {req.multiplicity} 0 1
{fragments}

"""
    elif kind == "pi_complex":
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "128GB"}
%Chk={req.checkpoint_name or f"{req.name}_pi_complex.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm")}

{req.name} productive C=C pi-complex

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "o_ti_complex":
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "128GB"}
%Chk={req.checkpoint_name or f"{req.name}_O_Ti_complex.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) Guess=Mix Stable=Opt Opt=(CalcFC,MaxCycles=300) Freq NoSymm")}

{req.name} nonproductive O-to-Ti complex

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "insertion_ts":
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "128GB"}
%Chk={req.checkpoint_name or f"{req.name}_insert_TS.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) Guess=Mix Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm")}

{req.name} insertion TS

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "irc":
        ts_chk = req.ts_chk or f"{req.name}_insert_TS.chk"
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "128GB"}
%OldChk={ts_chk}
%Chk={req.checkpoint_name or f"{req.name}_IRC.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) Geom=Check Guess=Read IRC=(CalcFC,MaxPoints=100,Stepsize=8,Forward,Reverse) NoSymm")}

IRC from insertion TS

{req.charge} {req.multiplicity}

"""
    elif kind in {"hydrolysis_ts", "condensation_ts"}:
        label = "hydrolysis TS" if kind == "hydrolysis_ts" else "condensation TS"
        content = f"""%NProcShared={req.nproc or 32}
%Mem={req.memory or "128GB"}
%Chk={req.checkpoint_name or f"{req.name}_{kind}.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) Opt=(TS,CalcFC,NoEigenTest,MaxCycles=300) Freq NoSymm")}

{req.name} {label}

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    elif kind == "fragment_distortion":
        content = f"""%NProcShared={req.nproc}
%Mem={req.memory}
%Chk={req.checkpoint_name or f"{req.name}_distortion_sp.chk"}
{route_line(req, "SCF=(XQC,MaxCycle=512) NoSymm")}

{req.name} fragment distortion single point

{req.charge} {req.multiplicity}
{_coords(req)}

"""
    else:
        content = ""

    if req.job_notes:
        content = content.rstrip() + f"\n\n! Notes: {req.job_notes}\n"

    return GaussianInputResponse(
        file_name=f"{req.name}_{kind}.gjf",
        content=dedent(content).lstrip(),
        job_type=req.job_type,
        warnings=warnings,
    )
