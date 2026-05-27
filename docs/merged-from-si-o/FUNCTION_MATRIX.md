# 📊 SiO Catalyst Quantum Studio Pro: Industrial Function Matrix

This document maps the complete functional landscape of the platform for industrial-grade automated verification.

| ID | Function Name | Module | File Path | Entry Point | Input | Output | UI | API | DB | Upload | Export | Charts | Sci-Calc | Units | Risk | Testing Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| F01 | Gaussian Parser | `gaussian` | `/gaussian/parser/page.tsx` | `GaussianParserContent` | `.log` file | Json Result | Yes | Yes | No | Yes | Yes | No | Yes | Yes | P0 | E2E + Scientific |
| F02 | Kinetics Simulator | `kinetics` | `/kinetics-simulator/page.tsx` | `KineticsSimulatorContent` | T, P, Conc | Rate Plot | Yes | No | No | No | Yes | Yes | Yes | Yes | P0 | Numerical Stability |
| F03 | DOE Optimizer | `doe` | `/doe-optimizer/page.tsx` | `DOEOptimizerContent` | Design Space | Optimal Set | Yes | No | No | No | Yes | Yes | Yes | No | P0 | Bayesian Integration |
| F04 | Thermochem Lab | `thermo` | `/thermochem/page.tsx` | `ThermochemContent` | Frequency Data | G, H, S | Yes | No | No | No | No | No | Yes | Yes | P1 | Partition Function |
| F05 | 29Si NMR | `nmr` | `/nmr-simulator/page.tsx` | `NMRSimulatorContent` | Shielding | Spectrum | Yes | No | No | No | No | Yes | Yes | Yes | P1 | Lorentz Shape |
| F06 | XAS Simulator | `xas` | `/xas-simulator/page.tsx` | `XASSimulatorContent` | Excitation | XANES Plot | Yes | No | No | No | No | Yes | Yes | Yes | P2 | Transition Dipole |
| F07 | Active Discovery | `discovery`| `/active-discovery/page.tsx` | `ActiveDiscoveryContent` | Seed Data | Pareto Point | Yes | Yes | Yes | No | Yes | Yes | Yes | No | P1 | Metamorphic |
| F08 | Decision Engine | `decision` | `/decision-engine/page.tsx` | `DecisionEngineContent` | Criteria Weights | Ranking | Yes | No | No | No | Yes | Yes | No | No | P1 | Weighted Sum |
| F09 | Si-O Lab | `lab` | `/sio-lab/page.tsx` | `SiOLabContent` | Bond Params | Energy | Yes | No | No | No | No | Yes | Yes | Yes | P1 | Morse Potential |
| F10 | Industrial Report| `report` | `/industrial-report/page.tsx` | `IndustrialReportContent` | Workspace State | PDF/Print | Yes | No | No | No | Yes | No | No | No | P0 | Export Integrity |
| U01 | Physics Utils | `utils` | `src/utils/physics.ts` | `CONSTANTS` | - | Values | No | No | No | No | No | No | Yes | Yes | P0 | Unit Consistency |
| U02 | Workspace Store | `store` | `src/store/useWorkspaceStore.ts` | `useWorkspaceStore` | - | State | No | No | No | No | No | No | No | No | P0 | State Persistence |

---
*Legend: P0 (Critical/Safety), P1 (High/Accuracy), P2 (Medium/UI), P3 (Low/UX)*
