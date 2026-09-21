import { describe, expect, it } from "vitest";
import { LEG1_ANCHOR_MATRIX } from "../research/fixtures/sp2l_leg1_anchor_matrix_v1.js";

describe("SP2L Leg-1 anchor hypothesis matrix", () => {
  it("keeps the three plausible anchor families distinct", () => {
    expect(new Set(LEG1_ANCHOR_MATRIX.map(x => x.hypothesis)).size).toBe(3);
  });

  it("keeps bullish and bearish observations mirrored", () => {
    expect(LEG1_ANCHOR_MATRIX.filter(x => x.direction === "BUY")).toHaveLength(3);
    expect(LEG1_ANCHOR_MATRIX.filter(x => x.direction === "SELL")).toHaveLength(3);
  });

  it("never promotes an OHLC anchor hypothesis to canonical", () => {
    expect(LEG1_ANCHOR_MATRIX.every(x =>
      x.sourceStatus === "STRUCTURE_SUPPORTED_FIELD_UNRESOLVED" &&
      x.canonicalEligible === false
    )).toBe(true);
  });
});
