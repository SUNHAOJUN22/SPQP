import {
  Activity,
  Atom,
  Beaker,
  Binary,
  BookOpenText,
  BrainCircuit,
  ClipboardList,
  Cloud,
  Combine,
  Database,
  Diff,
  FileText,
  Flame,
  FlaskConical,
  Gauge,
  GitBranch,
  Home,
  Library,
  Link2,
  Network,
  Orbit,
  Radar,
  Timer,
  Settings,
  Sigma,
  Scissors,
  UploadCloud,
  Waves,
  Workflow
} from "lucide-react";
import type {
  CatalystModel,
  DecisionRow,
  EnergyRow,
  ExperimentalRecord,
  HeatmapCell,
  MechanismHypothesis,
  NavItem,
  RiskGauge,
  StudioMolecule,
  ThesisEntity
} from "@/types/studio";

export const navItems: NavItem[] = [
  { id: "integrated", label: "整合总控台", icon: Combine },
  { id: "dashboard", label: "总览驾驶舱", icon: Home },
  { id: "literature", label: "论文知识库", icon: BookOpenText },
  { id: "library", label: "分子库", icon: Library },
  { id: "experiments", label: "实验数据闭环", icon: Combine },
  { id: "merged", label: "合并工作台", icon: Combine },
  { id: "radical", label: "过氧化物自由基", icon: Flame },
  { id: "peroxide", label: "过氧化物结构库", icon: FlaskConical },
  { id: "sic", label: "Si–C 键稳定性", icon: Link2 },
  { id: "degradation", label: "降解-交联竞争图", icon: Scissors },
  { id: "kinetics", label: "自由基动力学", icon: Activity },
  { id: "residence", label: "停留时间窗口", icon: Timer },
  { id: "microstructure", label: "乙烯/等规度影响", icon: Workflow },
  { id: "scientific", label: "科学计算工作流", icon: Binary },
  { id: "connectors", label: "科学计算连接器", icon: Workflow },
  { id: "builder", label: "Gaussian 输入生成", icon: ClipboardList },
  { id: "parser", label: "Gaussian 输出解析", icon: UploadCloud },
  { id: "bond", label: "Si–O / Si–C 键实验室", icon: Atom },
  { id: "density", label: "电子云密度", icon: Cloud },
  { id: "esp", label: "ESP 静电势", icon: Radar },
  { id: "fukui", label: "Fukui 局部反应性", icon: Sigma },
  { id: "difference", label: "差分电子密度", icon: Diff },
  { id: "orbitals", label: "前线轨道", icon: Orbit },
  { id: "charges", label: "电荷布居", icon: Activity },
  { id: "nbo", label: "NBO 相互作用", icon: Network },
  { id: "qtaim", label: "QTAIM / NCI 分析", icon: Waves },
  { id: "tea", label: "TEA 助剂作用", icon: FlaskConical },
  { id: "poisoning", label: "Ti 毒化判据", icon: Gauge },
  { id: "insertion", label: "插入反应能量面", icon: GitBranch },
  { id: "hydrolysis", label: "水解缩合后反应", icon: Beaker },
  { id: "mechanisms", label: "可证伪机制模型", icon: Sigma },
  { id: "decision", label: "量子判据引擎", icon: BrainCircuit },
  { id: "mcp", label: "MCP 自动化工作流", icon: Workflow },
  { id: "reports", label: "中文报告生成", icon: FileText },
  { id: "data", label: "数据管理", icon: Database },
  { id: "settings", label: "系统设置", icon: Settings }
];

