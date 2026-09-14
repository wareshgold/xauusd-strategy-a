import { describe, expect, it } from "vitest";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { replayCsv } from "../src/replay/csv-replay.js";

describe("replayCsv", () => {
  it("streams valid OHLC rows in source order", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "xauusd.csv");
    await writeFile(path, [
      "timestamp,open,high,low,close",
      "2026-01-01T00:00:00Z,2600,2605,2595,2602",
      "2026-01-01T00:05:00Z,2602,2610,2600,2608",
    ].join("\n"));

    const candles: unknown[] = [];
    const count = await replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, (candle) => {
      candles.push(candle);
    });

    expect(count).toBe(2);
    expect(candles).toHaveLength(2);
    expect(candles[0]).toMatchObject({ close: 2602, timeframe: "5m" });
    expect(candles[1]).toMatchObject({ timestamp: "2026-01-01T00:05:00Z", open: 2602 });
  });

  it("rejects malformed OHLC rows", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "bad.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,2590,2595,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_OHLC");
  });
});
