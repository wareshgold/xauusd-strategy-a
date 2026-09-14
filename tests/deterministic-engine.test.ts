import { describe, expect, it } from "vitest";
import { DeterministicEngine, type StrategyDetector } from "../src/engine/deterministic-engine.js";
import type { EngineDecision, MarketSnapshot, StrategyProvenance } from "../src/domain/market.js";

const canonical: StrategyProvenance = {
  strategyId: "SP2L",
  version: "source-core-v1",
  ruleIds: ["SOURCE_CONFIRMED_CORE"],
  canonical: true,
};

function detector(decision: EngineDecision): StrategyDetector {
  return {
    id: "fixture",
    provenance: canonical,
    evaluate: (_history: readonly MarketSnapshot[]) => decision,
  };
}

const candle = {
  timestamp: "2026-01-01T00:00:00Z",
  open: 2600,
  high: 2605,
  low: 2595,
  close: 2602,
  timeframe: "5m",
};

describe("DeterministicEngine", () => {
  it("blocks non-canonical signal candidates", () => {
    const decision: EngineDecision = {
      status: "SIGNAL",
      reason: "hypothesis",
      candidate: {
        symbol: "XAUUSD",
        direction: "LONG",
        timestamp: candle.timestamp,
        entryType: "PENDING_LIMIT",
        entryPrice: 2600,
        stopPrice: 2590,
        targetPrice: 2620,
        riskPrice: 10,
        expectedR: 2,
        provenance: { ...canonical, canonical: false },
      },
    };

    const engine = new DeterministicEngine({
      symbol: "XAUUSD",
      timeframe: "5m",
      strategy: detector(decision),
    });

    expect(engine.push(candle)).toEqual({
      status: "BLOCKED",
      reason: "NON_CANONICAL_STRATEGY_CANNOT_EMIT_SIGNAL",
    });
  });

  it("accepts a canonical, internally consistent signal", () => {
    const decision: EngineDecision = {
      status: "SIGNAL",
      reason: "canonical fixture",
      candidate: {
        symbol: "XAUUSD",
        direction: "LONG",
        timestamp: candle.timestamp,
        entryType: "PENDING_LIMIT",
        entryPrice: 2600,
        stopPrice: 2590,
        targetPrice: 2620,
        riskPrice: 10,
        expectedR: 2,
        provenance: canonical,
      },
    };

    const engine = new DeterministicEngine({
      symbol: "XAUUSD",
      timeframe: "5m",
      strategy: detector(decision),
    });

    expect(engine.push(candle).status).toBe("SIGNAL");
  });

  it("blocks timeframe mismatch before strategy evaluation", () => {
    const engine = new DeterministicEngine({
      symbol: "XAUUSD",
      timeframe: "5m",
      strategy: detector({ status: "NO_SIGNAL", reason: "unused" }),
    });

    expect(engine.push({ ...candle, timeframe: "1m" })).toEqual({
      status: "BLOCKED",
      reason: "TIMEFRAME_MISMATCH:1m",
    });
    expect(engine.snapshots()).toHaveLength(0);
  });
});
