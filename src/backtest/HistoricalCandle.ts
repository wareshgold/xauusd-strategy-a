import type { Candle } from '../domain/market/Candle.js';

export interface HistoricalCandle extends Candle {
  readonly timeframe: '1min' | '5min';
  readonly source: string;
}

export interface HistoricalDataset {
  readonly symbol: 'XAU/USD';
  readonly timeframe: HistoricalCandle['timeframe'];
  readonly source: string;
  readonly candles: readonly HistoricalCandle[];
}

export function normalizeHistoricalCandles(rows: readonly Omit<HistoricalCandle, 'timeframe' | 'source'>[], timeframe: HistoricalCandle['timeframe'], source: string): HistoricalDataset {
  const candles = rows.map((row) => ({ ...row, timeframe, source }));
  for (let i = 1; i < candles.length; i += 1) {
    if (candles[i]!.timestamp <= candles[i - 1]!.timestamp) throw new Error('Historical candles must be strictly chronological');
  }
  return { symbol: 'XAU/USD', timeframe, source, candles };
}
