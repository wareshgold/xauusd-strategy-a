import { describe, expect, it } from 'vitest';
import { G395_HYPOTHESES, assertResearchOnly } from '../../src/domain/research/sp2l-v2/G396HypothesisProvenance.js';

type Candle = { open: number; high: number; low: number; close: number };

const bodyHigh = (b: Candle) => Math.max(b.open, b.close);
const bodyLow = (b: Candle) => Math.min(b.open, b.close);

function hypotheses(c: readonly Candle[]) {
  const [b0, b1, b2] = c;
  return {
    pg01: b2!.low > b0!.high,
    pg02: b0!.close > b0!.open && b1!.close > b1!.open && b2!.low > b0!.high,
    pg04: b2!.low > b0!.high && b1!.low > b0!.low,
    ab01: b1!.high - b0!.low,
    ab02: bodyHigh(b1!) - bodyLow(b0!),
    ab03: b1!.close - b0!.close
  };
}

/**
 * G397 deliberately does not choose a winning formula. Fixtures only prove
 * that competing interpretations can be separated by observable geometry.
 */
describe('G397 synthetic geometry discrimination', () => {
  it('separates the basic P-Gap candidates', () => {
    const fixture: Candle[] = [
      { open: 100, high: 110, low: 95, close: 108 },
      { open: 108, high: 116, low: 105, close: 114 },
      { open: 118, high: 125, low: 112, close: 122 }
    ];
    const h = hypotheses(fixture);
    expect(h.pg01).toBe(true);
    expect(h.pg02).toBe(true);
    expect(h.pg04).toBe(true);
  });

  it('constructs a minimal pair where candle direction changes H02 but not H01', () => {
    const base: Candle[] = [
      { open: 100, high: 110, low: 95, close: 108 },
      { open: 108, high: 116, low: 105, close: 106 },
      { open: 118, high: 125, low: 112, close: 122 }
    ];
    const h = hypotheses(base);
    expect(h.pg01).toBe(true);
    expect(h.pg02).toBe(false);
  });

  it('keeps competing AB=CD measurement definitions visibly distinct', () => {
    const fixture: Candle[] = [
      { open: 100, high: 130, low: 90, close: 120 },
      { open: 120, high: 150, low: 110, close: 140 },
      { open: 140, high: 160, low: 135, close: 155 }
    ];
    const h = hypotheses(fixture);
    expect(h.ab01).toBe(60);
    // H02 uses bodyHigh(b1) - bodyLow(b0) = 140 - 100 = 40.
    expect(h.ab02).toBe(40);
    expect(h.ab03).toBe(20);
    expect(new Set([h.ab01, h.ab02, h.ab03]).size).toBe(3);
  });

  it('does not promote any G395 hypothesis during synthetic discrimination', () => {
    expect(G395_HYPOTHESES).toHaveLength(14);
    for (const hypothesis of G395_HYPOTHESES) {
      expect(hypothesis.status).toBe('UNRESOLVED');
      expect(hypothesis.canonicalEligible).toBe(false);
      assertResearchOnly(hypothesis);
    }
  });
});