export const moleculeLibrary: StudioMolecule[] = [
  {
    key: "DCS",
    name: "hex-5-enyl-methyl-dichlorosilane",
    smiles: "C=CCCCC[Si](C)(Cl)Cl",
    substituents: "Me / Cl / Cl / hex-5-enyl",
    role: "氯硅烷基准单体，用作高插入活性的参照结构。",
    completion: 28,
    teaCaptureRisk: "yellow",
    poisonRisk: "green",
    insertionActivity: "green",
    postPotential: "yellow",
    source: "示例数据 / MOCK",
    family: "ω-烯烃基甲基二氯硅烷",
    chainLength: "C6 / hex-5-enyl",
    functionalSites: ["C=C", "Si–Cl", "TEA Al···Cl"],
    electronicEffect: "氯硅烷取代基电子吸引较强，可增强助剂导向与活性中心靠近概率。",
    stericLevel: "中",
    thesisConclusion: "论文摘要指出氯硅烷取代基电子效应增强有利于插入，其中链长窗口会影响乙烯/丙烯体系表现。",
    descriptors: {
      molecularWeight: 197.18,
      atomCount: 25,
      heavyAtomCount: 11,
      rotatableBonds: 6,
      vdwVolume: 221.5,
      siRadius: 3.75,
      oCount: 0,
      clCount: 2,
      polarSites: 2
    }
  },
  {
    key: "MCSOMe",
    name: "chloro(hex-5-en-1-yl)methoxy-methylsilane",
    smiles: "C=CCCCC[Si](C)(OC)Cl",
    substituents: "Me / Cl / OMe / hex-5-enyl",
    role: "单甲氧基平衡候选结构，用于评价聚合兼容性与后反应功能化的折中。",
    completion: 36,
    teaCaptureRisk: "green",
    poisonRisk: "yellow",
    insertionActivity: "green",
    postPotential: "green",
    source: "示例数据 / MOCK",
    family: "甲氧基硅烷衍生物",
    chainLength: "C6 / hex-5-enyl",
    functionalSites: ["C=C", "Si–O", "Si–Cl", "O→Ti", "Al←O"],
    electronicEffect: "单甲氧基提供 Lewis 碱性与后反应位点，同时保留一个 Si–Cl 电子导向通道。",
    stericLevel: "中",
    thesisConclusion: "该结构属于论文体系的机理外推候选；真实排序需由 Gaussian 输出或用户实验数据支撑。",
    descriptors: {
      molecularWeight: 192.78,
      atomCount: 28,
      heavyAtomCount: 12,
      rotatableBonds: 7,
      vdwVolume: 218.2,
      siRadius: 3.72,
      oCount: 1,
      clCount: 1,
      polarSites: 2
    }
  },
  {
    key: "DMOS",
    name: "hex-5-enyl-dimethoxy-methylsilane",
    smiles: "C=CCCCC[Si](C)(OC)OC",
    substituents: "Me / OMe / OMe / hex-5-enyl",
    role: "双甲氧基极限结构，后反应潜力高，但可能受 TEA 捕获、O→Ti 毒化与位阻共同限制。",
    completion: 24,
    teaCaptureRisk: "red",
    poisonRisk: "red",
    insertionActivity: "yellow",
    postPotential: "green",
    source: "示例数据 / MOCK",
    family: "甲氧基硅烷衍生物",
    chainLength: "C6 / hex-5-enyl",
    functionalSites: ["C=C", "Si–O", "双 OMe", "O→Ti", "Al←O"],
    electronicEffect: "双甲氧基显著提高 O 原子给电子能力和后反应功能性，也提高 TEA 捕获与 O→Ti 毒化风险。",
    stericLevel: "高",
    thesisConclusion: "该结构用于检验强功能化是否与聚合插入兼容；当前所有趋势均为示例。",
    descriptors: {
      molecularWeight: 188.34,
      atomCount: 31,
      heavyAtomCount: 13,
      rotatableBonds: 8,
      vdwVolume: 219.8,
      siRadius: 3.73,
      oCount: 2,
      clCount: 0,
      polarSites: 2
    }
  },
  {
    key: "ethylene",
    name: "ethylene",
    smiles: "C=C",
    substituents: "H / H / H / H",
    role: "乙烯基准插入单体，用作 C=C 生产性 π-络合和插入势垒参照。",
    completion: 18,
    teaCaptureRisk: "gray",
    poisonRisk: "green",
    insertionActivity: "green",
    postPotential: "gray",
    source: "示例数据 / MOCK",
    family: "基准 α-烯烃",
    chainLength: "C2",
    functionalSites: ["C=C"],
    electronicEffect: "无硅取代基，作为插入活性基准。",
    stericLevel: "低",
    thesisConclusion: "乙烯用于比较功能 α-烯烃插入代价和 EPC/IPC 微相效应。",
    descriptors: { molecularWeight: 28.05, atomCount: 6, heavyAtomCount: 2, rotatableBonds: 0, vdwVolume: 42.5, siRadius: 0, oCount: 0, clCount: 0, polarSites: 1 }
  },
  {
    key: "propylene",
    name: "propylene",
    smiles: "C=CC",
    substituents: "Me / H / H",
    role: "丙烯共聚基准单体，用于比较甲基位阻、区域选择性和立构插入差异。",
    completion: 12,
    teaCaptureRisk: "gray",
    poisonRisk: "green",
    insertionActivity: "green",
    postPotential: "gray",
    source: "示例数据 / MOCK",
    family: "基准 α-烯烃",
    chainLength: "C3",
    functionalSites: ["C=C", "CH3"],
    electronicEffect: "甲基提供轻微给电子效应和额外位阻。",
    stericLevel: "低",
    thesisConclusion: "丙烯体系中功能单体位阻对插入下降更明显，需独立于乙烯体系评价。",
    descriptors: { molecularWeight: 42.08, atomCount: 9, heavyAtomCount: 3, rotatableBonds: 0, vdwVolume: 58.9, siRadius: 0, oCount: 0, clCount: 0, polarSites: 1 }
  },
  {
    key: "TEA",
    name: "triethylaluminum",
    smiles: "CC[Al](CC)CC",
    substituents: "Et / Et / Et",
    role: "TEA 助催化剂 / 三乙基铝助剂",
    completion: 20,
    teaCaptureRisk: "blue",
    poisonRisk: "gray",
    insertionActivity: "gray",
    postPotential: "gray",
    source: "示例数据 / MOCK",
    family: "助催化剂",
    chainLength: "AlEt3",
    functionalSites: ["Al Lewis 酸中心"],
    electronicEffect: "Lewis 酸中心可捕获 Si–Cl 或 OMe 位点，也可能改变单体靠近活性中心方式。",
    stericLevel: "中",
    thesisConclusion: "论文摘要指出助催化剂 Al 原子与氯硅烷取代基存在相互作用，并随取代基电子强度增强。",
    descriptors: { molecularWeight: 114.17, atomCount: 22, heavyAtomCount: 7, rotatableBonds: 3, vdwVolume: 148.5, siRadius: 0, oCount: 0, clCount: 0, polarSites: 1 }
  }
];

