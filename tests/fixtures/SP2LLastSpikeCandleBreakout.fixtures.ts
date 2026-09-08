export interface LastSpikeCandleBreakoutFixture {
  readonly id: string;
  readonly direction: 'BUY' | 'SELL';
  readonly description: string;
  readonly sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE' | 'NOT_REACHED';
  readonly lastSpikeCandleBreakoutHypothesis: 'TRIGGERED' | 'NOT_TRIGGERED';
  readonly discriminationValue: 'HIGH' | 'LOW';
}

/**
 * Research-only semantic fixtures for the secondary hypothesis:
 * correction followed by breakout/reclaim of the last Spike candle.
 *
 * These fixtures intentionally do not encode executable prices. They only
 * discriminate the event semantics against the source's pending-limit model.
 */
export const SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES: readonly LastSpikeCandleBreakoutFixture[] = [
  {
    id: 'LSCB-BUY-CORRECTION-NO-RECLAIM',
    direction: 'BUY',
    description: 'Bullish correction reaches the relevant low but never reclaims the last Spike candle.',
    sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE',
    lastSpikeCandleBreakoutHypothesis: 'NOT_TRIGGERED',
    discriminationValue: 'HIGH',
  },
  {
    id: 'LSCB-BUY-CORRECTION-THEN-RECLAIM',
    direction: 'BUY',
    description: 'Bullish correction reaches the relevant low and price later breaks/reclaims the last Spike candle.',
    sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE',
    lastSpikeCandleBreakoutHypothesis: 'TRIGGERED',
    discriminationValue: 'HIGH',
  },
  {
    id: 'LSCB-SELL-CORRECTION-NO-RECLAIM',
    direction: 'SELL',
    description: 'Bearish correction reaches the relevant high but never reclaims the last Spike candle to the downside.',
    sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE',
    lastSpikeCandleBreakoutHypothesis: 'NOT_TRIGGERED',
    discriminationValue: 'HIGH',
  },
  {
    id: 'LSCB-SELL-CORRECTION-THEN-RECLAIM',
    direction: 'SELL',
    description: 'Bearish correction reaches the relevant high and price later breaks/reclaims the last Spike candle to the downside.',
    sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE',
    lastSpikeCandleBreakoutHypothesis: 'TRIGGERED',
    discriminationValue: 'HIGH',
  },
  {
    id: 'LSCB-BOTH-AGREE',
    direction: 'BUY',
    description: 'Correction reaches the source reference and subsequent last-Spike-candle breakout also occurs; both interpretations agree on setup progression.',
    sourcePendingLimitInterpretation: 'ENTRY_AVAILABLE',
    lastSpikeCandleBreakoutHypothesis: 'TRIGGERED',
    discriminationValue: 'LOW',
  },
];
