import { assertValidCandle } from './Candle.js';
import type { Candle } from './Candle.js';

export interface DataQualityReport {
  readonly totalCandles: number;
  readonly duplicateTimestamps: string[];
  readonly outOfOrderTimestamps: string[];
  readonly gaps: Array<{ from: string; to: string; missingMinutes: number }>;
  readonly invalidCandles: string[];
}

export function inspectM1Data(candles: readonly Candle[]): DataQualityReport {
  const duplicateTimestamps: string[] = [];
  const outOfOrderTimestamps: string[] = [];
  const gaps: DataQualityReport['gaps'] = [];
  const invalidCandles: string[] = [];
  const seen = new Set<string>();

  for (let i = 0; i < candles.length; i += 1) {
    const candle = candles[i]!;
    if (seen.has(candle.timestamp)) duplicateTimestamps.push(candle.timestamp);
    seen.add(candle.timestamp);
    try { assertValidCandle(candle); } catch { invalidCandles.push(candle.timestamp); }

    if (i === 0) continue;
    const previous = candles[i - 1]!;
    const deltaMinutes = (Date.parse(candle.timestamp) - Date.parse(previous.timestamp)) / 60_000;
    if (deltaMinutes <= 0) outOfOrderTimestamps.push(candle.timestamp);
    else if (deltaMinutes > 1) gaps.push({ from: previous.timestamp, to: candle.timestamp, missingMinutes: deltaMinutes - 1 });
  }

  return { totalCandles: candles.length, duplicateTimestamps, outOfOrderTimestamps, gaps, invalidCandles };
}
