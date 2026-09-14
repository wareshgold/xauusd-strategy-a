import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";
import type { Candle } from "../domain/market.js";

export interface CsvReplayOptions {
  readonly symbol: string;
  readonly timeframe: string;
  readonly delimiter?: string;
}

export type CandleSink = (candle: Candle) => void | Promise<void>;

/**
 * Streaming CSV replay adapter. It only maps OHLC data into the domain candle
 * contract; it contains no Strategy A detection or execution assumptions.
 */
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

    const row = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const candle = parseCandle(row, options.timeframe);
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
  const candle: Candle = {
    timestamp: row.timestamp,
    open: number(row.open, "open"),
    high: number(row.high, "high"),
    low: number(row.low, "low"),
    close: number(row.close, "close"),
    timeframe,
  };

  if (!candle.timestamp || Number.isNaN(Date.parse(candle.timestamp))) {
    throw new Error(`CSV_INVALID_TIMESTAMP:${candle.timestamp}`);
  }
  if (candle.high < Math.max(candle.open, candle.close) || candle.low > Math.min(candle.open, candle.close)) {
    throw new Error(`CSV_INVALID_OHLC:${candle.timestamp}`);
  }
  return candle;
}

function number(value: string, field: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`CSV_INVALID_NUMBER:${field}`);
  return parsed;
}
