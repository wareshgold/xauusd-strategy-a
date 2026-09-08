import { describe, expect, it } from 'vitest';

type Resolution =
  | 'SOURCE_CONFIRMED'
  | 'SOURCE_CONFIRMED_SEMANTIC'
  | 'REJECTED'
  | 'REJECTED_AS_CANONICAL'
  | 'UNRESOLVED';

const finalResolution = {
  pGapRequiredForValidSpike: 'SOURCE_CONFIRMED' as Resolution,
  pGapExactBoundary: 'UNRESOLVED' as Resolution,
  pGapExactTiming: 'UNRESOLVED' as Resolution,
  genericFvgEqualsPGAP: 'REJECTED_AS_CANONICAL' as Resolution,
  bullishCorrectionReference: 'SOURCE_CONFIRMED_SEMANTIC' as Resolution,
  bearishCorrectionReference: 'SOURCE_CONFIRMED_SEMANTIC' as Resolution,
  pendingLimitExecution: 'SOURCE_CONFIRMED' as Resolution,
  exactEntryCandleIndex: 'UNRESOLVED' as Resolution,
  entryEqualsPGAPBoundary: 'REJECTED' as Resolution,
  entryEqualsClassicalC: 'REJECTED' as Resolution,
  entryEquals50PercentRetracement: 'REJECTED_AS_CANONICAL' as Resolution,
  slSpikeOriginSemantic: 'SOURCE_CONFIRMED_SEMANTIC' as Resolution,
  exactSLPriceConvention: 'UNRESOLVED' as Resolution,
  numericSLBuffer: 'UNRESOLVED' as Resolution,
  equalLegSemantic: 'SOURCE_CONFIRMED_SEMANTIC' as Resolution,
  exactLeg1OHLCAnchors: 'UNRESOLVED' as Resolution,
  classicalFibonacciABCMapping: 'REJECTED_AS_CANONICAL' as Resolution,
  abEqualCdTolerance: 'UNRESOLVED' as Resolution,
  baseTP: 'SOURCE_CONFIRMED' as Resolution,
};

describe('SP2L final source artifact search', () => {
  it('preserves source-confirmed semantics', () => {
    expect(finalResolution.pGapRequiredForValidSpike).toBe('SOURCE_CONFIRMED');
    expect(finalResolution.pendingLimitExecution).toBe('SOURCE_CONFIRMED');
    expect(finalResolution.equalLegSemantic).toBe('SOURCE_CONFIRMED_SEMANTIC');
    expect(finalResolution.baseTP).toBe('SOURCE_CONFIRMED');
  });

  it('does not promote unresolved executable geometry', () => {
    expect(finalResolution.pGapExactBoundary).toBe('UNRESOLVED');
    expect(finalResolution.pGapExactTiming).toBe('UNRESOLVED');
    expect(finalResolution.exactEntryCandleIndex).toBe('UNRESOLVED');
    expect(finalResolution.exactSLPriceConvention).toBe('UNRESOLVED');
    expect(finalResolution.numericSLBuffer).toBe('UNRESOLVED');
    expect(finalResolution.exactLeg1OHLCAnchors).toBe('UNRESOLVED');
    expect(finalResolution.abEqualCdTolerance).toBe('UNRESOLVED');
  });

  it('rejects unsupported substitutions as canonical rules', () => {
    expect(finalResolution.genericFvgEqualsPGAP).toBe('REJECTED_AS_CANONICAL');
    expect(finalResolution.entryEqualsPGAPBoundary).toBe('REJECTED');
    expect(finalResolution.entryEqualsClassicalC).toBe('REJECTED');
    expect(finalResolution.entryEquals50PercentRetracement).toBe('REJECTED_AS_CANONICAL');
    expect(finalResolution.classicalFibonacciABCMapping).toBe('REJECTED_AS_CANONICAL');
  });
});
