import type { Candle } from '../domain/market/Candle.js';

export interface ReplayEvent { readonly index:number; readonly candle:Candle; readonly visibleCandles:readonly Candle[]; }
export type ReplayHandler = (event: ReplayEvent) => void;

/** Deterministic chronological replay. The handler only receives candles available at that timestamp. */
export function replayCandles(candles: readonly Candle[], handler: ReplayHandler): void {
  for (let i=0;i<candles.length;i+=1) handler({ index:i, candle:candles[i]!, visibleCandles:candles.slice(0,i+1) });
}
