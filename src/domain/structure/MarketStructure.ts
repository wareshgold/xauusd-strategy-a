import type { Candle } from '../market/Candle.js';

export type SwingType = 'HH' | 'HL' | 'LH' | 'LL';

export interface SwingPoint {
  readonly index: number;
  readonly timestamp: string;
  readonly price: number;
  readonly type: SwingType;
}

export interface StructureConfig {
  readonly pivotLeft: number;
  readonly pivotRight: number;
}

export function detectSwingPoints(candles: readonly Candle[], config: StructureConfig): SwingPoint[] {
  if (config.pivotLeft < 1 || config.pivotRight < 1) throw new Error('Pivot sizes must be positive');
  const candidates: Array<{ index: number; timestamp: string; price: number; side: 'high' | 'low' }> = [];

  for (let i = config.pivotLeft; i < candles.length - config.pivotRight; i += 1) {
    const candle = candles[i]!;
    let isHigh = true;
    let isLow = true;
    for (let j = i - config.pivotLeft; j <= i + config.pivotRight; j += 1) {
      if (j === i) continue;
      const other = candles[j]!;
      if (other.high >= candle.high) isHigh = false;
      if (other.low <= candle.low) isLow = false;
    }
    if (isHigh) candidates.push({ index: i, timestamp: candle.timestamp, price: candle.high, side: 'high' });
    if (isLow) candidates.push({ index: i, timestamp: candle.timestamp, price: candle.low, side: 'low' });
  }

  candidates.sort((a, b) => a.index - b.index || (a.side === 'high' ? -1 : 1));
  const previousBySide: Partial<Record<'high' | 'low', number>> = {};
  const result: SwingPoint[] = [];
  for (const point of candidates) {
    const previous = previousBySide[point.side];
    if (previous === undefined) {
      previousBySide[point.side] = point.price;
      continue;
    }
    const type: SwingType = point.side === 'high'
      ? point.price > previous ? 'HH' : 'LH'
      : point.price > previous ? 'HL' : 'LL';
    result.push({ index: point.index, timestamp: point.timestamp, price: point.price, type });
    previousBySide[point.side] = point.price;
  }
  return result;
}