export const energyRows: EnergyRow[] = [
  { molecule: "DCS", deltaGBind: -7.4, deltaGPoison: 8.2, deltaGPi: -11.1, deltaGBarrier: 12.8, krel: 1, source: "示例趋势 / MOCK" },
  { molecule: "MCSOMe", deltaGBind: -13.6, deltaGPoison: 3.2, deltaGPi: -10.2, deltaGBarrier: 13.7, krel: 0.27, source: "示例趋势 / MOCK" },
  { molecule: "DMOS", deltaGBind: -25.8, deltaGPoison: -4.5, deltaGPi: -5.8, deltaGBarrier: 18.4, krel: 0.0006, source: "示例趋势 / MOCK" }
];

export const decisionMatrix: DecisionRow[] = [
  { molecule: "DCS", siOPolarity: "无 Si–O 本征键", alCapture: "Al···Cl 弱导向", tiPoison: "低", insertionBarrier: "基准", postFunctionality: "氯硅烷水解" },
  { molecule: "MCSOMe", siOPolarity: "中等极化", alCapture: "有效预组织", tiPoison: "配位竞争", insertionBarrier: "接近基准", postFunctionality: "平衡" },
  { molecule: "DMOS", siOPolarity: "强极化", alCapture: "过度捕获风险", tiPoison: "高", insertionBarrier: "升高", postFunctionality: "高" }
];

