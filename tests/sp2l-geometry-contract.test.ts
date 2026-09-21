import { describe, it } from 'vitest';
import {
  assertCanonicalGeometryFrozen,
  createResearchCandidate,
} from '../research/harness/sp2l_geometry_contract_v1.js';

function expectThrow(fn: () => void): void {
  let threw = false;
  try {
    fn();
  } catch {
    threw = true;
  }
  if (!threw) throw new Error('Expected function to throw');
}

describe('SP2L geometry contract', () => {
  it('blocks unresolved research candidates', () => {
    const candidate = createResearchCandidate();
    expectThrow(() => assertCanonicalGeometryFrozen(candidate));
  });

  it('accepts only fully source-confirmed geometry', () => {
    const resolved = createResearchCandidate();
    for (const key of Object.keys(resolved) as Array<keyof typeof resolved>) {
      resolved[key] = { provenance: 'SOURCE_CONFIRMED' };
    }
    assertCanonicalGeometryFrozen(resolved);
  });
});
