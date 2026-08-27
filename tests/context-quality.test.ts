import { describe, expect, it } from 'vitest';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

describe('Strategy A context and quality', () => {
  const config = { emaPeriod: 3, roundStep: 50, roundDistance: 5, tradingSessions: [{ name:'LONDON', startMinutes:480, endMinutes:720 }], avoidWindows: [{ startMinutes:720, endMinutes:735 }] };

  it('calculates EMA context without lookahead', () => {
    const ctx = buildEMAContext([100, 102, 104], config);
    // Recursive EMA seeded with the first observed value: 100 -> 101 -> 102.5.
    expect(ctx?.ema).toBe(102.5);
    expect(ctx?.side).toBe('ABOVE');
  });

  it('detects configurable round-number location', () => {
    const ctx = buildLocationContext(252, config);
    expect(ctx.nearRoundLevel).toBe(true);
    expect(ctx.nearestRoundLevel).toBe(250);
  });

  it('marks avoid windows as blocked', () => {
    const ctx = buildSessionContext('2026-01-01T12:05:00Z', config);
    expect(ctx.avoidWindow).toBe(true);
    expect(ctx.sessionRisk).toBe('BLOCKED');
  });

  it('produces an explainable score', () => {
    const spike = { startIndex:0,endIndex:3,direction:'BULLISH' as const,startPrice:100,endPrice:110,size:10,structureScore:.9,overlapScore:.9,hasPGAPEvidence:true };
    const context = { ema: buildEMAContext([100,102,104], config)!, location: buildLocationContext(252, config), session: buildSessionContext('2026-01-01T09:00:00Z', config) };
    const score = scoreSetup(spike, context);
    expect(score.grade).toBe('A');
    expect(score.factors.length).toBe(6);
    expect(score.tradeAllowed).toBe(true);
  });
});
