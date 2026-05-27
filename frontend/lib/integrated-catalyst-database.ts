/**
 * catalystDatabase.ts
 * ═══════════════════════════════════════════════════════════════
 * Central, type-safe catalyst descriptor database.
 * Every analysis page should read from here via activeMoleculeId.
 * ═══════════════════════════════════════════════════════════════
 */

export interface AtomDescriptor {
  element: string;
  x: number;
  y: number;
  z: number;
  charge?: number;
}

export interface OrbitalLevel {
  name: string;
  energy: number;        // Hartree
  type: "occupied" | "virtual";
}

export interface EnergyPoint {
  name: string;
  energy: number;        // kcal/mol relative
  label: string;
}

export interface ChargeSet {
  atomLabel: string;
  mulliken: number;
  npa: number;
  hirshfeld: number;
}

export interface SolvationShift {
  solventName: string;
  epsilon: number;
  dG_correction: number; // kcal/mol
}

export interface CatalystEntry {
  id: string;
  name: string;
  smiles: string;
  formula: string;
  molecularWeight: number; // g/mol — computed from atomic masses
  atoms: AtomDescriptor[];
  orbitalLevels: OrbitalLevel[];
  gapEv: number;
  energyProfile: EnergyPoint[];
  chargeData: ChargeSet[];
  kineticParams: {
    dG_ins: number;      // kcal/mol — insertion barrier
    dG_poi: number;      // kcal/mol — poisoning barrier
  };
  solvationShifts: SolvationShift[];
  contributionData: { atom: string; value: number }[];
  // ── Phase 19 extensions ──
  dipoleMoment: { x: number; y: number; z: number; magnitude: number }; // Debye
  polarizability: number; // Å³ (isotropic)
}

// ────────────────────────────────────────────────────────────────
// Atomic masses for MW calculation
// Si=28.085, O=15.999, C=12.011, H=1.008, Cl=35.453
// ────────────────────────────────────────────────────────────────

// Atomic polarizabilities (Å³) — Miller & Savchik values
const ATOMIC_ALPHA: Record<string, number> = { Si: 5.38, O: 0.80, Cl: 2.18, C: 1.76, H: 0.67, Ti: 3.50, N: 1.10 };

// Helper: compute μ = Σ q_k · r_k (NPA charges × coordinates → Debye)
// 1 e·Å = 4.8032 Debye
function computeDipole(atoms: AtomDescriptor[]): { x: number; y: number; z: number; magnitude: number } {
  let mx = 0, my = 0, mz = 0;
  for (const a of atoms) {
    const q = a.charge ?? 0;
    mx += q * a.x;
    my += q * a.y;
    mz += q * a.z;
  }
  const scale = 4.8032; // e·Å → Debye
  mx *= scale; my *= scale; mz *= scale;
  const mag = Math.sqrt(mx*mx + my*my + mz*mz);
  return { x: parseFloat(mx.toFixed(3)), y: parseFloat(my.toFixed(3)), z: parseFloat(mz.toFixed(3)), magnitude: parseFloat(mag.toFixed(3)) };
}

// Helper: α_iso ≈ Σ α_i^atom
function computePolarizability(atoms: AtomDescriptor[]): number {
  let alpha = 0;
  for (const a of atoms) alpha += ATOMIC_ALPHA[a.element] ?? 1.5;
  return parseFloat(alpha.toFixed(2));
}

