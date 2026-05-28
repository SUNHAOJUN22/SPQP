"use client";

import { useMemo, useState, useTransition } from "react";
import dynamic from "next/dynamic";
import { AnimatePresence, motion } from "framer-motion";
import { ToastContainer } from "@/components/ui/toast";
import { AppTopbar, MobileModuleRail } from "@/components/layout/app-topbar";
import { GroupedSidebar } from "@/components/layout/grouped-sidebar";
import { CommandPalette } from "@/components/shared/command-palette";
import { ErrorBoundary } from "@/components/shared/error-boundary";
import { ModuleLoading } from "@/components/shared/module-loading";
import { moleculeLibrary, navItems } from "@/lib/studio-data";
import { navGroups, StudioProvider, useStudio } from "@/lib/store";
import type { ModuleId } from "@/types/studio";

/* ── Lazy Module Imports ── */
const IntegratedHomePanel = dynamic(() => import("@/components/modules/integrated-home-panel").then((m) => m.IntegratedHomePanel), { ssr: false, loading: () => <ModuleLoading label="整合总控台" /> });
const LiteratureKnowledgeBase = dynamic(() => import("@/components/modules/v2-panels").then((m) => m.LiteratureKnowledgeBase), { ssr: false, loading: () => <ModuleLoading label="论文知识库" /> });
const ExperimentDftComparison = dynamic(() => import("@/components/modules/v2-panels").then((m) => m.ExperimentDftComparison), { ssr: false, loading: () => <ModuleLoading label="实验-DFT 对照" /> });
const MechanismHypothesisEngine = dynamic(() => import("@/components/modules/v2-panels").then((m) => m.MechanismHypothesisEngine), { ssr: false, loading: () => <ModuleLoading label="可证伪机制模型" /> });
const GaussianParserPanel = dynamic(() => import("@/components/modules/gaussian-parser-panel").then((m) => m.GaussianParserPanel), { ssr: false, loading: () => <ModuleLoading label="Gaussian 输出解析" /> });
const MergedUltraPanel = dynamic(() => import("@/components/modules/merged-ultra-panel").then((m) => m.MergedUltraPanel), { ssr: false, loading: () => <ModuleLoading label="合并工作台" /> });
const RadicalPostReactionPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.RadicalPostReactionPanel), { ssr: false, loading: () => <ModuleLoading label="自由基后反应" /> });
const PeroxideLibraryPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.PeroxideLibraryPanel), { ssr: false, loading: () => <ModuleLoading label="过氧化物结构库" /> });
const SiCStabilityPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.SiCStabilityPanel), { ssr: false, loading: () => <ModuleLoading label="Si–C 键稳定性" /> });
const DegradationCrosslinkPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.DegradationCrosslinkPanel), { ssr: false, loading: () => <ModuleLoading label="降解-交联竞争图" /> });
const RadicalKineticsPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.RadicalKineticsPanel), { ssr: false, loading: () => <ModuleLoading label="自由基动力学" /> });
const ResidenceTimeWindowPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.ResidenceTimeWindowPanel), { ssr: false, loading: () => <ModuleLoading label="停留时间窗口" /> });
const EthyleneIsotacticityPanel = dynamic(() => import("@/components/modules/radical-v4-panels").then((m) => m.EthyleneIsotacticityPanel), { ssr: false, loading: () => <ModuleLoading label="乙烯/等规度影响" /> });
const DashboardPanel = dynamic(() => import("@/components/modules/dashboard-panel").then((m) => m.DashboardPanel), { ssr: false, loading: () => <ModuleLoading label="总览驾驶舱" /> });
const MoleculeLibraryPanel = dynamic(() => import("@/components/modules/molecule-library-panel").then((m) => m.MoleculeLibraryPanel), { ssr: false, loading: () => <ModuleLoading label="分子库" /> });
const ScientificComputationPanel = dynamic(() => import("@/components/modules/scientific-computation-panel").then((m) => m.ScientificComputationPanel), { ssr: false, loading: () => <ModuleLoading label="科学计算工作流" /> });
const SimulationConnectorsPanel = dynamic(() => import("@/components/modules/simulation-connectors-panel").then((m) => m.SimulationConnectorsPanel), { ssr: false, loading: () => <ModuleLoading label="科学计算连接器" /> });
const GaussianBuilderPanel = dynamic(() => import("@/components/modules/gaussian-builder-panel").then((m) => m.GaussianBuilderPanel), { ssr: false, loading: () => <ModuleLoading label="Gaussian 输入生成" /> });
const SiOBondLabPanel = dynamic(() => import("@/components/modules/sio-bond-lab-panel").then((m) => m.SiOBondLabPanel), { ssr: false, loading: () => <ModuleLoading label="硅氧键实验室" /> });
const ElectronDensityPanel = dynamic(() => import("@/components/modules/electron-density-panel").then((m) => m.ElectronDensityPanel), { ssr: false, loading: () => <ModuleLoading label="电子云密度" /> });
const ESPPanel = dynamic(() => import("@/components/modules/electron-density-panel").then((m) => m.ESPPanel), { ssr: false, loading: () => <ModuleLoading label="ESP 静电势" /> });
const FukuiPanel = dynamic(() => import("@/components/modules/electron-density-panel").then((m) => m.FukuiPanel), { ssr: false, loading: () => <ModuleLoading label="Fukui 局部反应性" /> });
const DifferenceDensityPanel = dynamic(() => import("@/components/modules/electron-density-panel").then((m) => m.DifferenceDensityPanel), { ssr: false, loading: () => <ModuleLoading label="差分电子密度" /> });
const FrontierOrbitalsPanel = dynamic(() => import("@/components/modules/frontier-orbitals-panel").then((m) => m.FrontierOrbitalsPanel), { ssr: false, loading: () => <ModuleLoading label="前线轨道" /> });
const ChargePopulationPanel = dynamic(() => import("@/components/modules/charge-population-panel").then((m) => m.ChargePopulationPanel), { ssr: false, loading: () => <ModuleLoading label="电荷布居" /> });
const NBOInteractionsPanel = dynamic(() => import("@/components/modules/nbo-interactions-panel").then((m) => m.NBOInteractionsPanel), { ssr: false, loading: () => <ModuleLoading label="NBO 相互作用" /> });
const QTAIMNCIPanel = dynamic(() => import("@/components/modules/qtaim-nci-panel").then((m) => m.QTAIMNCIPanel), { ssr: false, loading: () => <ModuleLoading label="QTAIM / NCI" /> });
const TEAInteractionPanel = dynamic(() => import("@/components/modules/tea-interaction-panel").then((m) => m.TEAInteractionPanel), { ssr: false, loading: () => <ModuleLoading label="TEA 助剂作用" /> });
const TiPoisoningPanel = dynamic(() => import("@/components/modules/ti-poisoning-panel").then((m) => m.TiPoisoningPanel), { ssr: false, loading: () => <ModuleLoading label="Ti 毒化判据" /> });
const InsertionSurfacePanel = dynamic(() => import("@/components/modules/insertion-surface-panel").then((m) => m.InsertionSurfacePanel), { ssr: false, loading: () => <ModuleLoading label="插入反应能量面" /> });
const HydrolysisPanel = dynamic(() => import("@/components/modules/hydrolysis-panel").then((m) => m.HydrolysisPanel), { ssr: false, loading: () => <ModuleLoading label="水解缩合后反应" /> });
const DecisionEnginePanel = dynamic(() => import("@/components/modules/decision-engine-panel").then((m) => m.DecisionEnginePanel), { ssr: false, loading: () => <ModuleLoading label="量子判据引擎" /> });
const McpWorkflowPanel = dynamic(() => import("@/components/modules/mcp-workflow-panel").then((m) => m.McpWorkflowPanel), { ssr: false, loading: () => <ModuleLoading label="MCP 自动化工作流" /> });
const ReportsPanel = dynamic(() => import("@/components/modules/reports-panel").then((m) => m.ReportsPanel), { ssr: false, loading: () => <ModuleLoading label="报告生成" /> });
const DataManagementPanel = dynamic(() => import("@/components/modules/data-management-panel").then((m) => m.DataManagementPanel), { ssr: false, loading: () => <ModuleLoading label="数据管理" /> });
const SettingsPanel = dynamic(() => import("@/components/modules/settings-panel").then((m) => m.SettingsPanel), { ssr: false, loading: () => <ModuleLoading label="系统设置" /> });

