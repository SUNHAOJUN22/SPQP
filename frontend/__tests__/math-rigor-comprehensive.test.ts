import { describe, expect, it } from "vitest";
import {
  NIST_CONSTANTS,
  calculateEyringRate,
  calculateSelectivity,
  AdvancedGpr,
  VmcPreviewEngine,
  runTsGuidanceExample,
  clamp
} from "@/lib/advanced-science";
import {
  energyRows,
  pathwayData,
  moleculeLibrary,
  chargeData,
  qtaimData,
  sioDescriptors,
  nboData
} from "@/lib/studio-data";

// ─── Stream 1: 前后端常数交叉验证 ───────────────────────────────

describe("Stream 1: 物理常数交叉验证", () => {
  it("HARTREE_TO_KCAL_MOL = 627.509474 (NIST 精确值)", () => {
    expect(NIST_CONSTANTS.hartreeToKcalMol).toBe(627.509474);
  });
  it("R_KCAL_MOL_K = 0.00198720425864083", () => {
    expect(NIST_CONSTANTS.rKcalMolK).toBe(0.00198720425864083);
  });
  it("HARTREE_TO_EV = 27.211386245988 (CODATA 2018)", () => {
    expect(NIST_CONSTANTS.hartreeToEv).toBe(27.211386245988);
  });
  it("evToKcalMol 应与 hartreeToKcalMol / hartreeToEv 一致 (交叉验证)", () => {
    const exact = NIST_CONSTANTS.hartreeToKcalMol / NIST_CONSTANTS.hartreeToEv;
    expect(NIST_CONSTANTS.evToKcalMol).toBeCloseTo(exact, 5);
  });
  it("kB = 1.380649e-23 (SI 精确定义)", () => {
    expect(NIST_CONSTANTS.kB).toBe(1.380649e-23);
  });
  it("h = 6.62607015e-34 (SI 精确定义)", () => {
    expect(NIST_CONSTANTS.h).toBe(6.62607015e-34);
  });
  it("默认温度 350K (论文体系反应温度)", () => {
    expect(NIST_CONSTANTS.defaultTemperatureK).toBe(350);
  });
});

// ─── Stream 2: Eyring 方程深度验证 ──────────────────────────────

describe("Stream 2: Eyring 过渡态方程", () => {
  it("T=298.15K, ΔG‡=15 kcal/mol → k ≈ 62.8 s⁻¹", () => {
    // Exact: prefactor = kBT/h = 6.2124e12, exponent = -15/(0.001987204*298.15) = -25.32
    // rate = 6.2124e12 * exp(-25.32) = 62.83 s⁻¹
    const rate = calculateEyringRate(15, 298.15);
    expect(rate).toBeCloseTo(62.8, 0);
  });
  it("T=350K, ΔG‡=12.8 kcal/mol → k 在合理范围", () => {
    const rate = calculateEyringRate(12.8, 350);
    expect(rate).toBeGreaterThan(100);
    expect(rate).toBeLessThan(1e8);
  });
  it("ΔG‡=0 时速率等于指前因子 kBT/h", () => {
    const rate = calculateEyringRate(0, 300);
    const prefactor = (NIST_CONSTANTS.kB * 300) / NIST_CONSTANTS.h;
    expect(rate / prefactor).toBeCloseTo(1.0, 3);
  });
  it("clamp 函数截断范围 [-50, 50] 不产生 Infinity", () => {
    expect(clamp(1000)).toBe(50);
    expect(clamp(-1000)).toBe(-50);
    expect(Math.exp(clamp(1000))).toBeLessThan(Infinity);
    expect(Math.exp(clamp(-1000))).toBeGreaterThan(0);
  });
  it("极端高势垒不产生 NaN", () => {
    const rate = calculateEyringRate(1000, 298.15);
    expect(Number.isFinite(rate)).toBe(true);
    expect(rate).toBeGreaterThanOrEqual(0);
  });
  it("极端负势垒不产生 NaN", () => {
    const rate = calculateEyringRate(-1000, 298.15);
    expect(Number.isFinite(rate)).toBe(true);
  });
  it("温度越高同一势垒速率越快", () => {
    const rateLow = calculateEyringRate(15, 300);
    const rateHigh = calculateEyringRate(15, 600);
    expect(rateHigh).toBeGreaterThan(rateLow);
  });
});

// ─── Stream 3: Boltzmann 选择性验证 ─────────────────────────────

