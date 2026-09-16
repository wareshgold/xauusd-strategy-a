import {
  Sp2lGeometryContract,
  assertCanonicalGeometryFrozen,
} from './sp2l_geometry_contract_v1';

export type FixtureExpectation = {
  id: string;
  expected: string;
};

export type FixtureRun = {
  fixtureId: string;
  status: 'PASS' | 'FAIL' | 'BLOCKED_UNRESOLVED_GEOMETRY';
  reason?: string;
};

/** Research-only runner shell. It intentionally does not execute BUY/SELL logic. */
export function runCanonicalFixture(
  fixtureId: string,
  geometry: Sp2lGeometryContract,
  expectation: FixtureExpectation,
): FixtureRun {
  try {
    assertCanonicalGeometryFrozen(geometry);
  } catch (error) {
    return {
      fixtureId,
      status: 'BLOCKED_UNRESOLVED_GEOMETRY',
      reason: error instanceof Error ? error.message : String(error),
    };
  }

  // Execution semantics remain a separate unresolved research boundary.
  return {
    fixtureId,
    status: 'FAIL',
    reason: `Fixture ${expectation.id} requires explicit execution implementation before canonical validation.`,
  };
}
