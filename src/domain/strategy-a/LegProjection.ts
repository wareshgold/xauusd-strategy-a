import type { Candle } from '../market/Candle.js';
import type { Correction } from './CorrectionDetector.js';

export interface LegProjection {
  readonly direction: 'BUY' | 'SELL';
  readonly leg1StartIndex: number;
  readonly leg1EndIndex: number;
  readonly leg1Size: number;
  readonly projectionFrom: number;
  readonly tp1: number;
}

export function projectLeg2(candles: readonly Candle[], correction: Correction): LegProjection | null {
  const first = candles[correction.spikeStartIndex];
  const last = candles[correction.spikeEndIndex];
  if (!first || !last) return null;
  const leg1Size = Math.abs(last.close - first.open);
  if (!Number.isFinite(leg1Size) || leg1Size <= 0) return null;
  const direction = correction.direction === 'BULLISH' ? 'BUY' : 'SELL';
  const projectionFrom = correction.extremePrice;
  return { direction, leg1StartIndex: correction.spikeStartIndex, leg1EndIndex: correction.spikeEndIndex, leg1Size, projectionFrom, tp1: direction === 'BUY' ? projectionFrom + leg1Size : projectionFrom - leg1Size };
}
