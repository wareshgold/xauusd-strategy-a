import { describe, expect, it } from "vitest";
import type { Candle, EngineDecision, StrategyDetector } from "../src/domain/market.js";
import { DeterministicEngine } from "../src/engine/deterministic-engine.js";
import { replayCandles } from "../src/replay/replay-runner.js";

const candles: Candle[] = [
  { timestamp: "2026-01-01T00:00:00Z", open: 2600, high: 2605, low: 2595, close: 2602, timeframe: "5m" },
  { timestamp: "2026-01-01T00:05:00Z", open: 2602, high: 2610, low: 2600, close: 2608, timeframe: "5m" },
  { timestamp: "2026-01-01T00:10:00Z", open: 2608, high: 2612, low: 2604, close: 2606, timeframe: "5m" },
];

function detector(decisionAt: number): StrategyDetector {
  return {
    id: "fixture",
    provenance: { strategyId: "fixture", version: "1", ruleIds: ["FIXTURE"], canonical: true },
    evaluate: (history) => history.length === decisionAt
      ? ({
          status: "SIGNAL",
          reason: "FIXTURE_SIGNAL",
          candidate: {
            symbol: "XAUUSD",
            direction: "LONG",
            timestamp: history.at(-1)!.candle.timestamp,
            entryType: "PENDING_LIMIT",
            entryPrice: 2600,
            stopPrice: 2590,
            targetPrice: 2620,
            riskPrice: 10,
            expectedR: 2,
            provenance: { strategyId: "fixture", version: "1", ruleIds: ["FIXTURE"], canonical: true },
          },
        })
      : ({ status: "NO_SIGNAL", reason: "NO_FIXTURE_SIGNAL" } as EngineDecision),
  };
}

describe("replayCandles", () => {
  it("replays every candle and counts decisions deterministically", () => {
    const result = replayCandles(
      new DeterministicEngine({ symbol: "XAUUSD", timeframe: "5m", strategy: detector(2) }),
      candles,
    );

    expect(result.candles).toBe(3);
    expect(result.signals).toBe(1);
    expect(result.blocked).toBe(0);
    expect(result.noSignals).toBe(2);
    expect(result.decisions[1]?.status).toBe("SIGNAL");
  });
});
