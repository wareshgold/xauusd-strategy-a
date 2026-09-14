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

  it("preserves valid market gaps without synthesizing candles", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "gap.csv");
    await writeFile(path, [
      "timestamp,open,high,low,close",
      "2026-01-02T21:55:00Z,2600,2605,2595,2602",
      "2026-01-05T00:00:00Z,2602,2610,2600,2608",
    ].join("\n"));

    const candles: Array<{ timestamp: string; timeframe: string }> = [];
    const count = await replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, (candle) => {
      candles.push({ timestamp: candle.timestamp, timeframe: candle.timeframe });
    });

    expect(count).toBe(2);
    expect(candles).toEqual([
      { timestamp: "2026-01-02T21:55:00Z", timeframe: "5m" },
      { timestamp: "2026-01-05T00:00:00Z", timeframe: "5m" },
    ]);
  });

  it("propagates the configured timeframe without inferring it from timestamp spacing", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "timeframe.csv");
    await writeFile(path, [
      "timestamp,open,high,low,close",
      "2026-01-01T00:00:00Z,2600,2605,2595,2602",
      "2026-01-01T00:05:00Z,2602,2610,2600,2608",
    ].join("\n"));

    const candles: unknown[] = [];
    await replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, (candle) => {
      candles.push(candle);
    });

    expect(candles[0]).toMatchObject({ timeframe: "5m" });
    expect(candles[1]).toMatchObject({ timeframe: "5m" });
  });

  it("accepts a boundary-valid candle when high equals the body maximum and low equals the body minimum", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "boundary.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,2602,2600,2602\n");

    const candles: unknown[] = [];
    await replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, (candle) => {
      candles.push(candle);
    });

    expect(candles).toHaveLength(1);
  });

  it("rejects a high below the candle body maximum", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "bad-high.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,2590,2585,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_OHLC");
  });

  it("rejects a low above the candle body minimum", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "bad-low.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,2610,2605,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_OHLC");
  });

  it("rejects non-finite OHLC values", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "non-finite.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,Infinity,2595,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_NUMBER:high");
  });

  it("rejects duplicate timestamps", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "duplicate.csv");
    await writeFile(path, [
      "timestamp,open,high,low,close",
      "2026-01-01T00:00:00Z,2600,2605,2595,2602",
      "2026-01-01T00:00:00Z,2602,2610,2600,2608",
    ].join("\n"));

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_NON_MONOTONIC_TIMESTAMP");
  });

  it("rejects timestamps that move backwards", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "backwards.csv");
    await writeFile(path, [
      "timestamp,open,high,low,close",
      "2026-01-01T00:05:00Z,2600,2605,2595,2602",
      "2026-01-01T00:00:00Z,2602,2610,2600,2608",
    ].join("\n"));

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_NON_MONOTONIC_TIMESTAMP");
  });

  it("rejects timestamps without an explicit timezone", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "timezone-less.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00,2600,2605,2595,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_TIMESTAMP");
  });

  it("accepts an explicit numeric timezone offset deterministically", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "offset.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T03:30:00+03:30,2600,2605,2595,2602\n");

    const candles: unknown[] = [];
    await replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, (candle) => {
      candles.push(candle);
    });

    expect(candles[0]).toMatchObject({ timestamp: "2026-01-01T03:30:00+03:30" });
  });

  it("rejects malformed OHLC rows", async () => {
    const dir = await mkdtemp(join(tmpdir(), "sp2l-replay-"));
    const path = join(dir, "bad.csv");
    await writeFile(path, "timestamp,open,high,low,close\n2026-01-01T00:00:00Z,2600,2590,2595,2602\n");

    await expect(replayCsv(path, { symbol: "XAUUSD", timeframe: "5m" }, () => undefined))
      .rejects.toThrow("CSV_INVALID_OHLC");
  });
});
