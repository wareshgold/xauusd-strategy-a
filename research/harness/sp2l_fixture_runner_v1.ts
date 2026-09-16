import {
  Sp2lGeometryContract,
  assertCanonicalGeometryFrozen,
} from './sp2l_geometry_contract_v1';
import {
  createBlockedValidationReport,
  createReadyValidationReport,
  ValidationReport,
} from './sp2l_validation_report_v1';

export type FixtureExpectation = {
  id: string;
  expected: string;
};

export type FixtureRun = ValidationReport & {
  expectationId: string;
};

/** Research-only runner shell. It intentionally does not execute BUY/SELL logic. */
export function runCanonicalFixture(
  fixtureId: string,
  geometry: Sp2lGeometryContract,
  expectation: FixtureExpectation,
): FixtureRun {
  try {
    assertCanonicalGeometryFrozen(geometry);
  } catch {
    return {
      ...createBlockedValidationReport(fixtureId, geometry),
      expectationId: expectation.id,
    };
  }

  // Geometry may be frozen, but execution/fill semantics remain a separate boundary.
  return {
    ...createReadyValidationReport(fixtureId, geometry),
    expectationId: expectation.id,
  };
}
