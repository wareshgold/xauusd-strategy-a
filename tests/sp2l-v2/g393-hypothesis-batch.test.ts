import { describe, expect, it } from 'vitest';
import { runHypothesisBatch } from '../../src/domain/research/sp2l-v2/G393HypothesisBatch.js';
import { noCanonicalStrategyAdapter } from '../../src/domain/research/sp2l-v2/G390StrategyAdapter.js';
import type { RawCandle } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';

const candle: RawCandle = {symbol:'XAU/USD',timestamp:'2026-07-01 00:00:00',timezone:'UTC',timeframe:'5min',open:1,high:2,low:.5,close:1.5,provider:'twelvedata',datasetVersion:'snapshot'};

describe('G393 hypothesis batch', () => {
  it('keeps unresolved adapter noncanonical and produces zero candidates', () => {
    const result = runHypothesisBatch([candle], noCanonicalStrategyAdapter(), () => null);
    expect(result.strategyVersion).toBe('SP2L-UNRESOLVED-GEOMETRY');
    expect(result.canonical).toBe(false);
    expect(result.candidates).toBe(0);
    expect(result.metrics.every((m) => m.trades === 0)).toBe(true);
  });
});
