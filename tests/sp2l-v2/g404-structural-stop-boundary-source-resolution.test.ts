import { describe, expect, it } from 'vitest';
import {
  G404_HYPOTHESES,
  G404_MINIMAL_PAIRS,
  G404_STATUS,
  g404AllHypothesesRemainNonCanonical,
  g404DoesNotInventExecutableStopGeometry,
} from '../../src/domain/research/sp2l-v2/G404StructuralStopBoundarySourceResolution.js';

describe('G404 structural stop boundary source resolution', () => {
  it('keeps every stop interpretation non-canonical', () => {
    expect(g404AllHypothesesRemainNonCanonical()).toBe(true);
    expect(G404_HYPOTHESES.every((item) => item.canonical === false)).toBe(true);
  });

  it('keeps executable stop geometry unresolved', () => {
    expect(G404_STATUS.status).toBe('UNRESOLVED');
    expect(g404DoesNotInventExecutableStopGeometry()).toBe(true);
  });

  it('enumerates the targeted source-discrimination dimensions', () => {
    expect(G404_MINIMAL_PAIRS).toEqual([
      'STOP-MP-01:spike-origin-vs-setup-boundary',
      'STOP-MP-02:wick-vs-body-boundary',
      'STOP-MP-03:high-low-vs-open-close-price-field',
      'STOP-MP-04:zero-vs-positive-buffer',
      'STOP-MP-05:pre-fill-vs-post-fill-invalidation',
      'STOP-MP-06:structural-boundary-vs-executable-stop',
      'STOP-MP-07:bullish-vs-bearish-mirror',
    ]);
  });

  it('does not promote the existing G3 stop candidate', () => {
    expect(G404_STATUS.canonicalReference).toBeNull();
    expect(G404_STATUS.canonicalBoundary).toBeNull();
    expect(G404_STATUS.canonicalBuffer).toBeNull();
    expect(G404_STATUS.canonicalExecutableStop).toBeNull();
  });
});
