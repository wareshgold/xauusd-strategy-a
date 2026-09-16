import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.ts';
import { createResearchCandidate } from '../research/harness/sp2l_geometry_contract_v1';
import { runFrozenGeometryBacktest } from '../research/harness/sp2l_canonical_backtest_gate_v1';

const candles: readonly Candle[] = [
  { timestamp: '2026-01-01T00:00:00Z', open: 100, high: 101, low: 99, close: 100 },
  { timestamp: '2026-01-01T00:01:00Z', open: 100, high: 101, low: 99, close: 100 },
];

describe('SP2L canonical backtest boundary', () => {
  it('fails closed before a decision function can run when geometry is unresolved', () => {
    const geometry = createResearchCandidate();
    let decisionCalled = false;

    expect(() => runFrozenGeometryBacktest(candles, geometry, () => {
      decisionCalled = true;
      return [];
    })).toThrowError(/CANONICAL_GEOMETRY_NOT_FROZEN/);

    expect(decisionCalled).toBe(false);
  });

  it('permits the adapter only after every geometry field is source-confirmed', () => {
    const geometry = createResearchCandidate();
    for (const field of Object.keys(geometry) as (keyof typeof geometry)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const run = runFrozenGeometryBacktest(candles, geometry, () => []);

    expect(run.result.trades).toEqual([]);
    expect(run.result.metrics.trades).toBe(0);
  });
});
