import { describe, expect, it } from "vitest";
import {
  NIST_CONSTANTS,
  calculateEyringRate,
  calculateSelectivity,
  AdvancedGpr,
  VmcPreviewEngine
} from "@/lib/advanced-science";

describe("数理严谨性测试 - 物理常数", () => {
  it("气体常数 R 取值正确 (kcal/mol*K)", () => {
    // R = 8.314462618 J/(mol*K) / 4184 J/kcal = 0.001987204
    expect(NIST_CONSTANTS.rKcalMolK).toBeCloseTo(0.001987204, 7);
  });
  it("玻尔兹曼常数 kB 取值正确 (J/K)", () => {
    expect(NIST_CONSTANTS.kB).toBeCloseTo(1.380649e-23, 29);
  });
  it("普朗克常数 h 取值正确 (J*s)", () => {
    expect(NIST_CONSTANTS.h).toBeCloseTo(6.62607015e-34, 42);
  });
});

describe("数理严谨性测试 - Eyring 方程", () => {
  it("计算标准室温 (298.15K) 下，势垒 20 kcal/mol 的速率常数", () => {
    // Prefactor: (1.380649e-23 * 298.15) / 6.62607015e-34 = 6.2124e12
    // Exponent: -20 / (0.001987204 * 298.15) = -33.756
    // Rate = 6.2124e12 * exp(-33.756) ≈ 0.0135 s^-1
    const rate = calculateEyringRate(20, 298.15);
    expect(rate).toBeCloseTo(0.0135, 3);
  });

  it("势垒为 0 时，速率应等于指前因子", () => {
    const rate = calculateEyringRate(0, 300);
    const expectedPrefactor = (NIST_CONSTANTS.kB * 300) / NIST_CONSTANTS.h;
    expect(rate).toBeCloseTo(expectedPrefactor, -10);
  });

  it("极限边界测试：传入 T = -100K 应当自动 fallback 至保护边界，避免 NaN", () => {
    const rate = calculateEyringRate(10, -100);
    expect(Number.isNaN(rate)).toBe(false);
  });

  it("极限边界测试：传入极大势垒 deltaG = 9999", () => {
    const rate = calculateEyringRate(9999, 300);
    expect(Number.isNaN(rate)).toBe(false);
    expect(rate).toBeGreaterThanOrEqual(0);
  });
});

describe("数理严谨性测试 - 玻尔兹曼选择性", () => {
  it("能差为 0 时，选择性应为 50%", () => {
    const sel = calculateSelectivity(10, 10, 298.15);
    expect(sel).toBeCloseTo(50.0, 2);
  });

  it("能差约为 1.364 kcal/mol (常温下 RT*ln10) 时，选择性应约为 90.9% (即 10:1)", () => {
    // RT at 298.15K = 0.59248. 0.59248 * ln(10) = 1.3642
    const sel = calculateSelectivity(0, 1.3642, 298.15);
    expect(sel).toBeCloseTo(90.9, 1);
  });

  it("大能差时，选择性应趋近 100%", () => {
    const sel = calculateSelectivity(0, 10, 298.15);
    expect(sel).toBeCloseTo(100.0, 2);
  });
});

describe("数理严谨性测试 - 高斯过程回归 (GPR)", () => {
  it("在训练点处的预测应接近真实值且不确定度趋近于零 (真实 GPR 行为)", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[1], [2], [3]], [10, 20, 30]);
    const p = gpr.predict([2]);
    expect(p.mean).toBeCloseTo(20, 1);
    // 真实的 GPR 在训练点处的方差受限于 noiseVariance
    expect(p.variance).toBeLessThan(0.001);
  });

  it("远离训练点时，方差/不确定度应增大", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    gpr.train([[1], [2], [3]], [10, 20, 30]);
    const pClose = gpr.predict([2.1]);
    const pFar = gpr.predict([10]);
    expect(pFar.variance).toBeGreaterThan(pClose.variance);
  });

  it("极限边界测试：传入完全相等的矩阵，应当触发 1e-12 保护，不抛出异常", () => {
    const gpr = new AdvancedGpr(1.0, 1e-6);
    expect(() => {
      gpr.train([[1], [1], [1]], [10, 10, 10]);
    }).not.toThrow();
    const p = gpr.predict([1]);
    expect(Number.isNaN(p.mean)).toBe(false);
  });
});

describe("数理严谨性测试 - VMC Metropolis 采样", () => {
  it("采样过程接受率应收敛在合理范围并返回统计结果", () => {
    const vmc = new VmcPreviewEngine(2); // 2 电子
    const result = vmc.run(500);
    // VMC block average 应该计算标准误
    expect(result.meanEnergyHartree).toBeDefined();
    expect(result.stdErrorHartree).toBeGreaterThanOrEqual(0);
    expect(result.acceptanceRatio).toBeGreaterThan(0);
    expect(result.acceptanceRatio).toBeLessThan(1);
    expect(result.samples).toBe(500);
  });
});
