import type { Candle } from './Candle.js';

export type BreakoutDirection = 'BULLISH' | 'BEARISH';

export interface BreakoutEvent {
  readonly index: number;
  readonly timestamp: string;
  readonly direction: BreakoutDirection;
  readonly brokenLevel: number;
  readonly close: number;
}

export function detectBreakout(candles: readonly Candle[], lookback: number): BreakoutEvent[] {
  if (lookback < 1) throw new Error('Breakout lookback must be positive');
  const events: BreakoutEvent[] = [];
  for (let i = lookback; i < candles.length; i += 1) {
    const candle = candles[i]!;
    const prior = candles.slice(i - lookback, i);
    const resistance = Math.max(...prior.map((c) => c.high));
    const support = Math.min(...prior.map((c) => c.low));
    if (candle.close > resistance) {
      events.push({ index: i, timestamp: candle.timestamp, direction: 'BULLISH', brokenLevel: resistance, close: candle.close });
    } else if (candle.close < support) {
      events.push({ index: i, timestamp: candle.timestamp, direction: 'BEARISH', brokenLevel: support, close: candle.close });
    }
  }
  return events;
}
