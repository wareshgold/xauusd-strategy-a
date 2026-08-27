import type { Candle } from './Candle.js';

export type SwingKind = 'HH' | 'HL' | 'LH' | 'LL';
export type SwingSide = 'HIGH' | 'LOW';

export interface SwingPoint {
  readonly index: number;
  readonly timestamp: string;
  readonly price: number;
  readonly side: SwingSide;
  readonly kind: SwingKind | 'INITIAL';
}

export interface StructureConfig {
  readonly leftBars: number;
  readonly rightBars: number;
}

export function detectSwingPoints(candles: readonly Candle[], config: StructureConfig): SwingPoint[] {
  if (config.leftBars < 1 || config.rightBars < 1) throw new Error('Pivot windows must be positive');
  const points: SwingPoint[] = [];
  let previousHigh: number | undefined;
  let previousLow: number | undefined;

  for (let i = config.leftBars; i < candles.length - config.rightBars; i += 1) {
    const candidate = candles[i]!;
    const left = candles.slice(i - config.leftBars, i);
    const right = candles.slice(i + 1, i + config.rightBars + 1);
    const isHigh = left.every((c) => candidate.high > c.high) && right.every((c) => candidate.high > c.high);
    const isLow = left.every((c) => candidate.low < c.low) && right.every((c) => candidate.low < c.low);

    if (isHigh) {
      const kind: SwingKind | 'INITIAL' = previousHigh === undefined ? 'INITIAL' : candidate.high > previousHigh ? 'HH' : 'LH';
      points.push({ index: i, timestamp: candidate.timestamp, price: candidate.high, side: 'HIGH', kind });
      previousHigh = candidate.high;
    }
    if (isLow) {
      const kind: SwingKind | 'INITIAL' = previousLow === undefined ? 'INITIAL' : candidate.low > previousLow ? 'HL' : 'LL';
      points.push({ index: i, timestamp: candidate.timestamp, price: candidate.low, side: 'LOW', kind });
      previousLow = candidate.low;
    }
  }

  return points.sort((a, b) => a.index - b.index);
}
