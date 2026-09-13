import { describe, expect, it } from 'vitest';
import {
  G379_HYPOTHESES,
  g379AllNonCanonical,
  g379GateDecision,
  g379HasUnresolvedGeometry,
  g379HypothesisRegistryIsComplete,
} from '../../src/domain/research/sp2l-v2/G379HypothesisExecution.js';

describe('G379 non-canonical hypothesis execution gate', () => {
  it('contains exactly the registered 23 unresolved/candidate hypotheses', () => {
    expect(G379_HYPOTHESES).toHaveLength(23);
    expect(g379HypothesisRegistryIsComplete()).toBe(true);
  });

  it('keeps every hypothesis explicitly non-canonical', () => {
    expect(g379AllNonCanonical()).toBe(true);
    expect(G379_HYPOTHESES.every((h) => h.canonical === false)).toBe(true);
  });

  it('records at least one unresolved executable geometry dimension', () => {
    expect(g379HasUnresolvedGeometry()).toBe(true);
  });

  it('blocks frozen geometry rather than promoting hypotheses', () => {
    expect(g379GateDecision()).toBe('FROZEN-GEOMETRY-BLOCKED');
  });
});
