import { describe, expect, it } from 'vitest';
import { SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES } from './fixtures/SP2LLastSpikeCandleBreakout.fixtures.js';

describe('SP2L last-spike-candle breakout hypothesis discrimination', () => {
  it('contains explicit BUY correction-without-reclaim discrimination', () => {
    const fixture = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES.find(
      (item) => item.id === 'LSCB-BUY-CORRECTION-NO-RECLAIM',
    );

    expect(fixture).toBeDefined();
    expect(fixture?.sourcePendingLimitInterpretation).toBe('ENTRY_AVAILABLE');
    expect(fixture?.lastSpikeCandleBreakoutHypothesis).toBe('NOT_TRIGGERED');
  });

  it('contains explicit SELL correction-without-reclaim discrimination', () => {
    const fixture = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES.find(
      (item) => item.id === 'LSCB-SELL-CORRECTION-NO-RECLAIM',
    );

    expect(fixture).toBeDefined();
    expect(fixture?.sourcePendingLimitInterpretation).toBe('ENTRY_AVAILABLE');
    expect(fixture?.lastSpikeCandleBreakoutHypothesis).toBe('NOT_TRIGGERED');
  });

  it('records the bullish reclaim case where both interpretations progress', () => {
    const fixture = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES.find(
      (item) => item.id === 'LSCB-BUY-CORRECTION-THEN-RECLAIM',
    );

    expect(fixture).toBeDefined();
    expect(fixture?.sourcePendingLimitInterpretation).toBe('ENTRY_AVAILABLE');
    expect(fixture?.lastSpikeCandleBreakoutHypothesis).toBe('TRIGGERED');
  });

  it('records the bearish mirror of the reclaim case', () => {
    const fixture = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES.find(
      (item) => item.id === 'LSCB-SELL-CORRECTION-THEN-RECLAIM',
    );

    expect(fixture).toBeDefined();
    expect(fixture?.sourcePendingLimitInterpretation).toBe('ENTRY_AVAILABLE');
    expect(fixture?.lastSpikeCandleBreakoutHypothesis).toBe('TRIGGERED');
  });

  it('marks agreement cases as low discrimination value', () => {
    const fixture = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES.find(
      (item) => item.id === 'LSCB-BOTH-AGREE',
    );

    expect(fixture?.discriminationValue).toBe('LOW');
  });

  it('does not promote the secondary hypothesis to canonical Strategy A', () => {
    const all = SP2L_LAST_SPIKE_CANDLE_BREAKOUT_FIXTURES;

    expect(all.length).toBeGreaterThanOrEqual(5);
    expect(all.some((item) => item.sourcePendingLimitInterpretation === 'ENTRY_AVAILABLE')).toBe(true);
  });
});
