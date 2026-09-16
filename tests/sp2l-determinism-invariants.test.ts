import { describe, expect, it } from 'vitest';
import { createResearchCandidate, Sp2lGeometryContract } from '../research/harness/sp2l_geometry_contract_v1';
import { runCanonicalFixture } from '../research/harness/sp2l_fixture_runner_v1';

describe('SP2L deterministic replay invariants', () => {
  it('returns identical blocked results for identical unresolved inputs', () => {
    const geometry = createResearchCandidate();
    const expectation = { id: 'DET-FIXTURE-001', expected: 'BLOCKED_UNRESOLVED_GEOMETRY' };

    const first = runCanonicalFixture('DET-001', geometry, expectation);
    const second = runCanonicalFixture('DET-001', geometry, expectation);

    expect(second).toEqual(first);
  });

  it('returns identical ready results for identical source-confirmed inputs', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const expectation = { id: 'DET-FIXTURE-002', expected: 'READY_FOR_EXECUTION' };
    const first = runCanonicalFixture('DET-002', geometry, expectation);
    const second = runCanonicalFixture('DET-002', geometry, expectation);

    expect(second).toEqual(first);
    expect(first.status).toBe('READY_FOR_EXECUTION');
    expect(first.metrics.tradeCount).toBe(0);
  });
});
