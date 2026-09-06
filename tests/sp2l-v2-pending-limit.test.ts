import { describe, expect, it } from 'vitest';
import {
  createPendingLimitCandidate,
  isExactRetest,
} from '../src/domain/research/sp2l-v2/PendingLimitCandidate.js';

describe('SP2L V2 G2 pending-limit candidate', () => {
  it('uses a bullish higher-low price as a candidate buy limit', () => {
    const result = createPendingLimitCandidate('BULLISH', {
      index: 12,
      high: 2050,
      low: 2042,
    });

    expect(result.status).toBe('CANDIDATE');
    expect(result.entryPrice).toBe(2042);
    expect(result.sourceCandleIndex).toBe(12);
  });

  it('uses a bearish lower-high price as a candidate sell limit', () => {
    const result = createPendingLimitCandidate('BEARISH', {
      index: 21,
      high: 2064,
      low: 2056,
    });

    expect(result.status).toBe('CANDIDATE');
    expect(result.entryPrice).toBe(2064);
    expect(result.sourceCandleIndex).toBe(21);
  });

  it('requires an exact retest and does not invent tolerance', () => {
    const result = createPendingLimitCandidate('BULLISH', {
      index: 4,
      high: 100,
      low: 95,
    });

    expect(isExactRetest(result, 95)).toBe(true);
    expect(isExactRetest(result, 95.01)).toBe(false);
  });

  it('rejects non-finite candle geometry', () => {
    expect(() => createPendingLimitCandidate('BULLISH', {
      index: 1,
      high: Number.NaN,
      low: 95,
    })).toThrow('PENDING_LIMIT_REQUIRES_FINITE_CANDLE');
  });

  it('rejects non-finite retest prices', () => {
    const result = createPendingLimitCandidate('BEARISH', {
      index: 2,
      high: 100,
      low: 96,
    });

    expect(() => isExactRetest(result, Number.NaN)).toThrow(
      'PENDING_LIMIT_RETEST_REQUIRES_FINITE_PRICE',
    );
  });
});
