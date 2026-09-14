import { describe, expect, it } from "vitest";
import { serializeRunManifest, type ReplayRunManifest } from "../src/replay/run-manifest.js";

describe("serializeRunManifest", () => {
  it("serializes a manifest deterministically", () => {
    const manifest: ReplayRunManifest = {
      runId: "run-001",
      datasetId: "xauusd-demo",
      datasetVersion: "2026-09-14T00:00:00Z",
      strategyId: "TEST",
      strategyVersion: "1",
      executionPolicy: "TOUCH_ENTRY/OHLC_AMBIGUOUS",
      symbol: "XAUUSD",
      timeframe: "1m",
      startedAt: "2026-09-14T10:00:00Z",
      completedAt: "2026-09-14T10:01:00Z",
      candleCount: 100,
      signalCount: 4,
      blockedCount: 0,
      noSignalCount: 96,
      executionEventCount: 8,
      ambiguousEventCount: 1,
    };

    expect(serializeRunManifest(manifest)).toBe(JSON.stringify(manifest, null, 2) + "\n");
  });
});