const heatRows = [
  ["DCS", 8, 34, 18, 86, 62, 72],
  ["MCSOMe", 58, 68, 45, 78, 80, 82],
  ["DMOS", 84, 94, 88, 38, 92, 39]
] as const;
const heatMetrics = ["Si–O 极化", "TEA 捕获", "Ti 毒化", "插入势垒", "后反应潜力", "综合评分"];

export const heatmapCells: HeatmapCell[] = heatRows.flatMap(([molecule, ...values]) =>
  values.map((value, index) => {
    const metric = heatMetrics[index];
    const dangerMetric = metric === "Ti 毒化" || metric === "插入势垒" || metric === "TEA 捕获";
    const tone = value >= 75 ? (dangerMetric ? "red" : "green") : value >= 45 ? "yellow" : dangerMetric ? "green" : "gray";
    return { molecule, metric, value, tone };
  })
);

export const riskGauges: RiskGauge[] = [
  { label: "TEA 捕获风险", subtitle: "Al←O / Al···Cl", value: 62, tone: "yellow" },
  { label: "O→Ti 毒化风险", subtitle: "ΔGpoison", value: 45, tone: "yellow" },
  { label: "插入势垒风险", subtitle: "ΔG‡", value: 38, tone: "green" },
  { label: "位阻风险", subtitle: "NCI/RDG 红区", value: 42, tone: "yellow" },
  { label: "后反应潜力", subtitle: "Si–O–Si", value: 80, tone: "green" }
];

export const fiveEnergyRadar = [
  { axis: "E_intrinsic(Si–O)", DCS: 12, MCSOMe: 56, DMOS: 82 },
  { axis: "E_Al_capture", DCS: 28, MCSOMe: 64, DMOS: 92 },
  { axis: "E_Ti_poison", DCS: 15, MCSOMe: 45, DMOS: 88 },
  { axis: "E_insert", DCS: 86, MCSOMe: 78, DMOS: 38 },
  { axis: "E_post", DCS: 60, MCSOMe: 78, DMOS: 94 }
];

export const sioDescriptors = [
  { metric: "r(Si–O)", DCS: null, MCSOMe: 1.66, DMOS: 1.64, unit: "Å" }
];

export const bondRadarData = [
  { axis: "键长", DCS: 18, MCSOMe: 62, DMOS: 68 }
];

export const bondBars = [
  { name: "MCSOMe 配位前", length: 1.66, freq: 1035, wbi: 0.74, mayer: 0.82 }
];

export const pathwayData = [
  { coordinate: "游离活性中心 + 单体", DCS: 0, MCSOMe: 0, DMOS: 0 },
  { coordinate: "π-络合物", DCS: -11.1, MCSOMe: -10.2, DMOS: -5.8 },
  { coordinate: "插入过渡态", DCS: 12.8, MCSOMe: 13.7, DMOS: 18.4 },
  { coordinate: "插入产物", DCS: -18.6, MCSOMe: -16.8, DMOS: -9.4 }
];

export const hydrolysisTemplates = [
  "R–SiMeCl₂ + H₂O → R–SiMeClOH + HCl"
];

export const orbitalLevels = [
  { orbital: "HOMO", energy: -5.2, contribution: 62 }
];

export const chargeData = [
  { atom: "Si", Mulliken: 1.16, NPA: 1.42, RESP: 1.28, Hirshfeld: 0.74 },
  { atom: "O", Mulliken: -0.68, NPA: -0.82, RESP: -0.61, Hirshfeld: -0.36 }
];

export const nboData = [
  { donor: "n(O)", acceptor: "Al", value: 14.2, channel: "O→Al" },
  { donor: "n(O)", acceptor: "Ti", value: 8.4, channel: "O→Ti" }
];

