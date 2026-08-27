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

/**
 * Finds the first confirmation candle that actually crosses the correction
 * extreme during the candle itself. The caller must provide only candles
 * available at the current replay time.
 */
export function detectEntryTrigger(candles: readonly Candle[], correction: Correction): EntryTrigger | null {
  const start = correction.correctionExtremeIndex + 1;
  if (start >= candles.length) return null;

  for (let i = start; i < candles.length; i += 1) {
    const candle = candles[i]!;

    if (correction.direction === 'BULLISH' && candle.open <= correction.extremePrice && candle.high > correction.extremePrice && candle.close > correction.extremePrice) {
      return {
        index: i,
        timestamp: candle.timestamp,
        direction: 'BUY',
        entryPrice: candle.close,
        triggerLevel: correction.extremePrice,
        reason: 'CORRECTION_EXTREME_RECLAIM',
      };
    }

    if (correction.direction === 'BEARISH' && candle.open >= correction.extremePrice && candle.low < correction.extremePrice && candle.close < correction.extremePrice) {
      return {
        index: i,
        timestamp: candle.timestamp,
        direction: 'SELL',
        entryPrice: candle.close,
        triggerLevel: correction.extremePrice,
        reason: 'CORRECTION_EXTREME_RECLAIM',
      };
    }
  }

  return null;
}
