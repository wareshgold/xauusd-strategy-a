import { describe, expect, it } from "vitest";
import type { Candle, SignalCandidate, StrategyProvenance } from "../src/domain/market.js";
import { DeterministicEngine } from "../src/engine/deterministic-engine.js";
import { runBacktest } from "../src/replay/backtest-runner.js";
import { ExecutionSimulator } from "../src/replay/execution-simulator.js";
import { TradeLedger } from "../src/replay/trade-ledger.js";

const provenance: StrategyProvenance = {
  strategyId: "TEST",
  version: "1",
  ruleIds: ["TEST.R1"],
  canonical: true,
};

const candidate: SignalCandidate = {
  symbol: "XAUUSD",
  direction: "LONG",
  timestamp: "2026-01-01T00:00:00Z",
  entryType: "PENDING_LIMIT",
  entryPrice: 100,
  stopPrice: 99,
  targetPrice: 102,
  riskPrice: 1,
  expectedR: 2,
  provenance,
};

const candles: Candle[] = [
  { timestamp: "2026-01-01T00:00:00Z", open: 101, high: 101, low: 100, close: 101, timeframe: "1m" },
  { timestamp: "2026-01-01T00:01:00Z", open: 101, high: 102, low: 101, close: 102, timeframe: "1m" },
];

describe("runBacktest", () => {
  it("connects signal, fill, exit and metrics deterministically", () => {
    const detector = {
      id: "test-detector",
      provenance,
      evaluate: () => ({ status: "SIGNAL", reason: "TEST", candidate }),
    };
    const engine = new DeterministicEngine({ symbol: "XAUUSD", timeframe: "1m", strategy: detector });
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    const result = runBacktest(engine, simulator, ledger, candles);

    expect(result.candles).toBe(2);
    expect(result.signals).toBe(2);
    expect(result.executionEvents.map((event) => event.type)).toEqual([
      "PENDING", "FILLED", "PENDING", "FILLED", "TARGET", "TARGET",
    ]);
    expect(result.metrics.closedTrades).toBe(2);
    expect(result.metrics.totalR).toBe(4);
  });
});
