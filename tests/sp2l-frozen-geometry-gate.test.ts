import { createResearchCandidate, Sp2lGeometryContract } from '../research/harness/sp2l_geometry_contract_v1';
import { evaluateFrozenGeometryGate } from '../research/harness/sp2l_frozen_geometry_gate_v1';

describe('SP2L frozen geometry gate', () => {
  it('blocks the current unresolved research candidate', () => {
    const geometry = createResearchCandidate();
    const result = evaluateFrozenGeometryGate(geometry);

    expect(result.status).toBe('BLOCKED');
    expect(result.blockedFields).toEqual([
      'entry', 'invalidation', 'limitRefresh', 'trigger', 'twoX', 'abcd', 'pGap',
    ]);
  });

  it('allows readiness only when every required field is source-confirmed', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const result = evaluateFrozenGeometryGate(geometry);
    expect(result.status).toBe('READY');
    expect(result.blockedFields).toEqual([]);
  });

  it('fails closed when even one field is candidate or unresolved', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }
    geometry.pGap = { provenance: 'CANDIDATE' };

    const result = evaluateFrozenGeometryGate(geometry);
    expect(result.status).toBe('BLOCKED');
    expect(result.blockedFields).toEqual(['pGap']);
  });
});