const catalysts: CatalystEntry[] = [
  // ╔═══════════════════ DCS ═══════════════════╗
  {
    id: "DCS",
    name: "Dichlorosilane",
    smiles: "Cl[SiH2]Cl",
    formula: "SiH₂Cl₂",
    molecularWeight: 28.085 + 2 * 1.008 + 2 * 35.453, // 101.007
    atoms: [
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.42 },
      { element: "Cl", x: -1.4, y: 1.2, z: 0.3, charge: -0.48 },
      { element: "Cl", x: 1.4, y: 1.2, z: -0.3, charge: -0.46 },
      { element: "H", x: -0.8, y: -1.0, z: 0.6 },
      { element: "H", x: 0.8, y: -1.0, z: -0.6 },
    ],
    orbitalLevels: [
      { name: "LUMO+1", energy: 0.14, type: "virtual" },
      { name: "LUMO", energy: 0.018, type: "virtual" },
      { name: "HOMO", energy: -0.247, type: "occupied" },
      { name: "HOMO-1", energy: -0.278, type: "occupied" },
      { name: "HOMO-2", energy: -0.305, type: "occupied" },
    ],
    gapEv: (0.265 * 27.2114),
    energyProfile: [
      { name: "RC", energy: 0, label: "反应物络合" },
      { name: "TS1", energy: 10.2, label: "插入过渡态" },
      { name: "INT", energy: -6.8, label: "烷基中间体" },
      { name: "TS2", energy: 1.5, label: "迁移过渡态" },
      { name: "PC", energy: -22.1, label: "产物络合" },
    ],
    chargeData: [
      { atomLabel: "Si1", mulliken: 1.18, npa: 1.42, hirshfeld: 0.62 },
      { atomLabel: "Cl2", mulliken: -0.38, npa: -0.48, hirshfeld: -0.22 },
      { atomLabel: "Cl3", mulliken: -0.36, npa: -0.46, hirshfeld: -0.21 },
      { atomLabel: "H4", mulliken: -0.22, npa: -0.24, hirshfeld: -0.10 },
      { atomLabel: "H5", mulliken: -0.22, npa: -0.24, hirshfeld: -0.09 },
    ],
    kineticParams: { dG_ins: 10.2, dG_poi: 16.8 },
    solvationShifts: [
      { solventName: "Gas Phase", epsilon: 1.0, dG_correction: 0 },
      { solventName: "Toluene", epsilon: 2.38, dG_correction: -1.2 },
      { solventName: "THF", epsilon: 7.58, dG_correction: -3.8 },
      { solventName: "DCM", epsilon: 8.93, dG_correction: -4.2 },
      { solventName: "Acetonitrile", epsilon: 36.6, dG_correction: -7.5 },
    ],
    contributionData: [
      { atom: "Si (3s)", value: 8 },
      { atom: "Si (3p)", value: 18 },
      { atom: "Cl (3p)", value: 62 },
      { atom: "H (1s)", value: 12 },
    ],
    dipoleMoment: computeDipole([
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.42 },
      { element: "Cl", x: -1.4, y: 1.2, z: 0.3, charge: -0.48 },
      { element: "Cl", x: 1.4, y: 1.2, z: -0.3, charge: -0.46 },
      { element: "H", x: -0.8, y: -1.0, z: 0.6 },
      { element: "H", x: 0.8, y: -1.0, z: -0.6 },
    ]),
    polarizability: computePolarizability([
      { element: "Si", x: 0, y: 0, z: 0 },
      { element: "Cl", x: -1.4, y: 1.2, z: 0.3 },
      { element: "Cl", x: 1.4, y: 1.2, z: -0.3 },
      { element: "H", x: -0.8, y: -1.0, z: 0.6 },
      { element: "H", x: 0.8, y: -1.0, z: -0.6 },
    ]),
  },

  // ╔═══════════════════ MCSOMe ═══════════════════╗
  {
    id: "MCSOMe",
    name: "Methoxychlorosilane",
    smiles: "CO[SiH](Cl)OC",
    formula: "C₂H₅ClO₂Si",
    molecularWeight: 2 * 12.011 + 5 * 1.008 + 35.453 + 2 * 15.999 + 28.085, // 128.59
    atoms: [
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.35 },
      { element: "O", x: 1.6, y: 0, z: 0, charge: -0.65 },
      { element: "Cl", x: -1.2, y: 1.5, z: 0.5, charge: -0.42 },
      { element: "C", x: -0.8, y: -1.2, z: 0.8 },
      { element: "C", x: 2.5, y: -0.8, z: 0.5 },
      { element: "O", x: -0.5, y: -0.2, z: -1.6, charge: -0.58 },
      { element: "H", x: 0.2, y: 1.8, z: -0.5 },
    ],
    orbitalLevels: [
      { name: "LUMO+1", energy: 0.12, type: "virtual" },
      { name: "LUMO", energy: 0.012, type: "virtual" },
      { name: "HOMO", energy: -0.254, type: "occupied" },
      { name: "HOMO-1", energy: -0.285, type: "occupied" },
      { name: "HOMO-2", energy: -0.312, type: "occupied" },
    ],
    gapEv: (0.266 * 27.2114),
    energyProfile: [
      { name: "RC", energy: 0, label: "反应物络合" },
      { name: "TS1", energy: 12.4, label: "插入过渡态" },
      { name: "INT", energy: -5.2, label: "烷基中间体" },
      { name: "TS2", energy: 3.1, label: "迁移过渡态" },
      { name: "PC", energy: -18.4, label: "产物络合" },
    ],
    chargeData: [
      { atomLabel: "Si1", mulliken: 1.12, npa: 1.35, hirshfeld: 0.55 },
      { atomLabel: "O2", mulliken: -0.52, npa: -0.65, hirshfeld: -0.32 },
      { atomLabel: "Cl3", mulliken: -0.34, npa: -0.42, hirshfeld: -0.19 },
      { atomLabel: "C4", mulliken: -0.18, npa: -0.22, hirshfeld: -0.08 },
      { atomLabel: "C5", mulliken: -0.15, npa: -0.18, hirshfeld: -0.06 },
      { atomLabel: "O6", mulliken: -0.48, npa: -0.58, hirshfeld: -0.28 },
      { atomLabel: "H7", mulliken: 0.55, npa: 0.70, hirshfeld: 0.38 },
    ],
    kineticParams: { dG_ins: 12.4, dG_poi: 18.2 },
    solvationShifts: [
      { solventName: "Gas Phase", epsilon: 1.0, dG_correction: 0 },
      { solventName: "Toluene", epsilon: 2.38, dG_correction: -1.8 },
      { solventName: "THF", epsilon: 7.58, dG_correction: -4.5 },
      { solventName: "DCM", epsilon: 8.93, dG_correction: -5.1 },
      { solventName: "Acetonitrile", epsilon: 36.6, dG_correction: -8.9 },
    ],
    contributionData: [
      { atom: "Si (3s)", value: 5 },
      { atom: "Si (3p)", value: 12 },
      { atom: "O (2p)", value: 65 },
      { atom: "Cl (3p)", value: 15 },
    ],
    dipoleMoment: computeDipole([
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.35 },
      { element: "O", x: 1.6, y: 0, z: 0, charge: -0.65 },
      { element: "Cl", x: -1.2, y: 1.5, z: 0.5, charge: -0.42 },
      { element: "C", x: -0.8, y: -1.2, z: 0.8 },
      { element: "C", x: 2.5, y: -0.8, z: 0.5 },
      { element: "O", x: -0.5, y: -0.2, z: -1.6, charge: -0.58 },
      { element: "H", x: 0.2, y: 1.8, z: -0.5 },
    ]),
    polarizability: computePolarizability([
      { element: "Si", x: 0, y: 0, z: 0 },
      { element: "O", x: 1.6, y: 0, z: 0 },
      { element: "Cl", x: -1.2, y: 1.5, z: 0.5 },
      { element: "C", x: -0.8, y: -1.2, z: 0.8 },
      { element: "C", x: 2.5, y: -0.8, z: 0.5 },
      { element: "O", x: -0.5, y: -0.2, z: -1.6 },
      { element: "H", x: 0.2, y: 1.8, z: -0.5 },
    ]),
  },

  // ╔═══════════════════ DMOS ═══════════════════╗
  {
    id: "DMOS",
    name: "Dimethoxysilane",
    smiles: "CO[SiH2]OC",
    formula: "C₂H₈O₂Si",
    molecularWeight: 2 * 12.011 + 8 * 1.008 + 2 * 15.999 + 28.085, // 92.168
    atoms: [
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.18 },
      { element: "O", x: 1.6, y: 0.3, z: 0, charge: -0.72 },
      { element: "O", x: -1.6, y: -0.3, z: 0, charge: -0.70 },
      { element: "C", x: 2.8, y: -0.5, z: 0.5 },
      { element: "C", x: -2.8, y: 0.5, z: -0.5 },
      { element: "H", x: 0.4, y: -1.2, z: 0.8 },
      { element: "H", x: -0.4, y: 1.2, z: -0.8 },
    ],
    orbitalLevels: [
      { name: "LUMO+1", energy: 0.10, type: "virtual" },
      { name: "LUMO", energy: 0.005, type: "virtual" },
      { name: "HOMO", energy: -0.220, type: "occupied" },
      { name: "HOMO-1", energy: -0.258, type: "occupied" },
      { name: "HOMO-2", energy: -0.290, type: "occupied" },
    ],
    gapEv: (0.225 * 27.2114),
    energyProfile: [
      { name: "RC", energy: 0, label: "反应物络合" },
      { name: "TS1", energy: 15.8, label: "插入过渡态" },
      { name: "INT", energy: -3.1, label: "烷基中间体" },
      { name: "TS2", energy: 5.4, label: "迁移过渡态" },
      { name: "PC", energy: -12.5, label: "产物络合" },
    ],
    chargeData: [
      { atomLabel: "Si1", mulliken: 0.95, npa: 1.18, hirshfeld: 0.48 },
      { atomLabel: "O2", mulliken: -0.58, npa: -0.72, hirshfeld: -0.35 },
      { atomLabel: "O3", mulliken: -0.56, npa: -0.70, hirshfeld: -0.34 },
      { atomLabel: "C4", mulliken: -0.14, npa: -0.18, hirshfeld: -0.06 },
      { atomLabel: "C5", mulliken: -0.12, npa: -0.16, hirshfeld: -0.05 },
      { atomLabel: "H6", mulliken: 0.22, npa: 0.29, hirshfeld: 0.16 },
      { atomLabel: "H7", mulliken: 0.23, npa: 0.29, hirshfeld: 0.16 },
    ],
    kineticParams: { dG_ins: 15.8, dG_poi: 20.5 },
    solvationShifts: [
      { solventName: "Gas Phase", epsilon: 1.0, dG_correction: 0 },
      { solventName: "Toluene", epsilon: 2.38, dG_correction: -2.1 },
      { solventName: "THF", epsilon: 7.58, dG_correction: -5.2 },
      { solventName: "DCM", epsilon: 8.93, dG_correction: -5.8 },
      { solventName: "Acetonitrile", epsilon: 36.6, dG_correction: -9.8 },
    ],
    contributionData: [
      { atom: "Si (3s)", value: 4 },
      { atom: "Si (3p)", value: 8 },
      { atom: "O (2p)", value: 78 },
      { atom: "C (2p)", value: 10 },
    ],
    dipoleMoment: computeDipole([
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.18 },
      { element: "O", x: 1.6, y: 0.3, z: 0, charge: -0.72 },
      { element: "O", x: -1.6, y: -0.3, z: 0, charge: -0.70 },
      { element: "C", x: 2.8, y: -0.5, z: 0.5 },
      { element: "C", x: -2.8, y: 0.5, z: -0.5 },
      { element: "H", x: 0.4, y: -1.2, z: 0.8 },
      { element: "H", x: -0.4, y: 1.2, z: -0.8 },
    ]),
    polarizability: computePolarizability([
      { element: "Si", x: 0, y: 0, z: 0 },
      { element: "O", x: 1.6, y: 0.3, z: 0 },
      { element: "O", x: -1.6, y: -0.3, z: 0 },
      { element: "C", x: 2.8, y: -0.5, z: 0.5 },
      { element: "C", x: -2.8, y: 0.5, z: -0.5 },
      { element: "H", x: 0.4, y: -1.2, z: 0.8 },
      { element: "H", x: -0.4, y: 1.2, z: -0.8 },
    ]),
  },

  // ╔═══════════════════ SiCl4 ═══════════════════╗
  {
    id: "SiCl4",
    name: "Silicon Tetrachloride",
    smiles: "Cl[Si](Cl)(Cl)Cl",
    formula: "SiCl₄",
    molecularWeight: 28.085 + 4 * 35.453, // 169.897
    atoms: [
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.62 },
      { element: "Cl", x: 1.2, y: 1.2, z: 0.8, charge: -0.41 },
      { element: "Cl", x: -1.2, y: -1.2, z: 0.8, charge: -0.40 },
      { element: "Cl", x: 1.2, y: -1.2, z: -0.8, charge: -0.41 },
      { element: "Cl", x: -1.2, y: 1.2, z: -0.8, charge: -0.40 },
    ],
    orbitalLevels: [
      { name: "LUMO+1", energy: 0.18, type: "virtual" },
      { name: "LUMO", energy: 0.032, type: "virtual" },
      { name: "HOMO", energy: -0.280, type: "occupied" },
      { name: "HOMO-1", energy: -0.310, type: "occupied" },
      { name: "HOMO-2", energy: -0.340, type: "occupied" },
    ],
    gapEv: (0.312 * 27.2114),
    energyProfile: [
      { name: "RC", energy: 0, label: "反应物络合" },
      { name: "TS1", energy: 8.5, label: "插入过渡态" },
      { name: "INT", energy: -8.2, label: "烷基中间体" },
      { name: "TS2", energy: 0.8, label: "迁移过渡态" },
      { name: "PC", energy: -25.0, label: "产物络合" },
    ],
    chargeData: [
      { atomLabel: "Si1", mulliken: 1.35, npa: 1.62, hirshfeld: 0.72 },
      { atomLabel: "Cl2", mulliken: -0.34, npa: -0.41, hirshfeld: -0.18 },
      { atomLabel: "Cl3", mulliken: -0.33, npa: -0.40, hirshfeld: -0.18 },
      { atomLabel: "Cl4", mulliken: -0.34, npa: -0.41, hirshfeld: -0.18 },
      { atomLabel: "Cl5", mulliken: -0.34, npa: -0.40, hirshfeld: -0.18 },
    ],
    kineticParams: { dG_ins: 8.5, dG_poi: 14.2 },
    solvationShifts: [
      { solventName: "Gas Phase", epsilon: 1.0, dG_correction: 0 },
      { solventName: "Toluene", epsilon: 2.38, dG_correction: -0.8 },
      { solventName: "THF", epsilon: 7.58, dG_correction: -2.5 },
      { solventName: "DCM", epsilon: 8.93, dG_correction: -2.9 },
      { solventName: "Acetonitrile", epsilon: 36.6, dG_correction: -5.2 },
    ],
    contributionData: [
      { atom: "Si (3s)", value: 10 },
      { atom: "Si (3p)", value: 22 },
      { atom: "Cl (3p)", value: 65 },
      { atom: "Cl (3s)", value: 3 },
    ],
    dipoleMoment: computeDipole([
      { element: "Si", x: 0, y: 0, z: 0, charge: 1.62 },
      { element: "Cl", x: 1.2, y: 1.2, z: 0.8, charge: -0.41 },
      { element: "Cl", x: -1.2, y: -1.2, z: 0.8, charge: -0.40 },
      { element: "Cl", x: 1.2, y: -1.2, z: -0.8, charge: -0.41 },
      { element: "Cl", x: -1.2, y: 1.2, z: -0.8, charge: -0.40 },
    ]),
    polarizability: computePolarizability([
      { element: "Si", x: 0, y: 0, z: 0 },
      { element: "Cl", x: 1.2, y: 1.2, z: 0.8 },
      { element: "Cl", x: -1.2, y: -1.2, z: 0.8 },
      { element: "Cl", x: 1.2, y: -1.2, z: -0.8 },
      { element: "Cl", x: -1.2, y: 1.2, z: -0.8 },
    ]),
  },

  // ╔═══════════════════ SiMe4 ═══════════════════╗
  {
    id: "SiMe4",
    name: "Tetramethylsilane",
    smiles: "C[Si](C)(C)C",
    formula: "Si(CH₃)₄",
    molecularWeight: 28.085 + 4 * 12.011 + 12 * 1.008, // 88.225
    atoms: [
      { element: "Si", x: 0, y: 0, z: 0, charge: 0.45 },
      { element: "C", x: 1.2, y: 1.2, z: 0.8 },
      { element: "C", x: -1.2, y: -1.2, z: 0.8 },
      { element: "C", x: 1.2, y: -1.2, z: -0.8 },
      { element: "C", x: -1.2, y: 1.2, z: -0.8 },
    ],
    orbitalLevels: [
      { name: "LUMO+1", energy: 0.08, type: "virtual" },
      { name: "LUMO", energy: -0.002, type: "virtual" },
      { name: "HOMO", energy: -0.195, type: "occupied" },
      { name: "HOMO-1", energy: -0.230, type: "occupied" },
      { name: "HOMO-2", energy: -0.260, type: "occupied" },
    ],
    gapEv: (0.193 * 27.2114),
    energyProfile: [
      { name: "RC", energy: 0, label: "反应物络合" },
      { name: "TS1", energy: 22.4, label: "插入过渡态" },
      { name: "INT", energy: -1.0, label: "烷基中间体" },
      { name: "TS2", energy: 8.2, label: "迁移过渡态" },
      { name: "PC", energy: -5.5, label: "产物络合" },
    ],
    chargeData: [
      { atomLabel: "Si1", mulliken: 0.32, npa: 0.45, hirshfeld: 0.18 },
      { atomLabel: "C2", mulliken: -0.08, npa: -0.11, hirshfeld: -0.04 },
      { atomLabel: "C3", mulliken: -0.08, npa: -0.12, hirshfeld: -0.05 },
      { atomLabel: "C4", mulliken: -0.08, npa: -0.11, hirshfeld: -0.05 },
      { atomLabel: "C5", mulliken: -0.08, npa: -0.11, hirshfeld: -0.04 },
    ],
    kineticParams: { dG_ins: 22.4, dG_poi: 28.0 },
    solvationShifts: [
      { solventName: "Gas Phase", epsilon: 1.0, dG_correction: 0 },
      { solventName: "Toluene", epsilon: 2.38, dG_correction: -0.4 },
      { solventName: "THF", epsilon: 7.58, dG_correction: -1.2 },
      { solventName: "DCM", epsilon: 8.93, dG_correction: -1.5 },
      { solventName: "Acetonitrile", epsilon: 36.6, dG_correction: -2.8 },
    ],
    contributionData: [
      { atom: "Si (3s)", value: 15 },
      { atom: "Si (3p)", value: 35 },
      { atom: "C (2p)", value: 42 },
      { atom: "C (2s)", value: 8 },
    ],
    dipoleMoment: computeDipole([
      { element: "Si", x: 0, y: 0, z: 0, charge: 0.45 },
      { element: "C", x: 1.2, y: 1.2, z: 0.8 },
      { element: "C", x: -1.2, y: -1.2, z: 0.8 },
      { element: "C", x: 1.2, y: -1.2, z: -0.8 },
      { element: "C", x: -1.2, y: 1.2, z: -0.8 },
    ]),
    polarizability: computePolarizability([
      { element: "Si", x: 0, y: 0, z: 0 },
      { element: "C", x: 1.2, y: 1.2, z: 0.8 },
      { element: "C", x: -1.2, y: -1.2, z: 0.8 },
      { element: "C", x: 1.2, y: -1.2, z: -0.8 },
      { element: "C", x: -1.2, y: 1.2, z: -0.8 },
    ]),
  },
];

// ────────────────────────────────────────────────────────────────
// Public API
// ────────────────────────────────────────────────────────────────

export function getCatalyst(id: string): CatalystEntry | undefined {
  return catalysts.find(c => c.id === id);
}

export function getAllCatalysts(): CatalystEntry[] {
  return catalysts;
}

export default catalysts;
