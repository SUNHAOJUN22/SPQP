# 🧪 Testing Strategy: SiO Catalyst Quantum Studio Pro

## 1. Multi-Tier Testing Architecture
- **Unit (L1)**: Pure function verification (Physics, Math, Parsers).
- **Integration (L2)**: Hook-State-UI interaction (Zustand + React).
- **Scientific (L3)**: Thermodynamic & Kinetic validity (NIST Golden Cases).
- **E2E (L4)**: Full workflow simulation (Gaussian -> Parser -> Dashboard).

## 2. Methodology
- **Numerical Stability**: Every division is protected by `EPSILON`.
- **Property-based**: Verification of conservation laws (Mass/Atom/Charge).
- **Metamorphic**: Checking unit consistency across scales.

## 3. Tooling
- Frontend: Vitest + Testing Library.
- Science: Python `test_science.py`.
- Arbiter: `quality-gate.py`.
