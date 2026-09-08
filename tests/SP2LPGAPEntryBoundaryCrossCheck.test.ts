import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'STRONGEST_CANDIDATE' | 'UNRESOLVED' | 'REJECTED_AS_CANONICAL';

const resolution = {
  breakoutAssociatedNonOverlap: 'SOURCE_CONFIRMED' as Resolution,
  previousHighToNextLowCandidate: 'STRONGEST_CANDIDATE' as Resolution,
  bodyBoundaryFormula: 'UNRESOLVED' as Resolution,
  wickPairFormula: 'UNRESOLVED' as Resolution,
  equalityTouchRule: 'UNRESOLVED' as Resolution,
  genericThreeCandleFVG: 'REJECTED_AS_CANONICAL' as Resolution,
  entryEqualsPGAPBoundary: 'REJECTED_AS_CANONICAL' as Resolution,
  entryPriorRelevantExtreme: 'STRONGEST_CANDIDATE' as Resolution,
};

describe('SP2L P-Gap / entry boundary source-resolution guardrails', () => {
  it('keeps breakout-associated non-overlap as the only source-confirmed P-Gap semantic', () => {
    expect(resolution.breakoutAssociatedNonOverlap).toBe('SOURCE_CONFIRMED');
  });

  it('does not freeze a specific OHLC P-Gap formula', () => {
    expect(resolution.previousHighToNextLowCandidate).toBe('STRONGEST_CANDIDATE');
    expect(resolution.bodyBoundaryFormula).toBe('UNRESOLVED');
    expect(resolution.wickPairFormula).toBe('UNRESOLVED');
  });

  it('does not invent equality or minimum-gap behavior', () => {
    expect(resolution.equalityTouchRule).toBe('UNRESOLVED');
  });

  it('rejects generic FVG as canonical Strategy A meaning without source confirmation', () => {
    expect(resolution.genericThreeCandleFVG).toBe('REJECTED_AS_CANONICAL');
  });

  it('keeps P-Gap boundary separate from pending-limit entry geometry', () => {
    expect(resolution.entryEqualsPGAPBoundary).toBe('REJECTED_AS_CANONICAL');
    expect(resolution.entryPriorRelevantExtreme).toBe('STRONGEST_CANDIDATE');
  });
});
