import { describe, expect, it } from "vitest";
import {
  DISCRIMINATION_OHLC,
  ENTRY_SL_2X_TRIGGER_ABCD_FIXTURES,
  TRIGGER_FORMS,
  abcdEqualityObservation,
  candidateAnchors,
  entryAndLeg2AreDistinct,
  halfTargetCandidates,
} from "../research/fixtures/sp2l_source_discrimination_entry_sl_2x_trigger_abcd_v1.js";

describe("SP2L source-discrimination fixtures", () => {
  it("keeps the fixture questions explicitly unresolved/partial", () => {
    expect(ENTRY_SL_2X_TRIGGER_ABCD_FIXTURES).toHaveLength(6);
    expect(ENTRY_SL_2X_TRIGGER_ABCD_FIXTURES.map((f) => f.canonicalStatus)).toEqual([
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
      "PARTIAL",
      "UNRESOLVED",
      "UNRESOLVED",
    ]);
  });

  it("preserves the source trigger family without selecting one canonical trigger", () => {
    expect(TRIGGER_FORMS).toEqual([
      "one-candle",
      "two-candle",
      "three-candle",
      "bar",
      "key-bar",
    ]);
  });

  it("separates entry from Leg-2 start when the fixture provides distinct anchors", () => {
    expect(entryAndLeg2AreDistinct(100, 104)).toBe(true);
    expect(entryAndLeg2AreDistinct(100, 100)).toBe(false);
  });

  it("keeps competing half-target 2X anchors observable", () => {
    const c = halfTargetCandidates(100, 104, 120);
    expect(c.fromEntry).toBe(110);
    expect(c.fromStructuralAnchor).toBe(112);
    expect(c.fromEntry).not.toBe(c.fromStructuralAnchor);
  });

  it("does not invent an AB=CD tolerance", () => {
    expect(abcdEqualityObservation(100, 110, 120, 130)).toBe(true);
    expect(abcdEqualityObservation(100, 110, 120, 130.01)).toBe(false);
  });

  it("keeps wick/body/pivot anchor models distinct", () => {
    const values = {
      A_wick: 99,
      B_wick: 110,
      C_wick: 104,
      D_wick: 115,
      A_body: 100,
      B_body: 108,
      C_body: 105,
      D_body: 113,
      A_pivot: 101,
      B_pivot: 109,
      C_pivot: 103,
      D_pivot: 114,
    };

    expect(candidateAnchors(values, "wick")).not.toEqual(candidateAnchors(values, "body"));
    expect(candidateAnchors(values, "body")).not.toEqual(candidateAnchors(values, "structural-pivot"));
  });

  it("provides deterministic OHLC fixture inputs", () => {
    expect(DISCRIMINATION_OHLC).toHaveLength(3);
    expect(DISCRIMINATION_OHLC[0]!.low).toBe(99);
    expect(DISCRIMINATION_OHLC[2]!.high).toBe(115);
  });
});
