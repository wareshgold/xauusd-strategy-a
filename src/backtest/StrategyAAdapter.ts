import type { Candle } from '../domain/market/Candle.js';
import { replayCandles, type ReplayEvent } from './ReplayEngine.js';
import { runBacktest, type BacktestCandidate } from './BacktestEngine.js';
import type { BacktestResult } from './BacktestTypes.js';

export interface StrategyAReplayState { readonly event: ReplayEvent; readonly candidates: readonly BacktestCandidate[]; }
export type StrategyADecision = (event: ReplayEvent) => readonly BacktestCandidate[];
export interface StrategyABacktestRun { readonly result: BacktestResult; readonly states: readonly StrategyAReplayState[]; }

/** Shared decision boundary: the same deterministic decision function can be used by live and historical runners. */
export function runStrategyABacktest(candles: readonly Candle[], decide: StrategyADecision): StrategyABacktestRun {
  const states: StrategyAReplayState[] = [];
  const candidates: BacktestCandidate[] = [];
  replayCandles(candles, (event) => {
    const current = decide(event).filter((candidate) => candidate.entryIndex === event.index);
    states.push({ event, candidates: current });
    candidates.push(...current);
  });
  return { result: runBacktest(candles, candidates), states };
}
