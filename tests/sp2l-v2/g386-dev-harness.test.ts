import { describe, expect, it } from 'vitest';
import {
  adjustedRMultiple,
  adjustedRiskDistance,
  assignSplit,
  buildDatasetManifest,
  canonicalExecutionAllowed,
  type DevConfig,
  type RawCandle
} from '../../src/domain/research/sp2l-v2/G386DevHarness';

const config: DevConfig = {
  devStart: '2026-01-01 00:00:00',
  devEnd: '2026-03-31 23:59:59',
  valStart: '2026-04-01 00:00:00',
  valEnd: '2026-06-30 23:59:59',
  holdoutStart: '2026-07-01 00:00:00',
  holdoutEnd: '2026-09-30 23:59:59',
  costs: { spreadPrice: 0.10, slippagePrice: 0.05, commissionPrice: 0.00 }
};

describe('G386 DEV harness', () => {
  it('assigns temporal splits without overlap', () => {
    expect(assignSplit('2026-02-01 00:00:00', config)).toBe('DEV');
    expect(assignSplit('2026-05-01 00:00:00', config)).toBe('VAL');
    expect(assignSplit('2026-08-01 00:00:00', config)).toBe('HOLDOUT');
    expect(assignSplit('2025-12-31 23:59:59', config)).toBeNull();
  });

  it('applies costs deterministically', () => {
    expect(adjustedRiskDistance(2, config.costs)).toBeCloseTo(2.15);
    expect(adjustedRMultiple(4, 2, config.costs)).toBeCloseTo(1.925);
  });

  it('builds a reproducible dataset manifest', () => {
    const candles: RawCandle[] = [
      { symbol: 'XAU/USD', timestamp: '2026-01-01 00:00:00', timezone: 'UTC', timeframe: '1min', open: 1, high: 2, low: 0.5, close: 1.5, provider: 'twelvedata', datasetVersion: 'fixture-v1' },
      { symbol: 'XAU/USD', timestamp: '2026-01-01 00:01:00', timezone: 'UTC', timeframe: '1min', open: 1.5, high: 2.2, low: 1.2, close: 2, provider: 'twelvedata', datasetVersion: 'fixture-v1' }
    ];
    expect(buildDatasetManifest(candles)).toEqual({
      symbol: 'XAU/USD', provider: 'twelvedata', timezone: 'UTC', timeframe: '1min',
      datasetVersion: 'fixture-v1', firstTimestamp: '2026-01-01 00:00:00',
      lastTimestamp: '2026-01-01 00:01:00', candleCount: 2
    });
  });

  it('cannot authorize canonical execution', () => {
    expect(canonicalExecutionAllowed()).toBe(false);
  });
});
