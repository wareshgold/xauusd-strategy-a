export type F13FixtureState =
  | "PASS_RELATION_ONLY"
  | "REJECT_RELATION"
  | "REJECT_GEOMETRY"
  | "UNRESOLVED_LIFECYCLE"
  | "UNRESOLVED_POLICY"
  | "UNRESOLVED_UPDATE"
  | "UNRESOLVED_RISK_BINDING"
  | "UNRESOLVED_TARGET_BINDING";

export interface F13Fixture {
  id: string;
  entry: number;
  stopLoss: number;
  secondaryEntry: number;
  expected: F13FixtureState;
  evidenceState: "SOURCE_CONFIRMED_RELATION" | "UNRESOLVED";
  canonicalEligible: false;
  productionEligible: false;
  unresolvedReason?: string;
}

export const F13_FIXTURES: readonly F13Fixture[] = [
  {id:"F13-001",entry:4350,stopLoss:4340,secondaryEntry:4345,expected:"PASS_RELATION_ONLY",evidenceState:"SOURCE_CONFIRMED_RELATION",canonicalEligible:false,productionEligible:false},
  {id:"F13-002",entry:4340,stopLoss:4350,secondaryEntry:4345,expected:"PASS_RELATION_ONLY",evidenceState:"SOURCE_CONFIRMED_RELATION",canonicalEligible:false,productionEligible:false},
  {id:"F13-003",entry:4350,stopLoss:4340,secondaryEntry:4346,expected:"REJECT_RELATION",evidenceState:"SOURCE_CONFIRMED_RELATION",canonicalEligible:false,productionEligible:false},
  {id:"F13-004",entry:4340,stopLoss:4350,secondaryEntry:4335,expected:"REJECT_GEOMETRY",evidenceState:"UNRESOLVED",canonicalEligible:false,productionEligible:false},
  ...[
    ["F13-005","UNRESOLVED_LIFECYCLE"],["F13-006","UNRESOLVED_LIFECYCLE"],["F13-007","UNRESOLVED_LIFECYCLE"],
    ["F13-008","UNRESOLVED_LIFECYCLE"],["F13-009","UNRESOLVED_POLICY"],["F13-010","UNRESOLVED_LIFECYCLE"],
    ["F13-011","UNRESOLVED_LIFECYCLE"],["F13-012","UNRESOLVED_UPDATE"],["F13-013","UNRESOLVED_UPDATE"],
    ["F13-014","UNRESOLVED_RISK_BINDING"],["F13-015","UNRESOLVED_TARGET_BINDING"]
  ].map(([id,expected]) => ({
    id, entry:4350, stopLoss:4340, secondaryEntry:4345,
    expected: expected as F13FixtureState, evidenceState:"UNRESOLVED" as const,
    canonicalEligible:false as const, productionEligible:false as const,
    unresolvedReason:"F13 executable lifecycle is not source-resolved"
  }))
];

export function f13RelationIsExact(f: Pick<F13Fixture,"entry"|"stopLoss"|"secondaryEntry">): boolean {
  return Math.abs(f.secondaryEntry - (f.entry + 0.5 * (f.stopLoss - f.entry))) < 1e-9;
}

export function validateF13Fixture(f: F13Fixture): boolean {
  if (f.canonicalEligible || f.productionEligible) return false;
  if (f.expected === "PASS_RELATION_ONLY") return f13RelationIsExact(f);
  if (f.expected === "REJECT_RELATION") return !f13RelationIsExact(f);
  return f.evidenceState === "UNRESOLVED" && !!f.unresolvedReason;
}
