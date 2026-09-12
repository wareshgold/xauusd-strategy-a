import { describe, expect, it } from 'vitest';
import { resolveStructuralStopCandidate } from '../src/domain/research/sp2l-v2/StructuralStopCandidate.js';

describe('G3 structural-stop candidate', () => {
  it('uses the bullish spike-origin low without inventing a buffer', () => {
    const result = resolveStructuralStopCandidate('BULLISH', {
      index: 12,
      high: 3050,
      low: 2990,
    });

    expect(result).toEqual({
      status: 'CANDIDATE',
      originCandleIndex: 12,
      stopPrice: 2990,
      rationale: 'G3_CANDIDATE_BULLISH_SPIKE_ORIGIN_LOW',
      bufferStatus: 'TBD',
    });
  });

  it('uses the bearish spike-origin high without inventing a buffer', () => {
    const result = resolveStructuralStopCandidate('BEARISH', {
      index: 21,
      high: 3060,
      low: 3005,
    });

    expect(result.stopPrice).toBe(3060);
    expect(result.bufferStatus).toBe('TBD');
    expect(result.rationale).toBe('G3_CANDIDATE_BEARISH_SPIKE_ORIGIN_HIGH');
  });

  it('rejects non-finite candle extremes', () => {
    expect(() =>
      resolveStructuralStopCandidate('BULLISH', {
        index: 1,
        high: Number.NaN,
        low: 2990,
      }),
    ).toThrow('STRUCTURAL_STOP_REQUIRES_FINITE_CANDLE');
  });
});
