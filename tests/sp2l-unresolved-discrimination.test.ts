import { describe, expect, it } from "vitest";
import { SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES } from "../research/fixtures/sp2l_unresolved_discrimination_v1.js";

describe("SP2L unresolved discrimination fixture guards", () => {
  it("covers all unresolved families", () => {
    const families = new Set(SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES.map((x: { family: string }) => x.family));
    const expectedFamilies = ["F08","F09","F10","F11","F12","F13","F14","F15","PGAP"];
    expect([...families].sort()).toEqual(expectedFamilies);
    expect(SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES).toHaveLength(18);
  });

  it("keeps every unresolved fixture non-canonical and hypothesis-discriminating", () => {
    for (const c of SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES) {
      expect(c.expectedStatus, c.id).toBe("UNRESOLVED");
      expect(c.canonicalEligible, c.id).toBe(false);
      expect(c.hypothesisA, c.id).not.toBe(c.hypothesisB);
    }
  });
});
