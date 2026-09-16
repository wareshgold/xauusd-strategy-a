import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';

type Direction = 'BUY' | 'SELL';

const candle = (i: number, open: number, high: number, low: number, close: number): Candle => ({
  timestamp: `2026-01-02T00:${String(i).padStart(2, '0')}:00Z`,
  open,
  high,
  low,
  close,
});

const mirror = (c: Candle): Candle => ({
  ...c,
  open: -c.open,
  high: -c.low,
  low: -c.high,
  close: -c.close,
});

/**
 * Research-only fixture primitives. These intentionally expose competing
 * interpretations; they do not select canonical Strategy A geometry.
 */

describe('SP2L synthetic geometry fixtures F8-F16', () => {
  it('F8 exposes first relevant swing versus evolving latest swing', () => {
    const candles = [candle(0, 100, 104, 99, 103), candle(1, 103, 108, 102, 107), candle(2, 107, 109, 105, 106), candle(3, 106, 110, 104, 109)];
    const lows = candles.map(x => x.low);
    expect(Math.min(...lows)).toBe(99);
    expect(candles.at(-1)?.low).toBe(104);
    expect(Math.min(...lows)).not.toBe(candles.at(-1)?.low);
  });

  it('F9 keeps Entry and Start-of-Leg-2 as deliberately separated observations', () => {
    const entry = 105;
    const leg2Start = 112;
    expect(entry).not.toBe(leg2Start);
  });

  it('F10 separates structural invalidation from risk-budget stop', () => {
    const structuralInvalidation = 98;
    const riskBudgetStop = 96.5;
    expect(structuralInvalidation).not.toBe(riskBudgetStop);
  });

  it('F11 represents pending-order replacement without inventing a threshold', () => {
    const pending = { state: 'PENDING', limit: 105 } as const;
    const updatedObservation = { state: 'PENDING', limit: 107 } as const;
    expect(pending.state).toBe('PENDING');
    expect(updatedObservation.state).toBe('PENDING');
    expect(updatedObservation.limit).not.toBe(pending.limit);
    // No numeric replacement threshold is encoded here.
  });

  it('F12 preserves the 1/2/3-candle trigger family as observations', () => {
    const triggerLengths = [1, 2, 3];
    expect(triggerLengths).toEqual([1, 2, 3]);
    expect(new Set(triggerLengths).size).toBe(3);
  });

  it('F13 keeps competing 2X interpretations numerically distinct', () => {
    const entry = 100;
    const stop = 95;
    const risk = entry - stop;
    const halfTarget = entry + risk;
    const twoRiskTarget = entry + 2 * risk;
    expect(halfTarget).not.toBe(twoRiskTarget);
  });

  it('F14 keeps competing AB=CD anchor constructions distinct', () => {
    const A1 = 100;
    const B1 = 110;
    const C1 = 104;
    const A2 = 102;
    const B2 = 112;
    const C2 = 104;
    const D1 = C1 + Math.abs(B1 - A1);
    const D2 = C2 + Math.abs(B2 - A2);
    expect(D1).toBe(114);
    expect(D2).toBe(114);
    expect([A1, B1, C1]).not.toEqual([A2, B2, C2]);
  });

  it('F15 mirrors the fixture question into bearish OHLC structure', () => {
    const bullish = candle(0, 100, 106, 98, 104);
    const bearish = mirror(bullish);
    expect(bearish.open).toBe(-100);
    expect(bearish.high).toBe(-98);
    expect(bearish.low).toBe(-106);
    expect(bearish.close).toBe(-104);
  });

  it('F16 preserves source-observed round-level spacing candidates without selecting one', () => {
    const sourceObservedCandidates = [250, 500, 1000];
    expect(sourceObservedCandidates).toEqual([250, 500, 1000]);
    expect(new Set(sourceObservedCandidates).size).toBe(3);
    // The primary artifact shows these spacing annotations, but does not
    // establish the canonical instrument scale, anchor, or selection rule.
  });

  it('does not assign a canonical direction from fixture construction', () => {
    const directions: Direction[] = ['BUY', 'SELL'];
    expect(directions).toEqual(['BUY', 'SELL']);
  });
});
