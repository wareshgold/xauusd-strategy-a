import { describe, expect, it } from 'vitest';

type Candidate = {
  readonly id: string;
  readonly sourceStatus: 'STRONG_CANDIDATE' | 'UNRESOLVED' | 'REJECTED_AS_CANONICAL';
};

/**
 * Research-only guardrails.
 * These tests intentionally do not implement a P-Gap formula or production
 * order logic. They prevent unresolved interpretations from being promoted
 * merely because they are convenient to code or profitable in a backtest.
 */
const candidates: readonly Candidate[] = [
  { id: 'prior-high-next-low-nonoverlap', sourceStatus: 'STRONG_CANDIDATE' },
  { id: 'body-only-gap', sourceStatus: 'UNRESOLVED' },
  { id: 'wick-only-gap', sourceStatus: 'UNRESOLVED' },
  { id: 'generic-three-candle-imbalance', sourceStatus: 'REJECTED_AS_CANONICAL' },
  { id: 'entry-at-prior-candle-low-high', sourceStatus: 'STRONG_CANDIDATE' },
  { id: 'entry-equals-classical-c-point', sourceStatus: 'UNRESOLVED' },
  { id: 'sl-exact-structural-anchor', sourceStatus: 'UNRESOLVED' },
];

describe('SP2L P-Gap / Entry / SL triangulation', () => {
  it('keeps source-supported candidates distinct from frozen rules', () => {
    expect(candidates.find((x) => x.id === 'prior-high-next-low-nonoverlap')?.sourceStatus)
      .toBe('STRONG_CANDIDATE');
    expect(candidates.find((x) => x.id === 'entry-at-prior-candle-low-high')?.sourceStatus)
      .toBe('STRONG_CANDIDATE');
  });

  it('does not canonize body-vs-wick semantics without source evidence', () => {
    expect(candidates.find((x) => x.id === 'body-only-gap')?.sourceStatus).toBe('UNRESOLVED');
    expect(candidates.find((x) => x.id === 'wick-only-gap')?.sourceStatus).toBe('UNRESOLVED');
  });

  it('does not import a generic three-candle imbalance as P-Gap', () => {
    expect(candidates.find((x) => x.id === 'generic-three-candle-imbalance')?.sourceStatus)
      .toBe('REJECTED_AS_CANONICAL');
  });

  it('keeps classical C-point mapping and exact SL anchor unresolved', () => {
    expect(candidates.find((x) => x.id === 'entry-equals-classical-c-point')?.sourceStatus)
      .toBe('UNRESOLVED');
    expect(candidates.find((x) => x.id === 'sl-exact-structural-anchor')?.sourceStatus)
      .toBe('UNRESOLVED');
  });
});
