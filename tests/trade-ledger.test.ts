import { describe, expect, it } from "vitest";
import { TradeLedger } from "../src/replay/trade-ledger.js";
import type { SignalCandidate } from "../src/domain/market.js";

const provenance = {
  strategyId: "SP2L",
  version: "source-core-v1",
  ruleIds: ["SOURCE_CONFIRMED_CORE"],
  canonical: true,
};

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
  provenance,
};

describe("TradeLedger", () => {
  it("records a target outcome as +R", () => {
    const ledger = new TradeLedger();
    ledger.open(candidate, "T-1");
    const trade = ledger.close("T-1", {
      timestamp: "2026-01-01T00:10:00Z",
      price: 2620,
      reason: "TARGET",
    });

    expect(trade.status).toBe("WON");
    expect(trade.realizedR).toBe(2);
  });

  it("records a stop outcome as -R", () => {
    const ledger = new TradeLedger();
    ledger.open(candidate, "T-2");
    const trade = ledger.close("T-2", {
      timestamp: "2026-01-01T00:10:00Z",
      price: 2590,
      reason: "STOP",
    });

    expect(trade.status).toBe("LOST");
    expect(trade.realizedR).toBe(-1);
  });

  it("keeps cancelled orders out of realized-R statistics", () => {
    const ledger = new TradeLedger();
    ledger.open(candidate, "T-3");
    const trade = ledger.close("T-3", {
      timestamp: "2026-01-01T00:05:00Z",
      reason: "CANCELLED",
    });

    expect(trade.status).toBe("CANCELLED");
    expect(trade.realizedR).toBeUndefined();
  });

  it("rejects duplicate and unknown trade ids", () => {
    const ledger = new TradeLedger();
    ledger.open(candidate, "T-4");
    expect(() => ledger.open(candidate, "T-4")).toThrow("DUPLICATE_TRADE_ID:T-4");
    expect(() => ledger.close("missing", {
      timestamp: "2026-01-01T00:10:00Z",
      price: 2620,
      reason: "TARGET",
    })).toThrow("UNKNOWN_TRADE_ID:missing");
  });
});
