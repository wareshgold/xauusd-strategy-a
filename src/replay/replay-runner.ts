import type { Candle, EngineDecision } from "../domain/market.js";
import { DeterministicEngine } from "../engine/deterministic-engine.js";

export interface ReplayRunResult {
  readonly candles: number;
  readonly signals: number;
  readonly blocked: number;
  readonly noSignals: number;
  readonly decisions: readonly EngineDecision[];
}

/**
 * Replays a validated candle stream through the deterministic engine.
 *
 * This is a decision-replay harness only. It intentionally does not assume
 * that a pending-limit candidate was filled; fill, cancellation, SL and TP
 * semantics remain separate until their source geometry is frozen.
 */
export function replayCandles(
  engine: DeterministicEngine,
  candles: Iterable<Candle>,
): ReplayRunResult {
  const decisions: EngineDecision[] = [];
  let candlesCount = 0;
  let signals = 0;
  let blocked = 0;
  let noSignals = 0;

  for (const candle of candles) {
    const decision = engine.push(candle);
    decisions.push(decision);
    candlesCount += 1;
    if (decision.status === "SIGNAL") signals += 1;
    else if (decision.status === "BLOCKED") blocked += 1;
    else noSignals += 1;
  }

  return { candles: candlesCount, signals, blocked, noSignals, decisions };
}
