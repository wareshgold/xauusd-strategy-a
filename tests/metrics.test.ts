import { describe, expect, it } from "vitest";
import { calculateTradeMetrics } from "../src/research/metrics.js";
import type { TradeRecord } from "../src/replay/trade-ledger.js";

const trade = (id: string, realizedR: number): TradeRecord => ({
  id,
  symbol: "XAUUSD",
  direction: "LONG",
  signalTimestamp: `2026-01-01T00:0${id.length}Z`,
  entryPrice: 2600,
  stopPrice: 2590,
  targetPrice: 2620,
  riskPrice: 10,
  expectedR: 2,
  status: realizedR > 0 ? "WON" : "LOST",
  exitTimestamp: `2026-01-01T00:1${id.length}Z`,
  exitPrice: realizedR > 0 ? 2620 : 2590,
  realizedR,
});

describe("calculateTradeMetrics", () => {
  it("calculates descriptive R metrics", () => {
    const metrics = calculateTradeMetrics([trade("a", 2), trade("b", -1), trade("c", -1), trade("d", 3)]);
    expect(metrics.closedTrades).toBe(4);
    expect(metrics.wins).toBe(2);
    expect(metrics.losses).toBe(2);
    expect(metrics.winRate).toBe(0.5);
    expect(metrics.totalR).toBe(3);
    expect(metrics.averageR).toBe(0.75);
    expect(metrics.medianR).toBe(0.5);
    expect(metrics.profitFactor).toBe(2.5);
    expect(metrics.maxDrawdownR).toBe(2);
    expect(metrics.maxConsecutiveLosses).toBe(2);
  });

  it("ignores open and cancelled records without realized R", () => {
    const records: TradeRecord[] = [
      trade("a", 2),
      { ...trade("b", 0), status: "CANCELLED", realizedR: undefined },
      { ...trade("c", 0), status: "OPEN", realizedR: undefined },
    ];
    const metrics = calculateTradeMetrics(records);
    expect(metrics.closedTrades).toBe(1);
    expect(metrics.totalR).toBe(2);
  });
});
