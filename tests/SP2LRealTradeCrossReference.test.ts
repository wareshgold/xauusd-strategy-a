import { describe, expect, it } from 'vitest';
import { SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES } from './fixtures/SP2LRealTradeCrossReference.fixtures.js';

describe('SP2L real-trade cross-reference', () => {
  it('preserves the four source-visible trades as SELL observations', () => {
    expect(SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES.map((f) => f.tradeId)).toEqual(['T1', 'T2', 'T3', 'T4']);
    expect(SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES.every((f) => f.direction === 'SELL')).toBe(true);
  });

  it('preserves the source-aligned correction/previous-high entry context without fixing exact geometry', () => {
    for (const fixture of SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES) {
      expect(fixture.observedStructuralEntryContext).toBe('CORRECTION_PREVIOUS_HIGH_CONTEXT');
      expect(fixture.exactEntryCandleResolved).toBe(false);
      expect(fixture.exactEntryBoundaryResolved).toBe(false);
    }
  });

  it('does not infer P-Gap or SL formulas from the trade records', () => {
    for (const fixture of SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES) {
      expect(fixture.exactPGAPBoundaryResolved).toBe(false);
      expect(fixture.exactPGAPCandleResolved).toBe(false);
      expect(fixture.exactSLBoundaryResolved).toBe(false);
    }
  });
});
