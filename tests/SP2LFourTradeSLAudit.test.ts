import { describe, expect, it } from 'vitest';
import { SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES } from './fixtures/SP2LFourTradeSLAudit.fixtures.js';

describe('SP2L four-trade source SL/origin audit', () => {
  it('preserves all four source-visible stop observations', () => {
    expect(SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES.map((f) => f.id)).toEqual(['T1', 'T2', 'T3', 'T4']);
  });

  it('preserves structural stop semantics without resolving exact geometry', () => {
    for (const fixture of SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES) {
      expect(fixture.stopSemantic).toBe('BEHIND_SPIKE_ORIGIN_CANDLE');
      expect(fixture.exactStopBoundaryResolved).toBe(false);
      expect(fixture.fixedBufferResolved).toBe(false);
    }
  });

  it('records risk distances descriptively rather than as a canonical fixed distance', () => {
    expect(SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES.map((f) => f.observedRiskDistance)).toEqual([8.65, 11.66, 6.62, 5.39]);
  });

  it('does not promote a fixed-distance stop rule', () => {
    const distances = SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES.map((f) => f.observedRiskDistance);
    expect(new Set(distances).size).toBeGreaterThan(1);
  });
});
