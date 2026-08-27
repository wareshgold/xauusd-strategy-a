import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectSwingPoints } from '../src/domain/structure/MarketStructure.js';

const c = (timestamp: string, high: number, low: number): Candle => ({ timestamp, open: low, high, low, close: high });

describe('market structure', () => {
  it('classifies higher highs and higher lows without lookahead beyond the pivot window', () => {
    const candles = [
      c('2026-01-01T00:00:00Z', 10, 5),
      c('2026-01-01T00:01:00Z', 12, 7),
      c('2026-01-01T00:02:00Z', 11, 6),
      c('2026-01-01T00:03:00Z', 14, 9),
      c('2026-01-01T00:04:00Z', 13, 8),
      c('2026-01-01T00:05:00Z', 16, 11),
      c('2026-01-01T00:06:00Z', 15, 10),
    ];
    const swings = detectSwingPoints(candles, { pivotLeft: 1, pivotRight: 1 });
    expect(swings.map((x) => x.type)).toEqual(['HH', 'HL', 'HH', 'HL']);
  });

  it('rejects invalid pivot configuration', () => {
    expect(() => detectSwingPoints([], { pivotLeft: 0, pivotRight: 1 })).toThrow();
  });
});
