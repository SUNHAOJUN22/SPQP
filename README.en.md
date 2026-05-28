# SiO-SiC Polyolefin Quantum Mechanism Studio Ultra

[Simplified Chinese](README.md) | [English](README.en.md)

A Chinese-first scientific computing platform for polyolefin functionalization, Ziegler-Natta catalysis, Si-O / Si-C bond physicochemical descriptors, Gaussian post-processing, peroxide radical chemistry, and the competition between polypropylene long-chain branching, crosslinking, and degradation.

## Overview

This project is a full-stack research-software prototype for data import, calculation templates, read-only parsing, mechanistic decision rules, evidence grading, and scientific report generation.

The platform focuses on the following research lines:

- Functional alpha-olefin monomers: DCS, MCSOMe, DMOS, and related Si-Cl, Si-OMe, Si-O, and Si-C structures.
- Coordination insertion mechanisms: Ziegler-Natta active sites, TEA cocatalyst effects, Al-O / Al-Cl / Al-C=C interactions, Ti poisoning, and C=C insertion transition states.
- Post-reaction mechanisms: Si-Cl / Si-OMe hydrolysis, Si-O-Si condensation, and Si-C linker stability.
- Radical post-modification: peroxide RO-OR homolysis, PP tertiary C-H abstraction, beta-scission, radical recombination, grafting, mild crosslinking, over-gelation, and oxidative carbonyl side reactions.
- Experimental closure: connecting GPC, MFR, gel, SAOS, FTIR, NMR, DSC, and dielectric data with DFT descriptors.

The project does not execute external quantum-chemistry or wavefunction-analysis software by default. Gaussian, cubegen, Multiwfn, and GoodVibes integrations are limited to input generation, command templates, text parsing, and report drafts unless explicitly configured and reviewed outside the default workflow.

## Product Scope

Current platform capabilities include:

- Chinese scientific workbench: Google Workspace / Google Cloud style information architecture with grouped navigation, global search, resource tables, right-side detail panels, and report previews.
- Molecule and structure management: built-in DCS, MCSOMe, DMOS, ethylene, propylene, 1-hexene, TEA, PP / EPC small models, and peroxide examples.
- Gaussian input generation: templates for opt/freq/NBO, TEA complexes, Ti pi-complexes, O-to-Ti poison complexes, insertion TS, IRC, hydrolysis, condensation, BDE, and radical pathways.
- Gaussian output parsing: read-only parsing of SCF, Gibbs, ZPE, frequencies, imaginary frequencies, HOMO / LUMO, dipole, charges, Wiberg indices, NBO E(2), and Counterpoise values.
- Cube file parsing: read-only metadata, slices, and downsample previews for density, ESP, HOMO, LUMO, spin density, and difference-density grids.
- Scientific computation core: unit conversion, Delta G formulas, BDE, relative rates, radical competition, and Boltzmann weighting.
- Mechanistic decision engine: Chinese explanations for Ti poisoning, TEA preorganization, Si-O weakening, Si-C risk, PP degradation, LCB, over-gelation, and oxidation risk.
- Literature and report knowledge base: read-only docx, PDF text-layer, or OCR text import with literature clues fixed at evidence grade C.
- Chinese scientific report generation: reports with data sources, evidence grades, missing-data statements, and mock-data boundaries.

## Architecture

The project uses a separated frontend and backend architecture.

```text
frontend/        Next.js, React, TypeScript, TailwindCSS
backend/         FastAPI, Pydantic, SQLAlchemy, SQLite
scripts/         quality gates, smoke tests, parser audits
docs/            scientific workflow, test reports, integration reports
examples/        controlled examples and non-executed external QC templates
integrated/      archived source assets from earlier Si-O subproject integration
```

Layering principles:

- scientific core: centralizes unit constants, energy formulas, BDE, kinetics, and decision rules.
- parsers: read-only parsing for Gaussian, cube, NBO, QTAIM, NCI, and GoodVibes text outputs.
- API: FastAPI endpoints for molecules, Gaussian, cube, analysis, literature, reports, and MCP safety workflows.
- UI: resource tables, workspaces, detail panels, and report previews.
- reports: separate computation, literature, experiment, and example data by provenance and reliability.

## Scientific Rules

Every scientific output must preserve data source, unit, temperature, method, basis set, provenance, evidence grade, and is_mock.

Evidence grades:

- A: Real Gaussian, Multiwfn, NBO, QTAIM, or NCI computation with convergence, frequency, TS imaginary mode, IRC, and provenance checks where applicable.
- B: Real experimental data with explicit sample, process, and characterization conditions.
- C: Literature clues or user input not reproduced in the current system.
- D: Example data, mock data, or mechanistic hypotheses only.

Without grade A or B data, reports must state that the current data is insufficient for reliable conclusions.

## Scientific Formulas

Unit constants:

```text
1 Hartree = 627.509474 kcal/mol
1 Hartree = 2625.499638 kJ/mol
1 Hartree = 27.211386245988 eV
R = 0.00198720425864083 kcal mol^-1 K^-1
Default T = 350 K
```

Coordination and insertion:

