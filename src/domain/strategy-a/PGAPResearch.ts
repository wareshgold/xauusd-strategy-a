import type { Candle } from '../market/Candle.js';
import type { SpikeCandidate } from './SpikeCandidate.js';

export type PGAPClassification = 'CANDIDATE' | 'NOT_CANDIDATE' | 'UNKNOWN';

export interface PGAPObservation {
  readonly index: number;
  readonly classification: PGAPClassification;
  readonly direction: 'BULLISH' | 'BEARISH';
  readonly upper: number;
  readonly lower: number;
  readonly size: number;
  readonly note: string;
}

/**
 * Research layer: records three-candle imbalance observations without
 * declaring them to be true P-GAPs. The actual P-GAP definition is an
 * unresolved Strategy A rule and must be validated before activation.
 */
export function collectPGAPObservations(
  candles: readonly Candle[],
  spike: SpikeCandidate,
): PGAPObservation[] {
  const observations: PGAPObservation[] = [];
  const from = Math.max(2, spike.startIndex);
  const to = Math.min(candles.length - 1, spike.endIndex + 1);

  for (let i = from; i <= to; i += 1) {
    const left = candles[i - 2]!;
    const right = candles[i]!;
    if (spike.direction === 'BULLISH' && right.low > left.high) {
      observations.push({ index: i, classification: 'CANDIDATE', direction: 'BULLISH', upper: right.low, lower: left.high, size: right.low - left.high, note: 'Three-candle bullish imbalance candidate; not yet validated as P-GAP.' });
    } else if (spike.direction === 'BEARISH' && right.high < left.low) {
      observations.push({ index: i, classification: 'CANDIDATE', direction: 'BEARISH', upper: left.low, lower: right.high, size: left.low - right.high, note: 'Three-candle bearish imbalance candidate; not yet validated as P-GAP.' });
    } else {
      observations.push({ index: i, classification: 'NOT_CANDIDATE', direction: spike.direction, upper: Math.max(left.high, right.high), lower: Math.min(left.low, right.low), size: 0, note: 'No three-candle imbalance observed under the research heuristic.' });
    }
  }
  return observations;
}
