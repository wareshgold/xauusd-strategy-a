export type Timeframe = '1min' | '5min';

export interface Candle {
  readonly timestamp: string;
  readonly open: number;
  readonly high: number;
  readonly low: number;
  readonly close: number;
  readonly volume?: number;
}

export function assertValidCandle(candle: Candle): void {
  if (!Number.isFinite(candle.open) || !Number.isFinite(candle.high) || !Number.isFinite(candle.low) || !Number.isFinite(candle.close)) {
    throw new Error(`Invalid OHLC values at ${candle.timestamp}`);
  }
  if (candle.high < Math.max(candle.open, candle.close)) {
    throw new Error(`High is below open/close at ${candle.timestamp}`);
  }
  if (candle.low > Math.min(candle.open, candle.close)) {
    throw new Error(`Low is above open/close at ${candle.timestamp}`);
  }
}

export function candleRange(candle: Candle): number {
  return candle.high - candle.low;
}

export function candleBody(candle: Candle): number {
  return Math.abs(candle.close - candle.open);
}
