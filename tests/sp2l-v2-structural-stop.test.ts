import { describe, expect, it } from 'vitest';
import {
  resolveStructuralStopCandidate,
} from '../src/domain/research/sp2l-v2/StructuralStopCandidate.js';

describe('SP2L V2 G3 structural stop candidate', () => {
  it('uses the spike-origin low for a bullish stop candidate', () => {
    const result = resolveStructuralStopCandidate('BULLISH', {
      index: 10,
      high: 101.2,
      low: 99.8,
    });

    expect(result.status).toBe('CANDIDATE');
    expect(result.originCandleIndex).toBe(10);
    expect(result.stopPrice).toBe(99.8);
    expect(result.bufferStatus).toBe('TBD');
  });

  it('uses the spike-origin high for a bearish stop candidate', () => {
    const result = resolveStructuralStopCandidate('BEARISH', {
      index: 21,
      high: 203.4,
      low: 201.9,
    });

    expect(result.status).toBe('CANDIDATE');
    expect(result.originCandleIndex).toBe(21);
    expect(result.stopPrice).toBe(203.4);
    expect(result.bufferStatus).toBe('TBD');
  });

  it('does not invent a stop buffer', () => {
    const result = resolveStructuralStopCandidate('BULLISH', {
      index: 5,
      high: 105,
      low: 100,
    });

    expect(result.bufferStatus).toBe('TBD');
    expect(result.stopPrice).toBe(100);
  });

  it('rejects non-finite spike-origin geometry', () => {
    expect(() =>
      resolveStructuralStopCandidate('BEARISH', {
        index: 3,
        high: Number.NaN,
        low: 99,
      }),
    ).toThrow('STRUCTURAL_STOP_REQUIRES_FINITE_CANDLE');
  });
});
