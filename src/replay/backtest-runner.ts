import type { Candle } from "../domain/market.js";
import type { DeterministicEngine } from "../engine/deterministic-engine.js";
import { calculateTradeMetrics, type TradeMetrics } from "../research/metrics.js";
import { ExecutionSimulator, type ExecutionEvent } from "./execution-simulator.js";
import { TradeLedger } from "./trade-ledger.js";

export interface BacktestRunResult {
  readonly candles: number;
  readonly signals: number;
  readonly blocked: number;
  readonly noSignals: number;
  readonly executionEvents: readonly ExecutionEvent[];
  readonly metrics: TradeMetrics;
  readonly trades: ReturnType<TradeLedger["all"]>;
}

export interface BacktestRunnerOptions {
  readonly tradeIdPrefix?: string;
}

/**
 * Generic end-to-end research runner.
 *
 * It connects deterministic decisions to the execution simulator and trade
 * ledger, then computes descriptive metrics. It does not resolve ambiguous
 * OHLC ordering or add any Strategy A geometry.
 */
export function runBacktest(
  engine: DeterministicEngine,
  simulator: ExecutionSimulator,
  ledger: TradeLedger,
  candles: Iterable<Candle>,
  options: BacktestRunnerOptions = {},
): BacktestRunResult {
  const executionEvents: ExecutionEvent[] = [];
  let candlesCount = 0;
  let signals = 0;
  let blocked = 0;
  let noSignals = 0;
  let signalSequence = 0;
  const prefix = options.tradeIdPrefix ?? "BT";

  for (const candle of candles) {
    const decision = engine.push(candle);
    candlesCount += 1;

    if (decision.status === "SIGNAL") {
      signals += 1;
      const id = `${prefix}-${++signalSequence}`;
      executionEvents.push(simulator.submit(decision.candidate!, id));
    } else if (decision.status === "BLOCKED") {
      blocked += 1;
    } else {
      noSignals += 1;
    }

    executionEvents.push(...simulator.onCandle(candle));
  }

  const trades = ledger.all();
  return {
    candles: candlesCount,
    signals,
    blocked,
    noSignals,
    executionEvents,
    metrics: calculateTradeMetrics(trades),
    trades,
  };
}
