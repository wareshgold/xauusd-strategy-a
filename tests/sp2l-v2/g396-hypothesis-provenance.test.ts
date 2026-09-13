import { describe, expect, it } from 'vitest';
import { G395_HYPOTHESES, assertResearchOnly, getHypothesisProvenance } from '../../src/domain/research/sp2l-v2/G396HypothesisProvenance.js';

describe('G396 hypothesis provenance guard', () => {
  it('keeps every G395 hypothesis explicitly unresolved and noncanonical', () => {
    expect(G395_HYPOTHESES).toHaveLength(14);
    expect(G395_HYPOTHESES.every((hypothesis) => hypothesis.status === 'UNRESOLVED')).toBe(true);
    expect(G395_HYPOTHESES.every((hypothesis) => hypothesis.canonicalEligible === false)).toBe(true);
  });

  it('resolves hypotheses by id without inferring geometry', () => {
    expect(getHypothesisProvenance('PG-H01')?.component).toBe('P-GAP');
    expect(getHypothesisProvenance('PG-H01')?.sourceRuleIds).toEqual([]);
    expect(getHypothesisProvenance('UNKNOWN')).toBeUndefined();
  });

  it('guards research-only hypotheses from canonical promotion', () => {
    for (const hypothesis of G395_HYPOTHESES) expect(() => assertResearchOnly(hypothesis)).not.toThrow();
  });
});
