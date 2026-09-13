import { describe, expect, it } from 'vitest';
import { runDataset } from '../../src/domain/research/sp2l-v2/G388DatasetRunner.js';
import type { DevConfig, RawCandle } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';

const config: DevConfig = {
  devStart: '2026-01-01 00:00:00', devEnd: '2026-03-31 23:59:59',
  valStart: '2026-04-01 00:00:00', valEnd: '2026-06-30 23:59:59',
  holdoutStart: '2026-07-01 00:00:00', holdoutEnd: '2026-09-30 23:59:59',
  costs: { spreadPrice: 0, slippagePrice: 0, commissionPrice: 0 }
};

const candle = (timestamp: string): RawCandle => ({
  symbol: 'XAU/USD', timestamp, timezone: 'UTC', timeframe: '5min',
  open: 1, high: 2, low: 0.5, close: 1.5, provider: 'twelvedata', datasetVersion: 'fixture-v1'
});

describe('G388 dataset runner', () => {
  it('splits chronologically and generates no canonical trades', () => {
    const result = runDataset([
      candle('2026-01-01 00:00:00'), candle('2026-04-01 00:00:00'), candle('2026-08-01 00:00:00')
    ], config);
    expect(result.counts).toEqual({ DEV: 1, VAL: 1, HOLDOUT: 1 });
    expect(result.ordered).toBe(true);
    expect(result.duplicateTimestamps).toBe(0);
    expect(result.leakageFree).toBe(true);
    expect(result.canonicalTradesGenerated).toBe(0);
  });

  it('detects duplicates and non-monotonic timestamps', () => {
    const result = runDataset([
      candle('2026-01-01 00:01:00'), candle('2026-01-01 00:01:00'), candle('2026-01-01 00:00:00')
    ], config);
    expect(result.duplicateTimestamps).toBe(1);
    expect(result.ordered).toBe(false);
    expect(result.leakageFree).toBe(false);
  });

  it('is deterministic for identical input', () => {
    const data = [candle('2026-01-01 00:00:00'), candle('2026-05-01 00:00:00')];
    expect(runDataset(data, config)).toEqual(runDataset(data, config));
  });
});