```text
Delta Gbind = G(complex) - sum G(fragments)
Delta Gpoison = G(O-to-Ti complex) - G(C=C pi-complex)
Delta Gpi = G(pi-complex) - G(free active site + monomer)
Delta Gddagger_insert = G(insertion TS) - G(free active site + monomer)
Delta Gddagger_complex = G(insertion TS) - G(pi-complex)
Delta Delta Gddagger = Delta Gddagger_candidate - Delta Gddagger_reference
krel = exp[-Delta Delta Gddagger / RT]
```

Bond dissociation and radical competition:

```text
BDE(Si-C) = G(R radical) + G(silyl radical fragment) - G(R-Si)
BDE(Si-O) = G(R radical) + G(O-Si radical fragment) - G(R-O-Si)
BDE(RO-OR) = G(2 RO radical) - G(RO-OR)
R_scission = k_beta [PP radical]
R_branch = k_rec [PP radical]^2 + k_g [PP radical][M] + k_c [PP radical][coagent]
S_LCB = R_branch / (R_branch + R_scission + R_oxidation)
```

## Requirements

Recommended environment:

- Node.js 20 or later
- Python 3.11 or later
- Windows PowerShell, Git Bash, macOS shell, or Linux shell
- SQLite for the local MVP database

Optional dependencies:

- RDKit for molecular descriptors and conformer generation. If unavailable, the backend falls back to clearly marked approximate descriptors.
- PyMuPDF / python-docx for read-only literature extraction.
- Gaussian, cubegen, Multiwfn, and GoodVibes are not executed by default and are treated as template targets unless explicitly configured.

## Installation

Install root and frontend dependencies:

```bash
npm install
npm --prefix frontend install
```

Create the backend virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Return to the project root:

```bash
cd ..
```

## Run

Start the backend:

```bash
npm run dev:backend
```

Start the frontend:

```bash
npm run dev
```

Default endpoints:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs

## Validation

Backend tests:

```bash
npm run test:backend
```

Frontend typecheck, lint, and build:

```bash
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

Chinese mojibake audit:

```bash
npm run audit:mojibake
```

Scientific rigor audit:

```bash
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
```

Full-function API smoke test:

```bash
backend\.venv\Scripts\python.exe scripts\full_function_smoke.py
```

Root quality gate:

```bash
python scripts\quality_gate.py
```

UI smoke tests require the frontend and backend to be running:

```bash
npm run dev:backend
npm run dev
npm run test:e2e
```

## Security Boundary

Forbidden by default:

- Execute Gaussian16.
- Execute cubegen.
- Execute Multiwfn.
- Execute GoodVibes.
- Execute user-uploaded files.
- Upgrade example data, mock data, or literature clues into real scientific conclusions.

Allowed by default:

- Generate Gaussian input files.
- Generate cubegen, Multiwfn, and GoodVibes command templates marked as not executed.
- Read-only parse Gaussian log/out, cube, NBO, QTAIM, NCI, and GoodVibes text outputs.
- Generate Chinese scientific report drafts.
- Evaluate user-provided data through formulas and decision rules.

## Documentation

- [Scientific computation workflow](docs/SCIENTIFIC_COMPUTATION_WORKFLOW.md)
- [Scientific computation full test report](docs/SCIENTIFIC_COMPUTATION_FULL_TEST_REPORT.md)
- [Scientific rigor test report](docs/SCIENTIFIC_RIGOR_TEST_REPORT.md)
- [Scientific calculation test report](docs/SCIENTIFIC_CALCULATION_TEST_REPORT.md)
- [Real instance test report](docs/REAL_INSTANCE_TEST_REPORT.md)
- [UI / UX test report](docs/UI_UX_TEST_REPORT.md)
- [Full function test report](docs/FULL_FUNCTION_TEST_REPORT.md)
- [Pro Max Ultra quality report](docs/ULTRA_QUALITY_TEST_REPORT.md)
- [Mojibake cleanup report](docs/MOJIBAKE_CLEANUP_REPORT.md)
- [External QC run examples](docs/EXTERNAL_QC_RUN_EXAMPLES.md)
- [Si-O integration report](docs/MERGE_REPORT.md)
- [Integration source map](docs/INTEGRATION_SOURCE_MAP.md)

## Repository Status

This repository is a research-software engineering version suitable for local development, scientific demonstrations, mechanistic validation, and further engineering iteration.

Recommended before production deployment:

- Add a formal LICENSE file.
- Add an environment variable template.
- Define a database migration strategy.
- Add user permission and project isolation.
- Expand compatibility tests with larger real Gaussian, cube, NBO, QTAIM, and NCI outputs.
- Add continuous integration workflows.

## Roadmap

- Real 3Dmol / vtk.js cube isosurface rendering.
- Structured Multiwfn import and advanced NBO parsing.
- Expanded GoodVibes real-format samples.
- Batch Gaussian task graphs, SLURM scripts, and task queues.
- Conformer-family Boltzmann weighting, entropy correction, and GoodVibes aggregation.
- Full-section literature extraction and table localization.
- PostgreSQL multi-project collaboration.

## Citation and Use

This repository is intended for research-software development and mechanism-model validation. Trends derived from example data are only for verifying software logic and must not be used as paper conclusions, patent claims, or engineering decisions. Real scientific conclusions require traceable grade A computational data or grade B experimental data plus human review.
