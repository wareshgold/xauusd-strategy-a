import type { Candle } from '../market/Candle.js';
import type { SpikeCandidate } from './SpikeCandidate.js';

export interface Correction {
  readonly spikeStartIndex: number;
  readonly spikeEndIndex: number;
  readonly correctionStartIndex: number;
  readonly correctionExtremeIndex: number;
  readonly direction: SpikeCandidate['direction'];
  readonly extremePrice: number;
}

export function detectFirstCorrection(candles: readonly Candle[], spike: SpikeCandidate): Correction | null {
  const start = spike.endIndex + 1;
  if (start >= candles.length) return null;
  if (spike.direction === 'BULLISH') {
    for (let i = start; i < candles.length; i += 1) {
      if (candles[i]!.low < spike.startPrice) {
        return { spikeStartIndex: spike.startIndex, spikeEndIndex: spike.endIndex, correctionStartIndex: start, correctionExtremeIndex: i, direction: spike.direction, extremePrice: candles[i]!.low };
      }
    }
  } else {
    for (let i = start; i < candles.length; i += 1) {
      if (candles[i]!.high > spike.startPrice) {
        return { spikeStartIndex: spike.startIndex, spikeEndIndex: spike.endIndex, correctionStartIndex: start, correctionExtremeIndex: i, direction: spike.direction, extremePrice: candles[i]!.high };
      }
    }
  }
  return null;
}
