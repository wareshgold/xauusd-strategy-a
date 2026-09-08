import { describe, expect, it } from 'vitest';
import {
  evaluateAllPGapHypotheses,
  type ResearchCandle,
} from '../src/research/sp2l/PGapHypotheses';

const c = (open: number, high: number, low: number, close: number): ResearchCandle => ({
  open,
  high,
  low,
  close,
});

describe('SP2L P-Gap hypothesis discrimination (research only)', () => {
  it('distinguishes adjacent-gap timing from three-candle outer-gap timing', () => {
    const candles = [
      c(104, 105, 100, 103),
      c(103, 110, 101, 109),
      c(109, 112, 106, 111),
    ];

    expect(evaluateAllPGapHypotheses('BUY', candles)).toEqual({
      H1_ADJACENT_WICK: false,
      H2_THREE_CANDLE_OUTER_WICK: true,
      H3_ADJACENT_BODY: false,
      H4_THREE_CANDLE_OUTER_BODY: true,
    });
  });

  it('shows body separation without wick separation', () => {
    const candles = [
      c(105, 112, 100, 107),
      c(103, 110, 101, 105),
      c(106, 108, 104, 107),
    ];

    expect(evaluateAllPGapHypotheses('BUY', candles)).toEqual({
      H1_ADJACENT_WICK: false,
      H2_THREE_CANDLE_OUTER_WICK: false,
      H3_ADJACENT_BODY: true,
      H4_THREE_CANDLE_OUTER_BODY: false,
    });
  });

  it('treats exact boundary touch as not a strict gap', () => {
    const candles = [
      c(100, 105, 98, 104),
      c(104, 110, 101, 108),
      c(108, 112, 110, 111),
    ];

    expect(evaluateAllPGapHypotheses('BUY', candles).H1_ADJACENT_WICK).toBe(false);
  });

  it('mirrors the timing distinction for bearish structures', () => {
    const candles = [
      c(106, 110, 105, 108),
      c(109, 111, 100, 102),
      c(102, 104, 94, 98),
    ];

    expect(evaluateAllPGapHypotheses('SELL', candles)).toEqual({
      H1_ADJACENT_WICK: false,
      H2_THREE_CANDLE_OUTER_WICK: true,
      H3_ADJACENT_BODY: false,
      H4_THREE_CANDLE_OUTER_BODY: true,
    });
  });

  it('does not turn the hypothesis result into a canonical decision', () => {
    // This test intentionally checks only the research API shape. A boolean
    // candidate result is not a Strategy A/P-Gap confirmation.
    const result = evaluateAllPGapHypotheses('BUY', [
      c(100, 101, 99, 100),
      c(100, 102, 99, 101),
      c(103, 105, 103, 104),
    ]);

    expect(Object.keys(result)).toEqual([
      'H1_ADJACENT_WICK',
      'H2_THREE_CANDLE_OUTER_WICK',
      'H3_ADJACENT_BODY',
      'H4_THREE_CANDLE_OUTER_BODY',
    ]);
  });
});
