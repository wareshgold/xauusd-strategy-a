export type StructuralStopDirection = 'BULLISH' | 'BEARISH';

export interface SpikeOriginCandle {
  index: number;
  high: number;
  low: number;
}

export interface StructuralStopCandidate {
  status: 'CANDIDATE';
  originCandleIndex: number;
  stopPrice: number;
  rationale: string;
  bufferStatus: 'TBD';
}

/**
 * G3 research candidate only.
 *
 * Public SP2L descriptions place the stop behind the candle where the
 * spike originated. This helper exposes that candle's structural extreme
 * without inventing a numeric buffer.
 */
export function resolveStructuralStopCandidate(
  direction: StructuralStopDirection,
  originCandle: SpikeOriginCandle,
): StructuralStopCandidate {
  if (!Number.isFinite(originCandle.high) || !Number.isFinite(originCandle.low)) {
    throw new Error('STRUCTURAL_STOP_REQUIRES_FINITE_CANDLE');
  }

  const stopPrice = direction === 'BULLISH' ? originCandle.low : originCandle.high;

  return {
    status: 'CANDIDATE',
    originCandleIndex: originCandle.index,
    stopPrice,
    rationale:
      direction === 'BULLISH'
        ? 'G3_CANDIDATE_BULLISH_SPIKE_ORIGIN_LOW'
        : 'G3_CANDIDATE_BEARISH_SPIKE_ORIGIN_HIGH',
    bufferStatus: 'TBD',
  };
}
