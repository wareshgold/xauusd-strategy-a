import { describe, expect, it } from 'vitest';
import {
  G405_HYPOTHESES,
  G405_MINIMAL_PAIRS,
  G405_STATUS,
  g405AllHypothesesRemainNonCanonical,
  g405DoesNotInventExecutableTargetGeometry,
} from '../../src/domain/research/sp2l-v2/G405TargetMappingSourceResolution.js';

describe('G405 target mapping source resolution', () => {
  it('keeps every target hypothesis explicitly non-canonical', () => {
    expect(g405AllHypothesesRemainNonCanonical()).toBe(true);
    expect(G405_HYPOTHESES.every((item) => item.canonical === false)).toBe(true);
  });

  it('remains unresolved and exposes no executable target geometry', () => {
    expect(G405_STATUS.status).toBe('UNRESOLVED');
    expect(g405DoesNotInventExecutableTargetGeometry()).toBe(true);
    expect(G405_STATUS.canonicalReference).toBeNull();
    expect(G405_STATUS.canonicalTargetLevel).toBeNull();
    expect(G405_STATUS.canonicalTargetCount).toBeNull();
    expect(G405_STATUS.canonicalPriceField).toBeNull();
    expect(G405_STATUS.canonicalLegRelation).toBeNull();
    expect(G405_STATUS.canonicalExecutableTarget).toBeNull();
  });

  it('covers the source-discrimination minimal pairs without selecting a winner', () => {
    expect(G405_MINIMAL_PAIRS).toEqual([
      'TARGET-MP-01:second-leg-endpoint-vs-abcd-projection',
      'TARGET-MP-02:single-vs-two-target-mapping',
      'TARGET-MP-03:geometric-endpoint-vs-risk-multiple',
      'TARGET-MP-04:high-low-vs-body-price-field',
      'TARGET-MP-05:ab-equals-cd-vs-approximate-leg-equality',
      'TARGET-MP-06:geometric-target-vs-executable-take-profit',
      'TARGET-MP-07:bullish-vs-bearish-mirror',
    ]);
  });

  it('does not treat common risk-multiple targets as canonical Strategy A behavior', () => {
    const riskMultiple = G405_HYPOTHESES.find((item) => item.id === 'TARGET-H6');
    expect(riskMultiple?.canonical).toBe(false);
  });
});
