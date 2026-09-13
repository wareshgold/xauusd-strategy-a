import { assignSplit, type DevConfig, type DevSplit, type RawCandle } from './G386DevHarness.js';

export interface DatasetRunResult {
  manifest: {
    symbol: string;
    provider: string;
    timeframe: string;
    timezone: string;
    datasetVersion: string;
    candleCount: number;
    firstTimestamp: string;
    lastTimestamp: string;
  };
  counts: Record<DevSplit, number>;
  ordered: boolean;
  duplicateTimestamps: number;
  leakageFree: boolean;
  canonicalTradesGenerated: number;
}

export function runDataset(candles: RawCandle[], config: DevConfig): DatasetRunResult {
  if (candles.length === 0) throw new Error('dataset must not be empty');
  let duplicates = 0;
  let ordered = true;
  const seen = new Set<string>();
  const counts: Record<DevSplit, number> = { DEV: 0, VAL: 0, HOLDOUT: 0 };
  let previous: string | undefined;

  for (const candle of candles) {
    if (previous !== undefined && candle.timestamp <= previous) ordered = false;
    previous = candle.timestamp;
    if (seen.has(candle.timestamp)) duplicates += 1;
    seen.add(candle.timestamp);
    const split = assignSplit(candle.timestamp, config);
    if (split) counts[split] += 1;
  }

  return {
    manifest: {
      symbol: candles[0]!.symbol,
      provider: candles[0]!.provider,
      timeframe: candles[0]!.timeframe,
      timezone: candles[0]!.timezone,
      datasetVersion: candles[0]!.datasetVersion,
      candleCount: candles.length,
      firstTimestamp: candles[0]!.timestamp,
      lastTimestamp: candles[candles.length - 1]!.timestamp
    },
    counts,
    ordered,
    duplicateTimestamps: duplicates,
    leakageFree: ordered && duplicates === 0,
    canonicalTradesGenerated: 0
  };
}
