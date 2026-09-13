import { describe, expect, it } from 'vitest';
import { simulateFilledCandidate } from '../../src/domain/research/sp2l-v2/G394OutcomeSimulator.js';
import type { RawCandle } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';
import type { ResearchCandidate } from '../../src/domain/research/sp2l-v2/G390StrategyAdapter.js';

const base: Omit<RawCandle, 'timestamp'> = {
  symbol: 'XAU/USD', timezone: 'UTC', timeframe: '5min', provider: 'fixture', datasetVersion: 'G394-fixture',
  open: 100, high: 101, low: 99, close: 100
};
const candle = (timestamp: string, high: number, low: number): RawCandle => ({ ...base, timestamp, high, low });
const candidate: ResearchCandidate = {
  timestamp: '2026-01-01T00:00:00Z', split: 'DEV', direction: 'LONG',
  entryPrice: 100, stopPrice: 99, targetPrice: 102, sourceRuleIds: ['RESEARCH-ONLY'], canonical: false
};

describe('G394 outcome simulator', () => {
  it('returns a deterministic win with MAE/MFE', () => {
    const result = simulateFilledCandidate([
      candle('2026-01-01T00:00:00Z', 101, 99.5),
      candle('2026-01-01T00:05:00Z', 101.5, 99.5),
      candle('2026-01-01T00:10:00Z', 102.5, 100.5)
    ], 0, candidate);
    expect(result.status).toBe('WIN');
    expect(result.outcome?.rMultiple).toBe(2);
    expect(result.outcome?.holdingBars).toBe(2);
    expect(result.outcome?.maeR).toBe(0.5);
    expect(result.outcome?.mfeR).toBe(2.5);
  });

  it('refuses to invent intrabar ordering when stop and target share a bar', () => {
    const result = simulateFilledCandidate([
      candle('2026-01-01T00:00:00Z', 101, 99.5),
      candle('2026-01-01T00:05:00Z', 103, 98)
    ], 0, candidate);
    expect(result.status).toBe('AMBIGUOUS');
    expect(result.outcome).toBeNull();
  });
});
