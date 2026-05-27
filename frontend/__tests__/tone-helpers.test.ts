import { describe, expect, it } from "vitest";
import {
  chartColors,
  poisonLabel,
  poisonTone,
  rateText,
  toneSurface,
} from "@/components/shared/tone-helpers";

describe("toneSurface", () => {
  it("returns correct classes for green", () => {
    expect(toneSurface("green")).toContain("bg-studio-green");
  });
  it("returns correct classes for red", () => {
    expect(toneSurface("red")).toContain("text-studio-red");
  });
  it("returns correct classes for gray", () => {
    expect(toneSurface("gray")).toContain("bg-studio-panel");
  });
  it("returns correct classes for all tones", () => {
    const tones = ["green", "yellow", "red", "blue", "gray", "violet", "orange"] as const;
    for (const tone of tones) {
      expect(toneSurface(tone)).toBeDefined();
      expect(toneSurface(tone).length).toBeGreaterThan(0);
    }
  });
});

describe("poisonTone", () => {
  it("returns gray for null", () => {
    expect(poisonTone(null)).toBe("gray");
  });
  it("returns green for value > 5", () => {
    expect(poisonTone(10)).toBe("green");
    expect(poisonTone(5.1)).toBe("green");
  });
  it("returns yellow for value 0..5", () => {
    expect(poisonTone(0)).toBe("yellow");
    expect(poisonTone(3)).toBe("yellow");
    expect(poisonTone(5)).toBe("yellow");
  });
  it("returns red for negative values", () => {
    expect(poisonTone(-1)).toBe("red");
    expect(poisonTone(-10)).toBe("red");
  });
});

describe("poisonLabel", () => {
  it("returns 数据缺失 for null", () => {
    expect(poisonLabel(null)).toBe("数据缺失");
  });
  it("returns positive label for > 5", () => {
    expect(poisonLabel(10)).toContain("C=C 插入占优");
  });
  it("returns competition label for 0..5", () => {
    expect(poisonLabel(3)).toContain("竞争");
  });
  it("returns risk label for negative", () => {
    expect(poisonLabel(-5)).toContain("毒化风险");
  });
});

describe("rateText", () => {
  it("returns 待计算 for null", () => {
    expect(rateText(null)).toBe("待计算");
  });
  it("returns 1.0 for value 1", () => {
    expect(rateText(1)).toBe("1.0");
  });
  it("returns exponential for very small values", () => {
    expect(rateText(0.0001)).toContain("e");
  });
  it("returns 2 sig figs for normal values", () => {
    expect(rateText(0.75)).toBe("0.75");
    expect(rateText(0.1)).toBe("0.10");
  });
});

describe("chartColors", () => {
  it("is an array", () => {
    expect(Array.isArray(chartColors)).toBe(true);
  });
  it("has at least 3 colors", () => {
    expect(chartColors.length).toBeGreaterThanOrEqual(3);
  });
  it("contains hsl vars", () => {
    for (const c of chartColors) {
      expect(c).toContain("hsl");
    }
  });
});
