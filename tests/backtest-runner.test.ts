import { describe, expect, it } from "vitest";
import type { Candle, MarketSnapshot, SignalCandidate, StrategyProvenance } from "../src/domain/market.js";
import { DeterministicEngine } from "../src/engine/deterministic-engine.js";
import { runBacktest } from "../src/replay/backtest-runner.js";
import { ExecutionSimulator } from "../src/replay/execution-simulator.js";
import { TradeLedger } from "../src/replay/trade-ledger.js";
import { calculateTradeMetrics } from "../src/research/metrics.js";
import { serializeRunManifest } from "../src/replay/run-manifest.js";

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
  { timestamp: "2026-01-01T00:01:00Z", open: 101, high: 102, low: 100, close: 102, timeframe: "1m" },
  { timestamp: "2026-01-01T00:02:00Z", open: 102, high: 102, low: 102, close: 102, timeframe: "1m" },
];

describe("runBacktest", () => {
  it("does not fill a pending order on the signal candle", () => {
    const detector = {
      id: "test-detector",
      provenance,
      evaluate: (_history: readonly MarketSnapshot[]) => ({ status: "SIGNAL" as const, reason: "TEST", candidate }),
    };
    const engine = new DeterministicEngine({ symbol: "XAUUSD", timeframe: "1m", strategy: detector });
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    const result = runBacktest(engine, simulator, ledger, candles.slice(0, 1));

    expect(result.executionEvents.map((event) => event.type)).toEqual(["PENDING"]);
    expect(result.metrics.closedTrades).toBe(0);
  });

  it("does not allow a fill candle to also establish an exit", () => {
    const detector = {
      id: "test-detector",
      provenance,
      evaluate: (_history: readonly MarketSnapshot[]) => ({
        status: "SIGNAL" as const,
        reason: "TEST",
        candidate: {
          ...candidate,
          timestamp: _history[_history.length - 1]!.candle.timestamp,
        },
      }),
    };
    const engine = new DeterministicEngine({ symbol: "XAUUSD", timeframe: "1m", strategy: detector });
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    const result = runBacktest(engine, simulator, ledger, candles.slice(0, 2));

    expect(result.executionEvents.map((event) => event.type)).toEqual([
      "PENDING", "PENDING", "FILLED",
    ]);
    expect(result.metrics.closedTrades).toBe(0);
    expect(result.metrics.totalR).toBe(0);
  });

  it("connects next-candle fill to a later exit and metrics deterministically", () => {
    let call = 0;
    const detector = {
      id: "test-detector",
      provenance,
      evaluate: () => {
        if (call >= 2) return { status: "NO_SIGNAL" as const, reason: "TEST_DONE" };
        const timestamp = candles[call++]!.timestamp;
        return {
          status: "SIGNAL" as const,
          reason: "TEST",
          candidate: { ...candidate, timestamp },
        };
      },
    };
    const engine = new DeterministicEngine({ symbol: "XAUUSD", timeframe: "1m", strategy: detector });
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    const result = runBacktest(engine, simulator, ledger, candles);

    expect(result.executionEvents.map((event) => event.type)).toEqual([
      "PENDING", "PENDING", "FILLED", "TARGET",
    ]);
    expect(result.metrics.closedTrades).toBe(1);
    expect(result.metrics.totalR).toBe(2);
  });

  it("requires explicit fill semantics instead of silently assuming them", () => {
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "UNRESOLVED", intrabarRule: "OHLC_AMBIGUOUS" });
    expect(() => simulator.submit(candidate, "BT-1")).toThrow("FILL_RULE_UNRESOLVED");
  });

  it("rejects non-finite ledger risk values", () => {
    const ledger = new TradeLedger();
    expect(() => ledger.open({ ...candidate, riskPrice: Number.NaN }, "BT-NAN"))
      .toThrow("NON_FINITE_RISK_PRICE");
    expect(() => ledger.open({ ...candidate, expectedR: Number.POSITIVE_INFINITY }, "BT-INF"))
      .toThrow("NON_FINITE_EXPECTED_R");
  });

  it("does not count cancelled trades as closed realized-R trades", () => {
    const ledger = new TradeLedger();
    ledger.open(candidate, "BT-CANCEL");
    ledger.close("BT-CANCEL", { timestamp: "2026-01-01T00:01:00Z", reason: "CANCELLED" });

    const metrics = calculateTradeMetrics(ledger.all());
    expect(metrics.closedTrades).toBe(0);
    expect(metrics.totalR).toBe(0);
    expect(metrics.profitFactor).toBe(0);
  });

  it("serializes a run manifest deterministically", () => {
    const manifest = {
      runId: "RUN-1",
      datasetId: "XAUUSD-TEST",
      datasetVersion: "1",
      datasetFingerprint: "sha256:test",
      strategyId: "TEST",
      strategyVersion: "1",
      executionPolicy: "TOUCH_ENTRY/OHLC_AMBIGUOUS",
      symbol: "XAUUSD",
      timeframe: "1m",
      startedAt: "2026-01-01T00:00:00Z",
      completedAt: "2026-01-01T00:03:00Z",
      candleCount: 3,
      signalCount: 2,
      blockedCount: 0,
      noSignalCount: 1,
      executionEventCount: 4,
      ambiguousEventCount: 0,
    } as const;

    expect(serializeRunManifest(manifest)).toBe(JSON.stringify(manifest, null, 2) + "\n");
  });
});
