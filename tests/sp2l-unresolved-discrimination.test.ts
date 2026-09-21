import { SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES } from "../research/fixtures/sp2l_unresolved_discrimination_v1";

describe("SP2L unresolved discrimination coverage", () => {
  it("covers every unresolved executable family without canonicalizing it", () => {
    const families = new Set(SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES.map(x => x.family));
    expect([...families].sort()).toEqual(["F08","F09","F10","F11","F12","F13","F14","F15","PGAP"]);
    expect(SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES).toHaveLength(18);
    for (const c of SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES) {
      expect(c.expectedStatus).toBe("UNRESOLVED");
      expect(c.canonicalEligible).toBe(false);
    }
  });

  it("keeps competing hypotheses explicit", () => {
    for (const c of SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES) {
      expect(c.hypothesisA).not.toBe(c.hypothesisB);
    }
  });
});
