import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { DEFAULT_AUTHOR_REPLICA, detectAuthorReplicaCandidates } from '../research/harness/sp2l_author_replica_v1.js';

const c = (i: number, open: number, high: number, low: number, close: number): Candle => ({
  timestamp: `2026-01-02T00:${String(i).padStart(2, '0')}:00Z`,
  open, high, low, close,
});

describe('SP2L author replica candidate', () => {
  it('detects the author-indexed bullish four-candle construction', () => {
    const data = [
      c(0, 100, 101.5, 99.5, 101),
      c(1, 101.5, 106.5, 101.5, 106),
      c(2, 106.5, 107.5, 103, 107),
      c(3, 107, 108, 106.5, 107.2),
      c(4, 104, 104.5, 102.5, 104.2),
    ];
    const [trade] = detectAuthorReplicaCandidates(data);
    expect(trade?.direction).toBe('BUY');
    expect(trade?.entryIndex).toBe(4);
    expect(trade?.entry).toBe(102.5);
    expect(trade?.stopLoss).toBe(99.5);
    expect(trade?.risk).toBe(3);
    expect(trade?.tp1).toBe(105.5);
    expect(trade?.pGapDistance).toBe(1.5);
  });

  it('detects the bearish mirror with the same indexing', () => {
    const data = [
      c(0, 200, 200.5, 198.5, 199),
      c(1, 198.5, 199, 193.5, 194),
      c(2, 193.5, 194, 192.5, 193),
      c(3, 193, 194, 192.8, 193.2),
      c(4, 193.5, 195, 193, 193.3),
    ];
    const [trade] = detectAuthorReplicaCandidates(data);
    expect(trade?.direction).toBe('SELL');
    expect(trade?.entryIndex).toBe(4);
    expect(trade?.entry).toBe(195);
    expect(trade?.stopLoss).toBe(200.5);
    expect(trade?.risk).toBe(5.5);
    expect(trade?.tp1).toBe(189.5);
    expect(trade?.pGapDistance).toBe(4.5);
  });

  it('uses the author defaults as research parameters, not canonical geometry', () => {
    expect(DEFAULT_AUTHOR_REPLICA).toEqual({
      gapPrice: 1.0,
      spikeMultiplier: 1.5,
      maxSlDistance: 10.0,
      tpR: 1.0,
    });
  });
});
