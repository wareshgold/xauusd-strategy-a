import { describe, expect, it } from 'vitest';
import { createResearchCandidate, Sp2lGeometryContract } from '../research/harness/sp2l_geometry_contract_v1';
import { runCanonicalFixture } from '../research/harness/sp2l_fixture_runner_v1';

describe('SP2L canonical fixture runner', () => {
  it('fails closed to BLOCKED when source geometry is unresolved', () => {
    const result = runCanonicalFixture(
      'UNRESOLVED-1',
      createResearchCandidate({ pGap: 'source formula unresolved' }),
      { id: 'EXPECT-BLOCK', expected: 'BLOCKED_UNRESOLVED_GEOMETRY' },
    );

    expect(result.status).toBe('BLOCKED_UNRESOLVED_GEOMETRY');
    expect(result.excludedFromMetrics).toBe(true);
    expect(result.metrics.tradeCount).toBe(0);
  });

  it('returns READY_FOR_EXECUTION only after every geometry field is source-confirmed', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const result = runCanonicalFixture(
      'FROZEN-READY-1',
      geometry,
      { id: 'EXPECT-READY', expected: 'READY_FOR_EXECUTION' },
    );

    expect(result.status).toBe('READY_FOR_EXECUTION');
    expect(result.excludedFromMetrics).toBe(true);
    expect(result.metrics.tradeCount).toBe(0);
  });

  it('fails closed when a single field remains a research candidate', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }
    geometry.pGap = { provenance: 'CANDIDATE' };

    const result = runCanonicalFixture(
      'CANDIDATE-1',
      geometry,
      { id: 'EXPECT-BLOCK-CANDIDATE', expected: 'BLOCKED_UNRESOLVED_GEOMETRY' },
    );

    expect(result.status).toBe('BLOCKED_UNRESOLVED_GEOMETRY');
    expect(result.provenance.pGap).toBe('CANDIDATE');
    expect(result.metrics.tradeCount).toBe(0);
  });
});
