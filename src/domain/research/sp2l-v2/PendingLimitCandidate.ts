export type PendingLimitDirection = 'BULLISH' | 'BEARISH';

export interface EntryLevelCandle {
  index: number;
  high: number;
  low: number;
}

export interface PendingLimitCandidate {
  status: 'CANDIDATE';
  sourceCandleIndex: number;
  entryPrice: number;
  rationale: string;
}

/**
 * G2 research candidate only.
 *
 * Public SP2L descriptions state that during a bullish spike, consecutive
 * higher lows create potential buy-entry levels, while during a bearish spike,
 * consecutive lower highs create potential sell-entry levels. The actual
 * entry is activated when price returns to retest that level.
 *
 * This helper treats a supplied HL/LH candle as a pending-limit candidate. It
 * deliberately does not decide how the spike, HL/LH sequence, validity
 * window, or final execution policy is detected.
 */
export function createPendingLimitCandidate(
  direction: PendingLimitDirection,
  sourceCandle: EntryLevelCandle,
): PendingLimitCandidate {
  if (!Number.isFinite(sourceCandle.high) || !Number.isFinite(sourceCandle.low)) {
    throw new Error('PENDING_LIMIT_REQUIRES_FINITE_CANDLE');
  }

  const entryPrice = direction === 'BULLISH' ? sourceCandle.low : sourceCandle.high;

  return {
    status: 'CANDIDATE',
    sourceCandleIndex: sourceCandle.index,
    entryPrice,
    rationale:
      direction === 'BULLISH'
        ? 'G2_CANDIDATE_HL_LOW_PENDING_BUY'
        : 'G2_CANDIDATE_LH_HIGH_PENDING_SELL',
  };
}

export function isExactRetest(
  candidate: PendingLimitCandidate,
  touchedPrice: number,
): boolean {
  if (!Number.isFinite(touchedPrice)) {
    throw new Error('PENDING_LIMIT_RETEST_REQUIRES_FINITE_PRICE');
  }

  return touchedPrice === candidate.entryPrice;
}
