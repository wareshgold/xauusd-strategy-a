import { describe, expect, it } from 'vitest';
import { SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES } from './fixtures/SP2LRealTradeEntryCandleHypotheses.fixtures.js';

describe('SP2L real-trade Entry candle hypotheses', () => {
  it('covers all four observed trades and five candidate interpretations', () => {
    expect(new Set(SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES.map((f) => f.tradeId))).toEqual(new Set(['T1', 'T2', 'T3', 'T4']));
    expect(SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES).toHaveLength(20);
  });

  it('preserves previous/relevant High as semantic context without freezing exact geometry', () => {
    const semanticCandidates = SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES.filter(
      (f) => f.hypothesis === 'RELEVANT_PREVIOUS_HIGH',
    );
    expect(semanticCandidates).toHaveLength(4);
    expect(semanticCandidates.every((f) => f.sourceSupported)).toBe(true);
    expect(semanticCandidates.every((f) => f.executableFormulaResolved === false)).toBe(true);
  });

  it('keeps competing candle/price interpretations unresolved', () => {
    for (const fixture of SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES) {
      expect(fixture.executableFormulaResolved).toBe(false);
    }
  });
});
