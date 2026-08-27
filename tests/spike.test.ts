import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { collectPGAPObservations } from '../src/domain/strategy-a/PGAPResearch.js';

const c = (i: number, open: number, high: number, low: number, close: number): Candle => ({ timestamp: `2026-01-01T00:${String(i).padStart(2, '0')}:00Z`, timeframe: '1m', open, high, low, close });

describe('Strategy A spike research', () => {
  it('creates a candidate only after breakout and follow-through', () => {
    const candles = [c(0,100,101,99,100),c(1,100,102,99.5,101),c(2,101,103,100.5,102),c(3,102,106,101.5,105),c(4,105,108,104,107)];
    const breakouts = detectBreakout(candles, 2);
    const ft = detectFollowThrough(candles, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
    const result = detectSpikeCandidates(candles, breakouts, ft, { maxCandles: 5, minDirectionalFraction: 0.5, maxOverlapFraction: 0.9 });
    expect(result.candidates.length).toBeGreaterThan(0);
    expect(result.candidates[0]?.hasPGAPEvidence).toBe(false);
  });

  it('keeps P-GAP as research evidence rather than a trading rule', () => {
    const candles = [c(0,100,101,99,100),c(1,100,102,100,101),c(2,101,103,101,102),c(3,102,106,105,105.5)];
    const spike = { startIndex: 0, endIndex: 3, direction: 'BULLISH' as const, startPrice: 99, endPrice: 106, size: 7, structureScore: 1, overlapScore: 1, hasPGAPEvidence: false };
    const observations = collectPGAPObservations(candles, spike);
    expect(observations.some((o) => o.classification === 'CANDIDATE')).toBe(true);
    expect(observations.every((o) => o.note.includes('not yet validated') || o.note.includes('research heuristic'))).toBe(true);
  });
});
