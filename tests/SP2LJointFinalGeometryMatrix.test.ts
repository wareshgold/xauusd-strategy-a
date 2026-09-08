import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'STRONGEST_CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const matrix = {
  pGapSemantic: 'SOURCE_CONFIRMED' as Resolution,
  pGapExactBoundary: 'UNRESOLVED' as Resolution,
  genericFVG: 'REJECTED' as Resolution,
  entryPriorExtremeSemantic: 'SOURCE_CONFIRMED' as Resolution,
  entryUniversalCandleIndex: 'UNRESOLVED' as Resolution,
  entryExactOHLC: 'UNRESOLVED' as Resolution,
  slOriginSemantic: 'SOURCE_CONFIRMED' as Resolution,
  slExactPrice: 'UNRESOLVED' as Resolution,
  leg1Semantic: 'SOURCE_CONFIRMED' as Resolution,
  leg1ExactOHLC: 'UNRESOLVED' as Resolution,
  classicalABCD: 'REJECTED' as Resolution,
  abEqualCdTolerance: 'UNRESOLVED' as Resolution,
};

describe('SP2L joint final geometry resolution guardrails', () => {
  it('keeps P-Gap source-confirmed but exact geometry unresolved', () => {
    expect(matrix.pGapSemantic).toBe('SOURCE_CONFIRMED');
    expect(matrix.pGapExactBoundary).toBe('UNRESOLVED');
    expect(matrix.genericFVG).toBe('REJECTED');
  });

  it('keeps Entry separate from P-Gap and preserves prior-extreme semantics', () => {
    expect(matrix.entryPriorExtremeSemantic).toBe('SOURCE_CONFIRMED');
    expect(matrix.entryUniversalCandleIndex).toBe('UNRESOLVED');
    expect(matrix.entryExactOHLC).toBe('UNRESOLVED');
  });

  it('keeps SL structural semantics without inventing an executable price', () => {
    expect(matrix.slOriginSemantic).toBe('SOURCE_CONFIRMED');
    expect(matrix.slExactPrice).toBe('UNRESOLVED');
  });

  it('keeps Leg-1 source semantics while exact OHLC anchors remain open', () => {
    expect(matrix.leg1Semantic).toBe('SOURCE_CONFIRMED');
    expect(matrix.leg1ExactOHLC).toBe('UNRESOLVED');
  });

  it('rejects classical harmonic anchors and invented AB=CD tolerance', () => {
    expect(matrix.classicalABCD).toBe('REJECTED');
    expect(matrix.abEqualCdTolerance).toBe('UNRESOLVED');
  });
});
