import { F13_FIXTURES, f13RelationIsExact, validateF13Fixture } from "../../research/harness/sp2l_f13_2x_synthetic_fixtures";

describe("SP2L F13 2X synthetic fixture gate", () => {
  it("contains all 15 fixture classes", () => {
    expect(F13_FIXTURES).toHaveLength(15);
    expect(new Set(F13_FIXTURES.map(f => f.id)).size).toBe(15);
  });

  it("accepts only the source-confirmed 50% relationship", () => {
    expect(f13RelationIsExact(F13_FIXTURES[0])).toBe(true);
    expect(f13RelationIsExact(F13_FIXTURES[1])).toBe(true);
    expect(f13RelationIsExact(F13_FIXTURES[2])).toBe(false);
  });

  it("keeps every fixture out of canonical and production eligibility", () => {
    for (const fixture of F13_FIXTURES) {
      expect(fixture.canonicalEligible).toBe(false);
      expect(fixture.productionEligible).toBe(false);
      expect(validateF13Fixture(fixture)).toBe(true);
    }
  });

  it("keeps lifecycle variants unresolved and distinguishable", () => {
    const lifecycle = F13_FIXTURES.filter(f => f.id >= "F13-005");
    expect(lifecycle.every(f => f.evidenceState === "UNRESOLVED")).toBe(true);
    expect(lifecycle.every(f => !!f.unresolvedReason)).toBe(true);
  });
});
