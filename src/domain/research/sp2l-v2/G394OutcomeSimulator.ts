import type { RawCandle } from './G386DevHarness.js';
import type { ResearchCandidate } from './G390StrategyAdapter.js';
import type { ResearchTradeOutcome } from './G392HypothesisMetrics.js';

export type OutcomeStatus = 'WIN' | 'LOSS' | 'TIMEOUT' | 'AMBIGUOUS';

export interface SimulatedOutcome {
  status: OutcomeStatus;
  outcome: ResearchTradeOutcome | null;
}

/**
 * Research-only execution simulator. It assumes the candidate is already filled
 * at entryPrice. It does not define Strategy A entry/fill semantics.
 * If one future OHLC bar touches both stop and target, the path is ambiguous and
 * no trade outcome is emitted rather than inventing intrabar ordering.
 */
export function simulateFilledCandidate(
  candles: readonly RawCandle[],
  candidateIndex: number,
  candidate: ResearchCandidate,
  maxHoldingBars = 100
): SimulatedOutcome {
  if (candidateIndex < 0 || candidateIndex >= candles.length) return { status: 'TIMEOUT', outcome: null };
  const risk = Math.abs(candidate.entryPrice - candidate.stopPrice);
  if (risk <= 0) return { status: 'TIMEOUT', outcome: null };

  let bestFavorable = 0;
  let worstAdverse = 0;
  const end = Math.min(candles.length - 1, candidateIndex + maxHoldingBars);

  for (let i = candidateIndex + 1; i <= end; i += 1) {
    const bar = candles[i]!;
    const favorable = candidate.direction === 'LONG'
      ? bar.high - candidate.entryPrice
      : candidate.entryPrice - bar.low;
    const adverse = candidate.direction === 'LONG'
      ? candidate.entryPrice - bar.low
      : bar.high - candidate.entryPrice;
    bestFavorable = Math.max(bestFavorable, favorable);
    worstAdverse = Math.max(worstAdverse, adverse);

    const stopHit = candidate.direction === 'LONG'
      ? bar.low <= candidate.stopPrice
      : bar.high >= candidate.stopPrice;
    const targetHit = candidate.direction === 'LONG'
      ? bar.high >= candidate.targetPrice
      : bar.low <= candidate.targetPrice;

    if (stopHit && targetHit) return { status: 'AMBIGUOUS', outcome: null };
    if (targetHit) {
      return {
        status: 'WIN',
        outcome: {
          split: candidate.split,
          direction: candidate.direction,
          rMultiple: Math.abs(candidate.targetPrice - candidate.entryPrice) / risk,
          holdingBars: i - candidateIndex,
          maeR: worstAdverse / risk,
          mfeR: bestFavorable / risk
        }
      };
    }
    if (stopHit) {
      return {
        status: 'LOSS',
        outcome: {
          split: candidate.split,
          direction: candidate.direction,
          rMultiple: -1,
          holdingBars: i - candidateIndex,
          maeR: worstAdverse / risk,
          mfeR: bestFavorable / risk
        }
      };
    }
  }

  return { status: 'TIMEOUT', outcome: null };
}
