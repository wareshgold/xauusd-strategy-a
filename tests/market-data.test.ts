import { describe, expect, it } from 'vitest';
import { aggregateM5 } from '../src/application/market-data/aggregateM5.js';
import type { Candle } from '../src/domain/market/Candle.js';

function candle(minute: number, open: number, high: number, low: number, close: number): Candle {
  return {
    timestamp: `2026-08-27T20:${String(minute).padStart(2, '0')}:00.000Z`,
    open,
    high,
    low,
    close,
  };
}

describe('aggregateM5', () => {
  it('aggregates exactly five contiguous M1 candles', () => {
    const result = aggregateM5([
      candle(0, 100, 101, 99, 100.5),
      candle(1, 100.5, 102, 100, 101.5),
      candle(2, 101.5, 103, 101, 102.5),
      candle(3, 102.5, 104, 102, 103.5),
      candle(4, 103.5, 105, 103, 104.5),
    ]);

    expect(result).toEqual([
      {
        timestamp: '2026-08-27T20:00:00.000Z',
        open: 100,
        high: 105,
        low: 99,
        close: 104.5,
      },
    ]);
  });

  it('does not fabricate an M5 candle when an M1 candle is missing', () => {
    const result = aggregateM5([
      candle(0, 100, 101, 99, 100.5),
      candle(1, 100.5, 102, 100, 101.5),
      candle(2, 101.5, 103, 101, 102.5),
      candle(4, 103.5, 105, 103, 104.5),
    ]);

    expect(result).toHaveLength(0);
  });
});