export const qtaimData = [
  { bond: "Si–O", rho: 0.092, laplacian: 0.42, h: -0.018 },
  { bond: "O→Ti", rho: 0.036, laplacian: 0.18, h: -0.004 }
];

export const sequenceHeatmap = [
  { first: "乙烯", second: "乙烯", value: 90 }
];

export const thesisEntities: ThesisEntity[] = [
  {
    category: "报告核心",
    name: "Si–O",
    chineseName: "Si–O 水解缩合活性",
    evidence: "报告揭示 Si–O 键具有提供后反应交联和网络交联的潜力，但同时带来 O→Ti 毒化风险。",
    source: "报告线索抽取",
    confidence: 0.95
  },
  {
    category: "报告核心",
    name: "Si–C",
    chineseName: "Si–C 侧链稳定性",
    evidence: "报告明确需要验证含硅单体接入 PP 链后，Si–C 键是否会在加工条件下断裂失效。",
    source: "报告线索抽取",
    confidence: 0.9
  },
  {
    category: "报告核心",
    name: "Ziegler–Natta",
    chineseName: "Ziegler-Natta 催化剂",
    evidence: "作为硅烷单体共聚的主体催化剂环境。",
    source: "报告线索抽取",
    confidence: 0.92
  },
  {
    category: "报告核心",
    name: "TEA",
    chineseName: "三乙基铝 (TEA) 预组织",
    evidence: "报告指出 TEA 络合 Si–O/Si–Cl，调控单体向活性中心的导向插入路径。",
    source: "报告线索抽取",
    confidence: 0.88
  },
  {
    category: "报告核心",
    name: "Ti-poisoning",
    chineseName: "Ti 毒化",
    evidence: "O 原子孤对电子可能与 Ti 形成强络合（O→Ti），阻碍 C=C 的生产性配位。",
    source: "报告线索抽取",
    confidence: 0.94
  },
  {
    category: "报告核心",
    name: "Peroxides",
    chineseName: "过氧化物",
    evidence: "用于诱导 PP 自由基网络生成，决定初级自由基提取氢原子的能力。",
    source: "报告线索抽取",
    confidence: 0.97
  },
  {
    category: "报告核心",
    name: "PP beta-scission",
    chineseName: "PP β-断裂",
    evidence: "叔碳大分子自由基易发生降解断链，与接枝交联竞争。",
    source: "报告线索抽取",
    confidence: 0.98
  },
  {
    category: "报告核心",
    name: "LCB",
    chineseName: "长链支化 (LCB)",
    evidence: "有效抑制熔体垂伸，改善 PP 加工性能的关键微观拓扑结构。",
    source: "报告线索抽取",
    confidence: 0.93
  },
  {
    category: "报告核心",
    name: "Crosslinking",
    chineseName: "交联网络",
    evidence: "大分子自由基复合或多官能团硅烷缩合产生的三维网络。",
    source: "报告线索抽取",
    confidence: 0.96
  },
  {
    category: "报告核心",
    name: "Degradation",
    chineseName: "降解",
    evidence: "导致 Mw 降低、MFR 升高的宏观失效表现。",
    source: "报告线索抽取",
    confidence: 0.99
  },
  {
    category: "报告核心",
    name: "Ethylene/Isotacticity/Crystallinity",
    chineseName: "乙烯/等规度/结晶度",
    evidence: "乙烯片段削弱 PP 结晶区，提供过氧化物扩散和自由基存活的微相窗口。",
    source: "报告线索抽取",
    confidence: 0.89
  },
  {
    category: "报告核心",
    name: "Carbonyl Taxonomy",
    chineseName: "羰基三分法",
    evidence: "报告首次提出分离“过氧化物羰基、单体羰基、氧化副产物羰基”以诊断介电性能恶化原因。",
    source: "报告线索抽取",
    confidence: 0.98
  }
];


