export type StructuralReferenceDirection = 'BULLISH' | 'BEARISH';

export interface StructuralReferenceCandle {
  index: number;
  high: number;
  low: number;
}

export interface StructuralReferenceCandidate {
  status: 'CANDIDATE';
  referenceCandleIndex: number;
  price: number;
  rationale: string;
}

/**
 * G1 research candidate only.
 *
 * Source-facing public documentation describes the second-leg correction as
 * reaching the low of the previous candle in bullish conditions and the high
 * of the previous candle in bearish conditions. This helper deliberately
 * models that relationship without claiming that it is the final canonical
 * structural-reference algorithm.
 */
export function resolvePreviousCandleReference(
  direction: StructuralReferenceDirection,
  previousCandle: StructuralReferenceCandle,
): StructuralReferenceCandidate {
  if (!Number.isFinite(previousCandle.high) || !Number.isFinite(previousCandle.low)) {
    throw new Error('STRUCTURAL_REFERENCE_REQUIRES_FINITE_CANDLE');
  }

  const price = direction === 'BULLISH' ? previousCandle.low : previousCandle.high;

  return {
    status: 'CANDIDATE',
    referenceCandleIndex: previousCandle.index,
    price,
    rationale:
      direction === 'BULLISH'
        ? 'G1_CANDIDATE_PREVIOUS_CANDLE_LOW'
        : 'G1_CANDIDATE_PREVIOUS_CANDLE_HIGH',
  };
}
