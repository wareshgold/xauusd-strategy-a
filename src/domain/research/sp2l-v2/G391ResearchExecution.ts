import type { DevSplit, RawCandle } from './G386DevHarness.js';
import { runDataset, type DatasetRunResult } from './G388DatasetRunner.js';
import type { ResearchStrategyAdapter } from './G390StrategyAdapter.js';

export interface ResearchExecutionResult extends DatasetRunResult {
  evaluatedCandles: number;
  candidateCount: number;
  canonicalCandidates: number;
}

export function executeResearch(
  candles: readonly RawCandle[],
  config: Parameters<typeof runDataset>[1],
  adapter: ResearchStrategyAdapter
): ResearchExecutionResult {
  const dataset = runDataset([...candles], config);
  let candidateCount = 0;
  let canonicalCandidates = 0;
  for (let i = 0; i < candles.length; i += 1) {
    const split: DevSplit | null =
      candles[i] ? (candles[i]!.timestamp >= config.devStart && candles[i]!.timestamp <= config.devEnd ? 'DEV' :
      candles[i]!.timestamp >= config.valStart && candles[i]!.timestamp <= config.valEnd ? 'VAL' :
      candles[i]!.timestamp >= config.holdoutStart && candles[i]!.timestamp <= config.holdoutEnd ? 'HOLDOUT' : null) : null;
    if (!split) continue;
    const candidate = adapter.evaluate(candles, i, split);
    if (candidate) {
      candidateCount += 1;
      if (candidate.canonical) canonicalCandidates += 1;
    }
  }
  return { ...dataset, evaluatedCandles: candles.length, candidateCount, canonicalCandidates };
}
