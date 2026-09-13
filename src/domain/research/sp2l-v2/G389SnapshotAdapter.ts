import type { RawCandle } from './G386DevHarness.js';
import { runDataset, type DatasetRunResult } from './G388DatasetRunner.js';

export interface SnapshotRecord {
  symbol: string;
  timeframe: string;
  source: string;
  timezone: string;
  candles: Array<{ timestamp: string; open: number; high: number; low: number; close: number }>;
}

export function adaptSnapshot(record: SnapshotRecord, datasetVersion: string): RawCandle[] {
  return record.candles.map((candle) => ({
    ...candle,
    symbol: record.symbol,
    timeframe: record.timeframe,
    provider: record.source,
    timezone: record.timezone,
    datasetVersion
  }));
}

export function runSnapshot(record: SnapshotRecord, datasetVersion: string, config: Parameters<typeof runDataset>[1]): DatasetRunResult {
  return runDataset(adaptSnapshot(record, datasetVersion), config);
}
