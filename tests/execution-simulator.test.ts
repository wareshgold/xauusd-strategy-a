import { describe, expect, it } from "vitest";
import type { SignalCandidate } from "../src/domain/market.js";
import { ExecutionSimulator } from "../src/replay/execution-simulator.js";
import { TradeLedger } from "../src/replay/trade-ledger.js";

const candidate: SignalCandidate = {
  symbol: "XAUUSD",
  direction: "LONG",
  timestamp: "2026-01-01T00:00:00Z",
  entryType: "PENDING_LIMIT",
  entryPrice: 2600,
  stopPrice: 2590,
  targetPrice: 2620,
  riskPrice: 10,
  expectedR: 2,
  provenance: { strategyId: "TEST", version: "0", ruleIds: ["fixture"], canonical: true },
};

const candle = (timestamp: string, open: number, high: number, low: number, close: number) => ({
  timestamp, open, high, low, close, timeframe: "5m",
});

describe("ExecutionSimulator", () => {
  it("fills a pending order when entry is touched and later closes at target", () => {
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    simulator.submit(candidate, "T1");
    expect(simulator.onCandle(candle("2026-01-01T00:05:00Z", 2605, 2610, 2599, 2608))[0]?.type).toBe("FILLED");
    expect(simulator.onCandle(candle("2026-01-01T00:10:00Z", 2610, 2620, 2608, 2618))[0]?.type).toBe("TARGET");
    expect(ledger.all()[0]?.realizedR).toBe(2);
  });

  it("does not invent intrabar ordering when stop and target are both touched", () => {
    const ledger = new TradeLedger();
    const simulator = new ExecutionSimulator(ledger, { fillRule: "TOUCH_ENTRY", intrabarRule: "OHLC_AMBIGUOUS" });

    simulator.submit(candidate, "T2");
    simulator.onCandle(candle("2026-01-01T00:05:00Z", 2605, 2610, 2599, 2608));
    const events = simulator.onCandle(candle("2026-01-01T00:10:00Z", 2605, 2620, 2585, 2600));

    expect(events[0]?.type).toBe("AMBIGUOUS");
    expect(ledger.all()[0]?.status).toBe("OPEN");
  });
});
