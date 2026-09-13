import type { DevSplit, RawCandle } from './G386DevHarness.js';
import { summarizeHypothesisOutcomes, type ResearchMetrics, type ResearchTradeOutcome } from './G392HypothesisMetrics.js';
import type { ResearchStrategyAdapter } from './G390StrategyAdapter.js';

export interface HypothesisBatchResult {
  strategyVersion: string;
  canonical: false;
  candidates: number;
  metrics: ResearchMetrics[];
}

export function runHypothesisBatch(
  candles: readonly RawCandle[],
  adapter: ResearchStrategyAdapter,
  outcomeResolver: (candidateIndex: number, candidate: NonNullable<ReturnType<ResearchStrategyAdapter['evaluate']>>) => ResearchTradeOutcome | null,
  splits: readonly DevSplit[] = ['DEV', 'VAL']
): HypothesisBatchResult {
  const outcomes: ResearchTradeOutcome[] = [];
  let candidates = 0;
  for (let i = 0; i < candles.length; i += 1) {
    for (const split of splits) {
      const candidate = adapter.evaluate(candles, i, split);
      if (!candidate) continue;
      candidates += 1;
      const outcome = outcomeResolver(i, candidate);
      if (outcome) outcomes.push(outcome);
    }
  }
  return {
    strategyVersion: adapter.strategyVersion,
    canonical: false,
    candidates,
    metrics: splits.map((split) => summarizeHypothesisOutcomes(outcomes, split))
  };
}
