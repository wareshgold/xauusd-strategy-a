import { describe, expect, it } from 'vitest';
import { summarizeHypothesisOutcomes, type ResearchTradeOutcome } from '../../src/domain/research/sp2l-v2/G392HypothesisMetrics.js';

describe('G392 hypothesis metrics', () => {
  it('computes deterministic DEV summary without implying canonicality', () => {
    const rows: ResearchTradeOutcome[] = [
      { split: 'DEV', direction: 'LONG', rMultiple: 1, holdingBars: 3 },
      { split: 'DEV', direction: 'SHORT', rMultiple: -1, holdingBars: 2 },
      { split: 'DEV', direction: 'LONG', rMultiple: 2, holdingBars: 4 },
      { split: 'VAL', direction: 'LONG', rMultiple: -1, holdingBars: 1 }
    ];
    const m = summarizeHypothesisOutcomes(rows, 'DEV');
    expect(m.trades).toBe(3);
    expect(m.wins).toBe(2);
    expect(m.losses).toBe(1);
    expect(m.winRate).toBeCloseTo(2 / 3);
    expect(m.averageR).toBeCloseTo(2 / 3);
    expect(m.medianR).toBe(1);
    expect(m.expectancyR).toBeCloseTo(2 / 3);
    expect(m.profitFactor).toBe(3);
    expect(m.maxConsecutiveLosses).toBe(1);
    expect(m.averageHoldingBars).toBe(3);
  });
});
