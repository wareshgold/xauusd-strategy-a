import type { Candle } from '../../domain/market/Candle.js';

/**
 * Deterministically derives UTC 5-minute candles from canonical M1 candles.
 * The input must contain complete M1 candles for a 5-minute bucket.
 */
export function aggregateM5(candles: readonly Candle[]): Candle[] {
  const sorted = [...candles].sort((a, b) => Date.parse(a.timestamp) - Date.parse(b.timestamp));
  const buckets = new Map<number, Candle[]>();

  for (const candle of sorted) {
    const time = Date.parse(candle.timestamp);
    if (!Number.isFinite(time)) throw new Error(`Invalid timestamp: ${candle.timestamp}`);
    const bucketStart = Math.floor(time / 300_000) * 300_000;
    const bucket = buckets.get(bucketStart) ?? [];
    bucket.push(candle);
    buckets.set(bucketStart, bucket);
  }

  const result: Candle[] = [];

  for (const [bucketStart, bucket] of [...buckets.entries()].sort(([a], [b]) => a - b)) {
    if (bucket.length !== 5) continue;

    const expected = Array.from({ length: 5 }, (_, index) => bucketStart + index * 60_000);
    const actual = bucket.map((candle) => Date.parse(candle.timestamp)).sort((a, b) => a - b);
    if (actual.some((timestamp, index) => timestamp !== expected[index])) continue;

    const ordered = [...bucket].sort((a, b) => Date.parse(a.timestamp) - Date.parse(b.timestamp));
    const first = ordered[0];
    const last = ordered[ordered.length - 1];
    if (!first || !last) continue;

    result.push({
      timestamp: new Date(bucketStart).toISOString(),
      open: first.open,
      high: Math.max(...ordered.map((candle) => candle.high)),
      low: Math.min(...ordered.map((candle) => candle.low)),
      close: last.close,
      ...(ordered.every((candle) => candle.volume !== undefined)
        ? { volume: ordered.reduce((sum, candle) => sum + (candle.volume ?? 0), 0) }
        : {}),
    });
  }

  return result;
}