/* ── Module Titles ── */
const moduleTitles: Record<ModuleId, { title: string; subtitle: string }> = {
  integrated: { title: "整合总控台", subtitle: "Integrated V3 Command Center" },
  dashboard: { title: "项目总览", subtitle: "Project Overview" },
  literature: { title: "论文与报告知识库", subtitle: "Literature Drive and Evidence Base" },
  library: { title: "分子结构与构象", subtitle: "Molecular Structures and Conformers" },
  experiments: { title: "实验-DFT 对照", subtitle: "Experiment and DFT Correlation" },
  merged: { title: "合并工作台", subtitle: "Merged Si-O Ultra Extensions" },
  radical: { title: "自由基后反应", subtitle: "Peroxide-Induced PP Radical Pathways" },
  peroxide: { title: "过氧化物结构库", subtitle: "Peroxide Structure and Half-Life Library" },
  sic: { title: "Si–C 键稳定性", subtitle: "Si-C Bond Stability Under Radical Processing" },
  degradation: { title: "降解-交联竞争图", subtitle: "PP beta-scission vs Branching/Crosslinking" },
  kinetics: { title: "自由基动力学", subtitle: "Radical Kinetics" },
  residence: { title: "停留时间窗口", subtitle: "Residence Time and Radical Flux Window" },
  microstructure: { title: "乙烯/等规度影响", subtitle: "Ethylene Incorporation and Isotacticity" },
  scientific: { title: "科学计算工作流", subtitle: "Scientific Computation Workflow" },
  connectors: { title: "科学计算连接器", subtitle: "Simulation Connectors" },
  builder: { title: "Gaussian 输入生成", subtitle: "Gaussian Input Builder" },
  parser: { title: "Gaussian 输出解析", subtitle: "Gaussian Output Parser" },
  bond: { title: "硅氧键本征属性", subtitle: "Intrinsic Si–O Bond Descriptors" },
  density: { title: "电子云密度与静电势分析", subtitle: "Electron Density and ESP" },
  esp: { title: "ESP 静电势", subtitle: "Electrostatic Potential" },
  fukui: { title: "Fukui 局部反应性", subtitle: "Fukui Local Reactivity" },
  difference: { title: "差分电子密度", subtitle: "Difference Electron Density" },
  orbitals: { title: "前线轨道与电子云分布", subtitle: "Frontier Orbitals" },
  charges: { title: "电荷分布与布居分析", subtitle: "Charge Population" },
  nbo: { title: "NBO 给体-受体相互作用", subtitle: "NBO Donor-Acceptor Interactions" },
  qtaim: { title: "QTAIM / NCI 弱相互作用分析", subtitle: "QTAIM and NCI/RDG" },
  tea: { title: "助催化剂相互作用", subtitle: "TEA Cocatalyst Interactions" },
  poisoning: { title: "Ti 活性中心毒化分析", subtitle: "Ti Poisoning Criteria" },
  insertion: { title: "反应自由能剖面", subtitle: "Insertion Free-Energy Surface" },
  hydrolysis: { title: "水解缩合与 Si–O–Si 后反应", subtitle: "Hydrolysis and Condensation" },
  mechanisms: { title: "可证伪机制模型", subtitle: "Falsifiable Mechanistic Hypotheses" },
  decision: { title: "量子判据引擎", subtitle: "Quantum Decision Engine" },
  mcp: { title: "MCP 自动化工作流", subtitle: "Safe Model Context Protocol Workflows" },
  reports: { title: "计算报告导出", subtitle: "Chinese Research Report" },
  data: { title: "数据管理", subtitle: "Data Provenance" },
  settings: { title: "系统设置", subtitle: "System Settings" },
};