export const mechanismHypotheses: MechanismHypothesis[] = [
  {
    key: "o-ti-poisoning",
    name: "O→Ti 毒化模型",
    summary: "甲氧基硅烷中的 O 原子与 Ti 非生产性配位，竞争 C=C π 配位并降低有效插入。",
    supportingEvidence: ["MCSOMe/DMOS 设计中 OMe 可作为 Lewis 碱位点。", "若 ΔGpoison < 0，O→Ti 络合物更稳定。"],
    falsification: ["若 n(O)→Ti 很弱且 ΔGpoison 明显为正，则 OMe 不构成主要毒化通道。"],
    requiredData: ["O→Ti complex log", "π-complex log", "n(O)→Ti E(2)", "Ti–O 距离"],
    currentStatus: "当前为软件假说引擎中的待验证模型，需进一步 DFT 支持。",
    confidence: 0.85,
    source: "报告机制抽取"
  },
  {
    key: "carbonyl-taxonomy",
    name: "羰基效应三分法",
    summary: "必须区分三种羰基：过氧化物残留羰基、接枝单体极性羰基、氧化老化副反应羰基，它们对电性能的损耗机制完全不同。",
    supportingEvidence: ["介电损耗随羰基指数上升但不完全线性相关。"],
    falsification: ["若三种羰基的电荷陷阱能级与损耗角正切表现一致，则无需区分。"],
    requiredData: ["FTIR", "Dielectric Loss", "Trap Energy Level"],
    currentStatus: "报告提出的创新假说，已内置至系统验证闭环。",
    confidence: 0.95,
    source: "报告机制抽取"
  },
  {
    key: "radical-competition",
    name: "PP β-scission 与 LCB 竞争模型",
    summary: "PP 自由基体系中，交联、支化与降解始终同时发生；只有调节自由基生存微环境与扩散速率，才能提高有效 LCB 选择性。",
    supportingEvidence: ["MFR 升高伴随少量 gel 出现表明断链与交联同时存在。"],
    falsification: ["若改变过氧化物半衰期不影响 LCB/Scission 比例，则扩散控制失效。"],
    requiredData: ["k_scission", "k_branching", "SAOS 流变", "MFR", "Gel fraction"],
    currentStatus: "自由基动力学引擎核心基石，验证通过。",
    confidence: 0.98,
    source: "报告机制抽取"
  }
];


export const statusChinese = {
  pending: "待计算",
  parsed: "已解析",
  missing: "数据缺失",
  example: "示例数据",
  real: "真实数据",
  failed: "解析失败",
  done: "计算完成",
  inspect: "需要检查",
  favorable: "有利插入",
  competition: "配位竞争",
  poisoned: "Ti 毒化",
  capture: "助剂捕获",
  steric: "位阻主导",
  balanced: "平衡候选",
  post: "后反应潜力高"
};

export const moduleIcon = Binary;


export const catalystModels: CatalystModel[] = [
  {
    key: "MgCl2-TiCl4-Et",
    name: "MgCl2/TiCl4/Et",
    role: "简化负载 Ziegler–Natta 活性中心，用于乙烯插入基准与功能单体插入势垒比较。",
    activeSite: "Ti–Et 生长链 / MgCl2 载体片段",
    thesisLink: "论文 DFT 模型之一，适合建立乙烯体系的插入参照。",
    source: "论文抽取 + 示例占位"
  },
  {
    key: "MgCl2-BMMF-TiCl4-iBU",
    name: "MgCl2/BMMF/TiCl4/iBU",
    role: "给电子体修饰活性中心模型，用于丙烯/功能 α-烯烃体系的位阻与电子效应分解。",
    activeSite: "Ti–iBU 生长链 / BMMF 给电子体环境",
    thesisLink: "论文 DFT 模型之一，可用于丙烯体系和立构/区域插入分析。",
    source: "论文抽取 + 示例占位"
  },
  {
    key: "TEA-guided",
    name: "Monomer···TEA preorganization",
    role: "助催化剂预组织模型，用于比较 Al···Cl、Al←O、Al···C=C 三类络合通道。",
    activeSite: "AlEt3 Lewis 酸中心",
    thesisLink: "论文指出 Al 与氯硅烷取代基相互作用增强可能帮助单体靠近活性中心。",
    source: "论文抽取 + 机制外推"
  }
];

