/**
 * Research-only P-Gap hypothesis evaluators.
 *
 * IMPORTANT: none of these functions is canonical Strategy A logic.
 * They exist solely to discriminate competing geometric interpretations
 * with synthetic fixtures before any historical research is permitted.
 */

export interface ResearchCandle {
  readonly open: number;
  readonly high: number;
  readonly low: number;
  readonly close: number;
}

export type PGapHypothesis =
  | 'H1_ADJACENT_WICK'
  | 'H2_THREE_CANDLE_OUTER_WICK'
  | 'H3_ADJACENT_BODY'
  | 'H4_THREE_CANDLE_OUTER_BODY';

function bodyHigh(c: ResearchCandle): number {
  return Math.max(c.open, c.close);
}

function bodyLow(c: ResearchCandle): number {
  return Math.min(c.open, c.close);
}

export function evaluatePGapHypothesis(
  hypothesis: PGapHypothesis,
  side: 'BUY' | 'SELL',
  candles: readonly ResearchCandle[],
): boolean {
  const needsThree = hypothesis.startsWith('H2_') || hypothesis.startsWith('H4_');
  if (candles.length < (needsThree ? 3 : 2)) return false;

  const previousIndex = candles.length - 2;
  const currentIndex = candles.length - 1;
  const previous = candles[previousIndex];
  const current = candles[currentIndex];
  if (!previous || !current) return false;

  const a = needsThree ? candles[candles.length - 3] : undefined;
  if (needsThree && !a) return false;

  switch (hypothesis) {
    case 'H1_ADJACENT_WICK':
      return side === 'BUY' ? current.low > previous.high : current.high < previous.low;
    case 'H2_THREE_CANDLE_OUTER_WICK':
      return side === 'BUY' ? current.low > a!.high : current.high < a!.low;
    case 'H3_ADJACENT_BODY':
      return side === 'BUY'
        ? bodyLow(current) > bodyHigh(previous)
        : bodyHigh(current) < bodyLow(previous);
    case 'H4_THREE_CANDLE_OUTER_BODY':
      return side === 'BUY'
        ? bodyLow(current) > bodyHigh(a!)
        : bodyHigh(current) < bodyLow(a!);
  }
}

export function evaluateAllPGapHypotheses(
  side: 'BUY' | 'SELL',
  candles: readonly ResearchCandle[],
): Record<PGapHypothesis, boolean> {
  return {
    H1_ADJACENT_WICK: evaluatePGapHypothesis('H1_ADJACENT_WICK', side, candles),
    H2_THREE_CANDLE_OUTER_WICK: evaluatePGapHypothesis('H2_THREE_CANDLE_OUTER_WICK', side, candles),
    H3_ADJACENT_BODY: evaluatePGapHypothesis('H3_ADJACENT_BODY', side, candles),
    H4_THREE_CANDLE_OUTER_BODY: evaluatePGapHypothesis('H4_THREE_CANDLE_OUTER_BODY', side, candles),
  };
}
