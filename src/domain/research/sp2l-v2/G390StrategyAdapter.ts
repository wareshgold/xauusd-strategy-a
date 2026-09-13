import type { RawCandle, DevSplit } from './G386DevHarness.js';

export interface ResearchCandidate {
  timestamp: string;
  split: DevSplit;
  direction: 'LONG' | 'SHORT';
  entryPrice: number;
  stopPrice: number;
  targetPrice: number;
  sourceRuleIds: string[];
  canonical: false;
}

export interface ResearchStrategyAdapter {
  readonly strategyVersion: string;
  readonly canonical: false;
  evaluate(candles: readonly RawCandle[], index: number, split: DevSplit): ResearchCandidate | null;
}

export function noCanonicalStrategyAdapter(): ResearchStrategyAdapter {
  return {
    strategyVersion: 'SP2L-UNRESOLVED-GEOMETRY',
    canonical: false,
    evaluate: () => null
  };
}