export const experimentalRecords: ExperimentalRecord[] = [
  {
    id: "exp-c4-dcs-ethylene",
    monomer: "C4-DCS",
    catalyst: "MgCl2/TiCl4/TEA",
    polymerization: "乙烯共聚",
    chainLength: "C4",
    activity: 82,
    insertionRatio: 68,
    hexeneContent: null,
    sequenceLength: null,
    meltingPoint: null,
    crystallinity: null,
    transparency: null,
    deltaGBarrier: 12.9,
    deltaGPoison: 8.8,
    stericPenalty: 42,
    electronicGuiding: 78,
    source: "论文趋势抽取 + 示例量化 / MOCK"
  },
  {
    id: "exp-c6-dcs-propylene",
    monomer: "DCS",
    catalyst: "MgCl2/BMMF/TiCl4/iBU",
    polymerization: "丙烯共聚",
    chainLength: "C6",
    activity: 74,
    insertionRatio: 72,
    hexeneContent: null,
    sequenceLength: null,
    meltingPoint: null,
    crystallinity: null,
    transparency: null,
    deltaGBarrier: 13.6,
    deltaGPoison: 7.1,
    stericPenalty: 48,
    electronicGuiding: 83,
    source: "论文趋势抽取 + 示例量化 / MOCK"
  },
  {
    id: "exp-c8-dcs-propylene",
    monomer: "C8-DCS",
    catalyst: "MgCl2/BMMF/TiCl4/iBU",
    polymerization: "丙烯共聚",
    chainLength: "C8",
    activity: 48,
    insertionRatio: 38,
    hexeneContent: null,
    sequenceLength: null,
    meltingPoint: null,
    crystallinity: null,
    transparency: null,
    deltaGBarrier: 17.8,
    deltaGPoison: 6.2,
    stericPenalty: 76,
    electronicGuiding: 75,
    source: "论文趋势抽取 + 示例量化 / MOCK"
  },
  {
    id: "exp-c6-dcs-hexene",
    monomer: "DCS + 1-hexene",
    catalyst: "MgCl2/TiCl4/TEA",
    polymerization: "乙烯/1-己烯/硅烷三元共聚",
    chainLength: "C6",
    activity: 58,
    insertionRatio: 44,
    hexeneContent: 31,
    sequenceLength: 42,
    meltingPoint: 118,
    crystallinity: 36,
    transparency: 72,
    deltaGBarrier: 15.2,
    deltaGPoison: 7.6,
    stericPenalty: 64,
    electronicGuiding: 80,
    source: "论文趋势抽取 + 示例量化 / MOCK"
  }
];

export const dftExperimentScatter = experimentalRecords.map((record) => ({
  name: record.monomer,
  barrier: record.deltaGBarrier,
  activity: record.activity,
  insertion: record.insertionRatio,
  steric: record.stericPenalty,
  electronic: record.electronicGuiding,
  source: record.source
}));

export const chainLengthTrend = experimentalRecords.map((record) => ({
  name: record.chainLength + "-" + record.polymerization.slice(0, 2),
  chain: record.chainLength,
  insertion: record.insertionRatio,
  activity: record.activity,
  barrier: record.deltaGBarrier
}));

export const rankingConsistency = [
  { row: "论文趋势", C4: 82, C6: 90, C8: 54 },
  { row: "DFT 示例", C4: 78, C6: 86, C8: 48 },
  { row: "实验待导入", C4: 0, C6: 0, C8: 0 }
];

export const taskTypes = [
  "孤立单体 opt/freq/NBO",
  "单体单点能精修",
  "²⁹Si GIAO NMR",
  "TEA 络合 Counterpoise",
  "生产性 C=C π-络合物",
  "非生产性 O→Ti 毒化络合物",
  "插入过渡态",
  "IRC 本征反应坐标",
  "水解过渡态",
  "缩合过渡态",
  "片段变形能单点"
];
