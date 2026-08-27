import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectSwingPoints } from '../src/domain/market/StructureDetector.js';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';

const candle = (i: number, high: number, low: number, close = (high + low) / 2): Candle => ({ timestamp: `2026-01-01T00:${String(i).padStart(2, '0')}:00Z`, open: close, high, low, close });

describe('market structure', () => {
  it('classifies confirmed swing highs and lows', () => {
    const candles = [
      candle(0, 10, 5), candle(1, 12, 7), candle(2, 15, 8), candle(3, 11, 6),
      candle(4, 16, 9), candle(5, 13, 7), candle(6, 14, 8),
    ];
    const points = detectSwingPoints(candles, { leftBars: 1, rightBars: 1 });
    expect(points.map((p) => p.kind)).toEqual(['INITIAL', 'INITIAL', 'HH']);
  });
});

describe('breakout', () => {
  it('requires a close beyond the prior lookback extreme', () => {
    const candles = [candle(0, 10, 5), candle(1, 12, 6), candle(2, 13, 7), candle(3, 14, 8, 13.5)];
    const events = detectBreakout(candles, 2);
    expect(events).toHaveLength(1);
    expect(events[0]?.direction).toBe('BULLISH');
    expect(events[0]?.brokenLevel).toBe(13);
  });
});