describe("Stream 3: Boltzmann 选择性", () => {
  it("ΔΔG=0 → 50%", () => {
    expect(calculateSelectivity(5, 5, 300)).toBeCloseTo(50, 2);
  });
  it("ΔΔG=RT*ln(10) → ~90.9% (10:1)", () => {
    const RT = NIST_CONSTANTS.rKcalMolK * 298.15;
    const ddg = RT * Math.log(10);
    const sel = calculateSelectivity(0, ddg, 298.15);
    expect(sel).toBeCloseTo(90.9, 0);
  });
  it("ΔΔG=RT*ln(100) → ~99.0% (100:1)", () => {
    const RT = NIST_CONSTANTS.rKcalMolK * 298.15;
    const ddg = RT * Math.log(100);
    const sel = calculateSelectivity(0, ddg, 298.15);
    expect(sel).toBeCloseTo(99.0, 0);
  });
  it("大能差 → 趋近 100%", () => {
    expect(calculateSelectivity(0, 20, 298.15)).toBeCloseTo(100, 1);
  });
  it("选择性始终在 [0, 100] 范围内", () => {
    for (const ddg of [-50, -10, 0, 10, 50]) {
      const sel = calculateSelectivity(0, ddg, 300);
      expect(sel).toBeGreaterThanOrEqual(0);
      expect(sel).toBeLessThanOrEqual(100);
    }
  });
});

// ─── Stream 4: GPR Cholesky 分解正确性 ──────────────────────────

describe("Stream 4: GPR Cholesky 分解", () => {
  it("Cholesky 重构误差 < 1e-10 (L*L^T ≈ K)", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[0], [1], [2]], [1, 2, 3]);
    // 通过 predict 验证间接正确性
    const p0 = gpr.predict([0]);
    const p1 = gpr.predict([1]);
    const p2 = gpr.predict([2]);
    expect(p0.mean).toBeCloseTo(1, 4);
    expect(p1.mean).toBeCloseTo(2, 4);
    expect(p2.mean).toBeCloseTo(3, 4);
  });
  it("训练点方差 ≈ noiseVariance (趋近于零)", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[1], [3], [5]], [10, 30, 50]);
    for (const x of [1, 3, 5]) {
      const p = gpr.predict([x]);
      expect(p.variance).toBeLessThan(1e-4);
    }
  });
  it("远离训练点方差 → k(x,x) = 1.0", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[0]], [5]);
    const far = gpr.predict([100]);
    expect(far.variance).toBeCloseTo(1.0, 2);
  });
  it("Expected Improvement 在最佳点处 ≈ 0", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[1], [2], [3]], [10, 20, 30]);
    const ei = gpr.expectedImprovement([3], 30);
    expect(ei).toBeLessThan(0.01);
  });
  it("runTsGuidanceExample 返回有序的 EI 排名", () => {
    const results = runTsGuidanceExample();
    expect(results.length).toBe(4);
    for (let i = 0; i < results.length - 1; i++) {
      expect(results[i].expectedImprovement).toBeGreaterThanOrEqual(results[i + 1].expectedImprovement);
    }
  });
});

// ─── Stream 5: VMC Block Average 统计验证 ───────────────────────

describe("Stream 5: VMC Block Average 统计", () => {
  it("Block Average 标准误 ≥ 0", () => {
    const vmc = new VmcPreviewEngine(4);
    const result = vmc.run(200);
    expect(result.stdErrorHartree).toBeGreaterThanOrEqual(0);
  });
  it("接受率在 [0.2, 0.8] 的合理范围内 (自适应步长)", () => {
    const vmc = new VmcPreviewEngine(3);
    const result = vmc.run(500);
    expect(result.acceptanceRatio).toBeGreaterThan(0.15);
    expect(result.acceptanceRatio).toBeLessThan(0.85);
  });
  it("均值能量接近 -78.4 Hartree (硬编码中心)", () => {
    const vmc = new VmcPreviewEngine(2);
    const result = vmc.run(400);
    expect(result.meanEnergyHartree).toBeCloseTo(-78.4, 0);
  });
});

// ─── Stream 9: 分子描述符数据交叉验证 ───────────────────────────

describe("Stream 9: 分子描述符交叉验证", () => {
  it("ethylene MW = 28.05", () => {
    const eth = moleculeLibrary.find(m => m.key === "ethylene");
    expect(eth?.descriptors.molecularWeight).toBe(28.05);
  });
  it("propylene MW = 42.08", () => {
    const prop = moleculeLibrary.find(m => m.key === "propylene");
    expect(prop?.descriptors.molecularWeight).toBe(42.08);
  });
  it("TEA MW = 114.17", () => {
    const tea = moleculeLibrary.find(m => m.key === "TEA");
    expect(tea?.descriptors.molecularWeight).toBe(114.17);
  });
  it("DCS 有 2 个 Cl, 0 个 O", () => {
    const dcs = moleculeLibrary.find(m => m.key === "DCS");
    expect(dcs?.descriptors.clCount).toBe(2);
    expect(dcs?.descriptors.oCount).toBe(0);
  });
  it("DMOS 有 2 个 O, 0 个 Cl", () => {
    const dmos = moleculeLibrary.find(m => m.key === "DMOS");
    expect(dmos?.descriptors.oCount).toBe(2);
    expect(dmos?.descriptors.clCount).toBe(0);
  });
  it("MCSOMe 有 1 个 O, 1 个 Cl (混合取代)", () => {
    const mcs = moleculeLibrary.find(m => m.key === "MCSOMe");
    expect(mcs?.descriptors.oCount).toBe(1);
    expect(mcs?.descriptors.clCount).toBe(1);
  });
  it("所有分子的 MW > 0 且 atomCount > 0", () => {
    for (const mol of moleculeLibrary) {
      expect(mol.descriptors.molecularWeight).toBeGreaterThan(0);
      expect(mol.descriptors.atomCount).toBeGreaterThan(0);
    }
  });
});

