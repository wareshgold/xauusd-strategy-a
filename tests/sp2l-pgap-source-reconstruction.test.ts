import { describe, expect, it } from "vitest";
import {
  PGAP_SOURCE_FIXTURES,
  bearishGapPrimitive,
  bullishGapPrimitive,
} from "../research/fixtures/sp2l_pgap_source_reconstruction_v1.js";

describe("SP2L P-Gap source reconstruction fixtures", () => {
  it("covers the three source-described bullish construction families", () => {
    expect(PGAP_SOURCE_FIXTURES.slice(0, 3).map((x) => x.variant)).toEqual([
      "breakout-follow-through-gap",
      "higher-lows-gap",
      "three-candle-spike",
    ]);
  });

  it("passes every positive bullish fixture through the reconstructed primitive", () => {
    for (const fixture of PGAP_SOURCE_FIXTURES.filter((x) => x.direction === "bullish")) {
      const [i, j] = fixture.gapPair;
      const a = fixture.candles[i];
      const b = fixture.candles[j];
      expect(a).toBeDefined();
      expect(b).toBeDefined();
      expect(bullishGapPrimitive(a!, b!)).toBe(fixture.expectedPrimitive);
    }
  });

  it("rejects overlap and equality for the bullish primitive", () => {
    expect(PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-004")?.expectedPrimitive).toBe(false);
    expect(PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-005")?.expectedPrimitive).toBe(false);
  });

  it("keeps late/E-Gap-like and fixed-index cases separate from qualification", () => {
    const late = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-006")!;
    const fixedIndex = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-007")!;
    expect(late.expectedPrimitive).toBe(true);
    expect(fixedIndex.expectedPrimitive).toBe(true);
    expect(late.qualificationStatus).toBe("UNRESOLVED");
    expect(fixedIndex.qualificationStatus).toBe("UNRESOLVED");
  });

  it("tests the bearish mirror as a geometric primitive only", () => {
    const fixture = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-008")!;
    const [i, j] = fixture.gapPair;
    expect(bearishGapPrimitive(fixture.candles[i]!, fixture.candles[j]!)).toBe(true);
    expect(fixture.canonicalEligible).toBe(false);
  });

  it("never marks a P-Gap fixture canonical", () => {
    expect(PGAP_SOURCE_FIXTURES.every((x) =>
      x.canonicalEligible === false && x.qualificationStatus === "UNRESOLVED"
    )).toBe(true);
  });

  it("does not encode the old fixed-index formula as the reconstructed primitive", () => {
    const fixedIndex = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-007")!;
    expect(fixedIndex.gapPair).toEqual([3, 4]);
    expect(fixedIndex.expectedPrimitive).toBe(true);
  });
});
