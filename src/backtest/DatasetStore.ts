import type { HistoricalDataset } from './HistoricalCandle.js';

export function serializeDataset(dataset: HistoricalDataset): string {
  return JSON.stringify(dataset, null, 2);
}

export function parseDataset(raw: string): HistoricalDataset {
  const value = JSON.parse(raw) as HistoricalDataset;
  if (value.symbol !== 'XAU/USD' || !Array.isArray(value.candles)) throw new Error('Invalid historical dataset');
  for (let i=1;i<value.candles.length;i+=1) if (value.candles[i]!.timestamp <= value.candles[i-1]!.timestamp) throw new Error('Dataset is not chronological');
  return value;
}
