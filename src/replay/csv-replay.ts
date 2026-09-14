import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";
import type { Candle } from "../domain/market.js";

export interface CsvReplayOptions {
  readonly symbol: string;
  readonly timeframe: string;
  readonly delimiter?: string;
}

export type CandleSink = (candle: Candle) => void | Promise<void>;

export async function replayCsv(
  path: string,
  options: CsvReplayOptions,
  sink: CandleSink,
): Promise<number> {
  const delimiter = options.delimiter ?? ",";
  const input = createReadStream(path, { encoding: "utf8" });
  const lines = createInterface({ input, crlfDelay: Infinity });

  let headers: string[] | undefined;
  let count = 0;
  let previousTimestampMs: number | undefined;

  for await (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (!headers) {
      headers = line.split(delimiter).map((value) => value.trim().toLowerCase());
      requireColumns(headers);
      continue;
    }

    const values = line.split(delimiter).map((value) => value.trim());
    if (values.length !== headers.length) {
      throw new Error(`CSV_COLUMN_COUNT:${count + 2}`);
    }

    const row: Record<string, string> = {};
    headers.forEach((header, index) => {
      const value = values[index];
      if (value !== undefined) row[header] = value;
    });
    const candle = parseCandle(row, options.timeframe);
    const timestampMs = Date.parse(candle.timestamp);
    if (previousTimestampMs !== undefined && timestampMs <= previousTimestampMs) {
      throw new Error(`CSV_NON_MONOTONIC_TIMESTAMP:${candle.timestamp}`);
    }
    previousTimestampMs = timestampMs;
    await sink(candle);
    count += 1;
  }

  return count;
}

function requireColumns(headers: readonly string[]): void {
  for (const required of ["timestamp", "open", "high", "low", "close"]) {
    if (!headers.includes(required)) throw new Error(`CSV_MISSING_COLUMN:${required}`);
  }
}

function parseCandle(row: Record<string, string>, timeframe: string): Candle {
  const timestamp = required(row.timestamp, "timestamp");
  const candle: Candle = {
    timestamp,
    open: number(required(row.open, "open"), "open"),
    high: number(required(row.high, "high"), "high"),
    low: number(required(row.low, "low"), "low"),
    close: number(required(row.close, "close"), "close"),
    timeframe,
  };

  if (Number.isNaN(Date.parse(candle.timestamp))) {
    throw new Error(`CSV_INVALID_TIMESTAMP:${candle.timestamp}`);
  }
  if (candle.high < Math.max(candle.open, candle.close) || candle.low > Math.min(candle.open, candle.close)) {
    throw new Error(`CSV_INVALID_OHLC:${candle.timestamp}`);
  }
  return candle;
}

function required(value: string | undefined, field: string): string {
  if (value === undefined || value === "") throw new Error(`CSV_MISSING_VALUE:${field}`);
  return value;
}

function number(value: string, field: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`CSV_INVALID_NUMBER:${field}`);
  return parsed;
}
