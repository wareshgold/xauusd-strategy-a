import { normalizeHistoricalCandles, type HistoricalDataset } from './HistoricalCandle.js';
import type { TwelveDataResponse } from './TwelveDataDownloader.js';
import type { Candle } from '../domain/market/Candle.js';

export function twelveDataToDataset(data: TwelveDataResponse, timeframe: '1min'|'5min'): HistoricalDataset {
  if (!data.values?.length) throw new Error('Twelve Data returned no candles');
  const rows: Array<Candle> = data.values.map((v) => {
    const timestamp = v.datetime;
    const open = Number(v.open), high = Number(v.high), low = Number(v.low), close = Number(v.close);
    if (!timestamp || [open,high,low,close].some((n)=>!Number.isFinite(n))) throw new Error(`Invalid Twelve Data candle at ${timestamp ?? 'unknown'}`);
    return { timestamp, open, high, low, close, volume: v.volume === undefined ? undefined : Number(v.volume) };
  }).sort((a,b)=>a.timestamp.localeCompare(b.timestamp));
  const deduped = rows.filter((c,i)=>i===0 || c.timestamp!==rows[i-1]!.timestamp);
  return normalizeHistoricalCandles(deduped, timeframe, 'twelvedata');
}
