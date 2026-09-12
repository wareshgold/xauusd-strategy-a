import { describe, expect, it } from 'vitest';
import {
  G344_MINIMAL_PAIRS,
  G344_NON_CANONICAL_DIMENSIONS,
  evaluateAllG344Pairs,
  g344CoveredDimensions,
  g344PairsRemainResearchOnly,
  g344ProjectionSingletonIsNotInvented,
} from '../src/domain/research/sp2l-v2/G344MinimalPairDiscrimination.js';

describe('G344 — minimal-pair synthetic discrimination', () => {
  it('covers every currently variable unresolved geometry dimension', () => {
    expect(g344CoveredDimensions(G344_MINIMAL_PAIRS)).toEqual(
      [...G344_NON_CANONICAL_DIMENSIONS].sort(),
    );
  });

  it('changes exactly one model dimension in every pair, excluding the research-only identity field', () => {
    for (const pair of G344_MINIMAL_PAIRS) {
      const differingKeys = (Object.keys(pair.left) as Array<keyof typeof pair.left>)
        .filter((key) => key !== 'id')
        .filter((key) => pair.left[key] !== pair.right[key]);
      const expectedKey =
        pair.dimension === 'A_SELECTOR' ? 'aSelector' :
        pair.dimension === 'B_SELECTOR' ? 'bSelector' :
        pair.dimension === 'C_SELECTOR' ? 'cSelector' :
        pair.dimension === 'PRICE_FIELD' ? 'priceField' :
        pair.dimension === 'SCALE' ? 'scale' : 'projection';
      expect(differingKeys).toEqual([expectedKey]);
    }
  });

  it('discriminates A, B, C and price-field changes under the research evaluator', () => {
    const results = evaluateAllG344Pairs();
    for (const dimension of ['A_SELECTOR', 'B_SELECTOR', 'C_SELECTOR', 'PRICE_FIELD'] as const) {
      expect(results.find((result) => result.dimension === dimension)?.discriminates).toBe(true);
    }
  });

  it('keeps fill-as-C as a discriminating negative control, not a canonical rule', () => {
    const pair = G344_MINIMAL_PAIRS.find((candidate) => candidate.dimension === 'C_SELECTOR');
    expect(pair).toBeDefined();
    expect(pair?.right.cSelector).toBe('FILL_AS_C');
    expect(pair?.right.canonical).toBe(false);
  });

  it('exposes that scale alone is not numerically discriminated by the current evaluator', () => {
    const result = evaluateAllG344Pairs().find((candidate) => candidate.dimension === 'SCALE');
    expect(result?.discriminates).toBe(false);
  });

  it('does not invent an alternative projection model', () => {
    expect(g344ProjectionSingletonIsNotInvented()).toBe(true);
  });

  it('keeps every pair research-only', () => {
    expect(g344PairsRemainResearchOnly(G344_MINIMAL_PAIRS)).toBe(true);
  });
});
