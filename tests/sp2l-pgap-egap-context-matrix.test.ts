import { describe, expect, it } from "vitest";
import { PGAP_EGAP_CONTEXT_MATRIX, validateContextMatrixFixture } from "../research/fixtures/sp2l_pgap_egap_context_matrix_v1.js";

describe("P-Gap / E-Gap context matrix", () => {
  it("covers early, late, same-geometry, and negative controls", () => {
    expect(PGAP_EGAP_CONTEXT_MATRIX.map(x => x.context)).toEqual([
      "early-pgap-shaped","late-egap-shaped","same-geometry-different-context",
      "no-gap-control","overlap-control","equality-control"
    ]);
  });

  it("validates every fixture without promoting qualification", () => {
    expect(PGAP_EGAP_CONTEXT_MATRIX.every(validateContextMatrixFixture)).toBe(true);
  });

  it("proves the same gap geometry can exist in different context classes", () => {
    const early = PGAP_EGAP_CONTEXT_MATRIX.find(x => x.id === "CTX-001")!;
    const same = PGAP_EGAP_CONTEXT_MATRIX.find(x => x.id === "CTX-003")!;
    expect(early.candles).toEqual(same.candles);
    expect(early.gapPair).toEqual(same.gapPair);
    expect(early.expectedGapPrimitive).toBe(same.expectedGapPrimitive);
    expect(early.expectedQualification).toBe("UNRESOLVED");
    expect(same.expectedQualification).toBe("UNRESOLVED");
  });

  it("rejects overlap and equality at the primitive layer", () => {
    expect(PGAP_EGAP_CONTEXT_MATRIX.find(x => x.id === "CTX-005")!.expectedGapPrimitive).toBe(false);
    expect(PGAP_EGAP_CONTEXT_MATRIX.find(x => x.id === "CTX-006")!.expectedGapPrimitive).toBe(false);
  });
});
