import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { runBacktest } from '../src/backtest/BacktestEngine.js';

const c = (i: number, open: number, high: number, low: number, close: number): Candle => ({
  timestamp: `2026-01-01T00:${String(i).padStart(2, '0')}:00Z`, open, high, low, close,
});

describe('pre-freeze metric accounting audit', () => {
  it('separates closed, ambiguous, and open outcomes', () => {
    const candles = [
      c(0, 100, 101, 99, 100),
      c(1, 100, 105, 95, 100),
      c(2, 100, 102, 99, 101),
    ];
    const result = runBacktest(candles, [
      { entryIndex: 0, entryTime: candles[0]!.timestamp, direction: 'BUY', entry: 100, stopLoss: 97, tp1: 103 },
      { entryIndex: 1, entryTime: candles[1]!.timestamp, direction: 'BUY', entry: 100, stopLoss: 90, tp1: 110 },
      { entryIndex: 2, entryTime: candles[2]!.timestamp, direction: 'BUY', entry: 101, stopLoss: 99, tp1: 110 },
    ]);

    expect(result.trades).toHaveLength(3);
    expect(result.trades.map(t => t.result)).toEqual(['AMBIGUOUS', 'OPEN', 'OPEN']);
    expect(result.metrics.trades).toBe(0);
    expect(result.metrics.wins).toBe(0);
    expect(result.metrics.losses).toBe(0);
  });

  it('rejects zero-risk candidates instead of creating infinite R', () => {
    const candles = [c(0, 100, 101, 99, 100), c(1, 100, 104, 99, 103)];
    expect(() => runBacktest(candles, [
      { entryIndex: 0, entryTime: candles[0]!.timestamp, direction: 'BUY', entry: 100, stopLoss: 100, tp1: 103 },
    ])).toThrow('Backtest candidate risk must be positive');
  });

  it('keeps extreme R as arithmetic, making tiny-risk cases auditable rather than silently clipped', () => {
    const candles = [c(0, 100, 100.01, 99.99, 100), c(1, 100, 101, 100, 101)];
    const result = runBacktest(candles, [
      { entryIndex: 0, entryTime: candles[0]!.timestamp, direction: 'BUY', entry: 100, stopLoss: 99.99, tp1: 101 },
    ]);
    expect(result.trades[0]!.result).toBe('TP1');
    expect(result.trades[0]!.riskDistance).toBeCloseTo(0.01);
    expect(result.trades[0]!.rMultiple).toBeCloseTo(100);
    expect(result.metrics.averageR).toBeCloseTo(100);
  });
});
