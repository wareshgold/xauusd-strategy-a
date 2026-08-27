import type { Candle } from '../market/Candle.js';
import type { Correction } from './CorrectionDetector.js';

export type EntryDirection = 'BUY' | 'SELL';

export interface EntryTrigger {
  readonly index: number;
  readonly timestamp: string;
  readonly direction: EntryDirection;
  readonly entryPrice: number;
  readonly triggerLevel: number;
  readonly reason: 'CORRECTION_EXTREME_RECLAIM';
}

/** Research-stage trigger: confirmation requires a close back through the correction extreme. */
export function detectEntryTrigger(candles: readonly Candle[], correction: Correction): EntryTrigger | null {
  for (let i = correction.correctionExtremeIndex + 1; i < candles.length; i += 1) {
    const candle = candles[i]!;
    if (correction.direction === 'BULLISH' && candle.close > correction.extremePrice) {
      return { index: i, timestamp: candle.timestamp, direction: 'BUY', entryPrice: candle.close, triggerLevel: correction.extremePrice, reason: 'CORRECTION_EXTREME_RECLAIM' };
    }
    if (correction.direction === 'BEARISH' && candle.close < correction.extremePrice) {
      return { index: i, timestamp: candle.timestamp, direction: 'SELL', entryPrice: candle.close, triggerLevel: correction.extremePrice, reason: 'CORRECTION_EXTREME_RECLAIM' };
    }
  }
  return null;
}