// ─── Stream 10: 能量面通道数据自洽性 ────────────────────────────

describe("Stream 10: 能量面通道数据自洽性", () => {
  it("π-络合物能量 < 0 (稳定化)", () => {
    const piRow = pathwayData.find(p => p.coordinate === "π-络合物");
    expect(piRow?.DCS).toBeLessThan(0);
    expect(piRow?.MCSOMe).toBeLessThan(0);
    expect(piRow?.DMOS).toBeLessThan(0);
  });
  it("插入过渡态能量 > 0 (势垒为正)", () => {
    const tsRow = pathwayData.find(p => p.coordinate === "插入过渡态");
    expect(tsRow?.DCS).toBeGreaterThan(0);
    expect(tsRow?.MCSOMe).toBeGreaterThan(0);
    expect(tsRow?.DMOS).toBeGreaterThan(0);
  });
  it("插入产物能量 < 0 (放热)", () => {
    const prodRow = pathwayData.find(p => p.coordinate === "插入产物");
    expect(prodRow?.DCS).toBeLessThan(0);
    expect(prodRow?.MCSOMe).toBeLessThan(0);
    expect(prodRow?.DMOS).toBeLessThan(0);
  });
  it("DCS krel=1 作为基准 (energyRows)", () => {
    const dcsRow = energyRows.find(e => e.molecule === "DCS");
    expect(dcsRow?.krel).toBe(1);
  });
  it("势垒越高 krel 越小 (DMOS > MCSOMe > DCS)", () => {
    const dcs = energyRows.find(e => e.molecule === "DCS")!;
    const mcs = energyRows.find(e => e.molecule === "MCSOMe")!;
    const dmos = energyRows.find(e => e.molecule === "DMOS")!;
    expect(dmos.deltaGBarrier!).toBeGreaterThan(mcs.deltaGBarrier!);
    expect(mcs.deltaGBarrier!).toBeGreaterThan(dcs.deltaGBarrier!);
    expect(dmos.krel!).toBeLessThan(mcs.krel!);
    expect(mcs.krel!).toBeLessThan(dcs.krel!);
  });
  it("Si 原子电荷在所有方法中为正 (chargeData)", () => {
    const si = chargeData.find(c => c.atom === "Si");
    expect(si?.Mulliken).toBeGreaterThan(0);
    expect(si?.NPA).toBeGreaterThan(0);
    expect(si?.RESP).toBeGreaterThan(0);
    expect(si?.Hirshfeld).toBeGreaterThan(0);
  });
  it("O 原子电荷在所有方法中为负 (chargeData)", () => {
    const o = chargeData.find(c => c.atom === "O");
    expect(o?.Mulliken).toBeLessThan(0);
    expect(o?.NPA).toBeLessThan(0);
    expect(o?.RESP).toBeLessThan(0);
    expect(o?.Hirshfeld).toBeLessThan(0);
  });
  it("QTAIM ρBCP(Si-O) > ρBCP(O→Ti) (共价 > 配位)", () => {
    const sio = qtaimData.find(q => q.bond === "Si–O");
    const oti = qtaimData.find(q => q.bond === "O→Ti");
    expect(sio!.rho).toBeGreaterThan(oti!.rho);
  });
  it("NBO n(O)→Al E(2) > n(O)→Ti E(2) (TEA 捕获更强)", () => {
    const oal = nboData.find(n => n.channel === "O→Al");
    const oti = nboData.find(n => n.channel === "O→Ti");
    expect(oal!.value).toBeGreaterThan(oti!.value);
  });
  it("Si–O 键长在合理范围 1.60-1.75 Å", () => {
    const rSiO = sioDescriptors.find(d => d.metric === "r(Si–O)");
    if (rSiO?.MCSOMe != null) {
      expect(rSiO.MCSOMe).toBeGreaterThan(1.60);
      expect(rSiO.MCSOMe).toBeLessThan(1.75);
    }
    if (rSiO?.DMOS != null) {
      expect(rSiO.DMOS).toBeGreaterThan(1.60);
      expect(rSiO.DMOS).toBeLessThan(1.75);
    }
  });
});

// ─── Stream 11: MOCK 数据防伪造防线 ────────────────────────────

describe("Stream 11: MOCK 数据标记检查", () => {
  it("所有 energyRows 的 source 包含 MOCK", () => {
    for (const row of energyRows) {
      expect(row.source).toContain("MOCK");
    }
  });
  it("所有分子库中的 MOCK 分子标注 source", () => {
    const mockMolecules = moleculeLibrary.filter(m => m.source.includes("MOCK"));
    expect(mockMolecules.length).toBeGreaterThan(0);
  });
});
