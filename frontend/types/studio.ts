import type { LucideIcon } from "lucide-react";

export type StatusTone = "green" | "yellow" | "red" | "blue" | "gray" | "violet" | "orange";

export interface NavItem {
  id: ModuleId;
  label: string;
  icon: LucideIcon;
}

export type ModuleId =
  | "integrated"
  | "dashboard"
  | "literature"
  | "library"
  | "experiments"
  | "merged"
  | "radical"
  | "peroxide"
  | "sic"
  | "degradation"
  | "kinetics"
  | "residence"
  | "microstructure"
  | "builder"
  | "scientific"
  | "parser"
  | "bond"
  | "density"
  | "esp"
  | "fukui"
  | "difference"
  | "orbitals"
  | "charges"
  | "nbo"
  | "qtaim"
  | "tea"
  | "poisoning"
  | "insertion"
  | "hydrolysis"
  | "mechanisms"
  | "decision"
  | "mcp"
  | "reports"
  | "data"
  | "settings";

export interface StudioMolecule {
  key: "DCS" | "MCSOMe" | "DMOS" | string;
  name: string;
  smiles: string;
  substituents: string;
  role: string;
  completion: number;
  teaCaptureRisk: StatusTone;
  poisonRisk: StatusTone;
  insertionActivity: StatusTone;
  postPotential: StatusTone;
  source: string;
  family?: string;
  chainLength?: string;
  functionalSites?: string[];
  electronicEffect?: string;
  stericLevel?: "低" | "中" | "高" | "基准";
  thesisConclusion?: string;
  descriptors: {
    molecularWeight: number | null;
    atomCount: number;
    heavyAtomCount: number;
    rotatableBonds: number;
    vdwVolume: number;
    siRadius: number;
    oCount: number;
    clCount: number;
    polarSites: number;
  };
}

export interface ThesisEntity {
  category: string;
  name: string;
  chineseName: string;
  evidence: string;
  source: string;
  confidence: number;
}

export interface CatalystModel {
  key: string;
  name: string;
  role: string;
  activeSite: string;
  thesisLink: string;
  source: string;
}

export interface ExperimentalRecord {
  id: string;
  monomer: string;
  catalyst: string;
  polymerization: string;
  chainLength: string;
  activity: number | null;
  insertionRatio: number | null;
  hexeneContent: number | null;
  sequenceLength: number | null;
  meltingPoint: number | null;
  crystallinity: number | null;
  transparency: number | null;
  deltaGBarrier: number | null;
  deltaGPoison: number | null;
  stericPenalty: number;
  electronicGuiding: number;
  source: string;
}

export interface MechanismHypothesis {
  key: string;
  name: string;
  summary: string;
  supportingEvidence: string[];
  falsification: string[];
  requiredData: string[];
  currentStatus: string;
  confidence: number;
  source: string;
}

export interface EnergyRow {
  molecule: string;
  deltaGBind: number | null;
  deltaGPoison: number | null;
  deltaGPi: number | null;
  deltaGBarrier: number | null;
  krel: number | null;
  source: string;
}

export interface DecisionRow {
  molecule: string;
  siOPolarity: string;
  alCapture: string;
  tiPoison: string;
  insertionBarrier: string;
  postFunctionality: string;
}

export interface HeatmapCell {
  molecule: string;
  metric: string;
  value: number;
  tone: StatusTone;
}

export interface RiskGauge {
  label: string;
  subtitle: string;
  value: number;
  tone: StatusTone;
}
