import { describe, expect, it } from 'vitest';
import { resolvePreviousCandleReference } from '../src/domain/research/sp2l-v2/StructuralReferenceCandidate.js';

describe('SP2L V2 G1 structural reference candidate', () => {
  it('uses the previous candle low for a bullish correction candidate', () => {
    const result = resolvePreviousCandleReference('BULLISH', {
      index: 11,
      high: 101.5,
      low: 99.25,
    });

    expect(result).toEqual({
      status: 'CANDIDATE',
      referenceCandleIndex: 11,
      price: 99.25,
      rationale: 'G1_CANDIDATE_PREVIOUS_CANDLE_LOW',
    });
  });

  it('uses the previous candle high for a bearish correction candidate', () => {
    const result = resolvePreviousCandleReference('BEARISH', {
      index: 21,
      high: 105.75,
      low: 103.5,
    });

    expect(result).toEqual({
      status: 'CANDIDATE',
      referenceCandleIndex: 21,
      price: 105.75,
      rationale: 'G1_CANDIDATE_PREVIOUS_CANDLE_HIGH',
    });
  });

  it('rejects non-finite candle geometry instead of inventing a reference', () => {
    expect(() =>
      resolvePreviousCandleReference('BULLISH', {
        index: 31,
        high: Number.NaN,
        low: 100,
      }),
    ).toThrow('STRUCTURAL_REFERENCE_REQUIRES_FINITE_CANDLE');
  });
});
