import type { Candle } from '../market/Candle.js';
import type { Correction } from './CorrectionDetector.js';

export interface InvalidationRule {
  readonly direction: 'BUY' | 'SELL';
  readonly invalidationLevel: number;
  readonly reason: 'CORRECTION_EXTREME_BREACH';
}

export function getInvalidationRule(correction: Correction): InvalidationRule {
  return {
    direction: correction.direction === 'BULLISH' ? 'BUY' : 'SELL',
    invalidationLevel: correction.extremePrice,
    reason: 'CORRECTION_EXTREME_BREACH',
  };
}

export function isInvalidated(candle: Candle, rule: InvalidationRule): boolean {
  return rule.direction === 'BUY'
    ? candle.close < rule.invalidationLevel
    : candle.close > rule.invalidationLevel;
}