/* ── Inner Shell ── */
function AppShellInner() {
  const {
    activeModule,
    switchModule,
    selectedMoleculeKey,
    setSelectedMoleculeKey,
    theme,
    toggleTheme,
    toasts,
    dismissToast,
    backendStatus,
    setCommandPaletteOpen,
  } = useStudio();

  const [parserText, setParserText] = useState("");
  const [task, setTask] = useState("孤立单体 opt/freq/NBO");
  const [isSwitching, startModuleSwitch] = useTransition();
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());

  const selected = useMemo(
    () => moleculeLibrary.find((m) => m.key === selectedMoleculeKey) ?? moleculeLibrary[1],
    [selectedMoleculeKey]
  );

  const title = moduleTitles[activeModule];

  function handleSwitchModule(id: ModuleId) {
    startModuleSwitch(() => switchModule(id));
  }

  function toggleGroup(label: string) {
    setCollapsedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  }

  /* breadcrumb */
  const breadcrumb = useMemo(() => {
    const group = navGroups.find((g) => g.ids.includes(activeModule));
    return group ? `${group.label}` : "首页";
  }, [activeModule]);

  /* module router */
  const activeContent = useMemo(() => {
    switch (activeModule) {
      case "integrated": return <IntegratedHomePanel />;
      case "dashboard": return <DashboardPanel selected={selected} onSelect={setSelectedMoleculeKey} />;
      case "literature": return <LiteratureKnowledgeBase />;
      case "library": return <MoleculeLibraryPanel selected={selected} onSelect={setSelectedMoleculeKey} />;
      case "experiments": return <ExperimentDftComparison />;
      case "merged": return <MergedUltraPanel />;
      case "radical": return <RadicalPostReactionPanel />;
      case "peroxide": return <PeroxideLibraryPanel />;
      case "sic": return <SiCStabilityPanel />;
      case "degradation": return <DegradationCrosslinkPanel />;
      case "kinetics": return <RadicalKineticsPanel />;
      case "residence": return <ResidenceTimeWindowPanel />;
      case "microstructure": return <EthyleneIsotacticityPanel />;
      case "scientific": return <ScientificComputationPanel />;
      case "connectors": return <SimulationConnectorsPanel />;
      case "builder": return <GaussianBuilderPanel selected={selected} task={task} setTask={setTask} />;
      case "parser": return <GaussianParserPanel parserText={parserText} setParserText={setParserText} />;
      case "bond": return <SiOBondLabPanel selected={selected} onSelect={setSelectedMoleculeKey} />;
      case "density": return <ElectronDensityPanel />;
      case "esp": return <ESPPanel />;
      case "fukui": return <FukuiPanel />;
      case "difference": return <DifferenceDensityPanel />;
      case "orbitals": return <FrontierOrbitalsPanel />;
      case "charges": return <ChargePopulationPanel />;
      case "nbo": return <NBOInteractionsPanel />;
      case "qtaim": return <QTAIMNCIPanel />;
      case "tea": return <TEAInteractionPanel />;
      case "poisoning": return <TiPoisoningPanel />;
      case "insertion": return <InsertionSurfacePanel />;
      case "hydrolysis": return <HydrolysisPanel />;
      case "mechanisms": return <MechanismHypothesisEngine />;
      case "decision": return <DecisionEnginePanel />;
      case "mcp": return <McpWorkflowPanel />;
      case "reports": return <ReportsPanel />;
      case "data": return <DataManagementPanel />;
      case "settings": return <SettingsPanel />;
      default: return <DashboardPanel selected={selected} onSelect={setSelectedMoleculeKey} />;
    }
  }, [activeModule, parserText, selected, task, setSelectedMoleculeKey]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-studio-ink text-studio-text" aria-label="硅氧键催化量子研究平台">
      <div className="relative mx-auto flex max-w-[1920px]">
        <GroupedSidebar
          activeModule={activeModule}
          onSwitch={handleSwitchModule}
          collapsedGroups={collapsedGroups}
          onToggleGroup={toggleGroup}
        />

        {/* ── Content ── */}
        <section className="min-w-0 flex-1 px-6 py-4" role="main">
          <AppTopbar
            title={title.title}
            subtitle={title.subtitle}
            breadcrumb={breadcrumb}
            backendStatus={backendStatus}
            theme={theme}
            onToggleTheme={toggleTheme}
            onOpenSearch={() => setCommandPaletteOpen(true)}
            selectedMoleculeKey={selectedMoleculeKey}
            onSelectMolecule={setSelectedMoleculeKey}
            moleculeKeys={moleculeLibrary.map((m) => m.key)}
          />
          <MobileModuleRail activeModule={activeModule} items={navItems} onSwitch={handleSwitchModule} />

          {/* Switching indicator */}
          <AnimatePresence>
            {isSwitching ? (
              <motion.div
                className="pointer-events-none fixed right-5 top-16 z-30 rounded-lg border border-studio-line/60 bg-studio-panel px-4 py-2 text-sm font-medium text-studio-muted shadow-elevation-2"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
              >
                正在切换模块…
              </motion.div>
            ) : null}
          </AnimatePresence>

          {/* Module content */}
          <AnimatePresence mode="wait">
            <motion.div
              className="content-auto"
              key={activeModule}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
            >
              <ErrorBoundary fallbackModule={title.title} key={`eb-${activeModule}`}>
                {activeContent}
              </ErrorBoundary>
            </motion.div>
          </AnimatePresence>
        </section>
      </div>

      {/* Global overlays */}
      <CommandPalette />
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </main>
  );
}

/* ── Root Shell (with Provider) ── */
export function AppShell() {
  return (
    <StudioProvider>
      <AppShellInner />
    </StudioProvider>
  );
}
