import { describe, expect, it } from "vitest";
import { clamp, cn, formatEnergy } from "@/lib/utils";

describe("cn (class merge)", () => {
  it("merges simple class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });
  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });
  it("deduplicates tailwind classes", () => {
    // twMerge deduplicates conflicting tailwind
    expect(cn("p-2", "p-4")).toBe("p-4");
  });
  it("handles undefined/null", () => {
    expect(cn("base", undefined, null)).toBe("base");
  });
});

describe("formatEnergy", () => {
  it("returns 待计算 for null", () => {
    expect(formatEnergy(null)).toBe("待计算");
  });
  it("returns 待计算 for undefined", () => {
    expect(formatEnergy(undefined)).toBe("待计算");
  });
  it("returns 待计算 for NaN", () => {
    expect(formatEnergy(NaN)).toBe("待计算");
  });
  it("formats positive with + sign", () => {
    expect(formatEnergy(5.67)).toBe("+5.7");
  });
  it("formats negative without + sign", () => {
    expect(formatEnergy(-3.14)).toBe("-3.1");
  });
  it("formats zero", () => {
    expect(formatEnergy(0)).toBe("0.0");
  });
  it("respects digits parameter", () => {
    expect(formatEnergy(1.234, 2)).toBe("+1.23");
    expect(formatEnergy(-1.234, 0)).toBe("-1");
  });
});

describe("clamp", () => {
  it("clamps within range", () => {
    expect(clamp(5, 0, 10)).toBe(5);
  });
  it("clamps to min", () => {
    expect(clamp(-5, 0, 10)).toBe(0);
  });
  it("clamps to max", () => {
    expect(clamp(15, 0, 10)).toBe(10);
  });
  it("handles edge at boundaries", () => {
    expect(clamp(0, 0, 10)).toBe(0);
    expect(clamp(10, 0, 10)).toBe(10);
  });
});
