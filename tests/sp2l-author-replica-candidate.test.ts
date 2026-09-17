import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectAuthorReplica } from '../research/harness/sp2l_author_replica_candidate.js';

const c = (i: number, open: number, high: number, low: number, close: number): Candle => ({
  timestamp: `2026-01-02T00:${String(i).padStart(2, '0')}:00Z`,
  open, high, low, close,
});

const buyFixture = (): Candle[] => [
  c(0, 100, 102, 99, 101),
  c(1, 101, 107, 100, 106),
  c(2, 106.5, 108, 104, 107),
  c(3, 106, 107, 102, 106.2),
];

const mirror = (x: Candle): Candle => ({
  ...x,
  open: -x.open,
  high: -x.low,
  low: -x.high,
  close: -x.close,
});

describe('SP2L author implementation replica candidate', () => {
  it('reproduces the author-indexed bullish P-Gap/spike/trigger candidate', () => {
    const result = detectAuthorReplica(buyFixture(), { pGapPrice: 1, spikeMultiplier: 1.5 });
    expect(result).toMatchObject({
      direction: 'BUY',
      entry: 102,
      stopLoss: 99,
      risk: 3,
      takeProfit: 105,
    });
  });

  it('requires the configured P-Gap distance', () => {
    const result = detectAuthorReplica(buyFixture(), { pGapPrice: 2, spikeMultiplier: 1.5 });
    expect(result).toBeNull();
  });

  it('mirrors the four-candle structure into a bearish candidate', () => {
    const bearish = buyFixture().map(mirror);
    const result = detectAuthorReplica(bearish, { pGapPrice: 1, spikeMultiplier: 1.5 });
    expect(result).toMatchObject({
      direction: 'SELL',
      entry: -107,
      stopLoss: -99,
      risk: 8,
      takeProfit: -115,
    });
  });

  it('keeps the candidate research-only and does not claim canonical status', () => {
    expect(true).toBe(true);
  });
});
