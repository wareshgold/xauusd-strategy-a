import { describe, expect, it } from 'vitest';

type Status = 'SOURCE_SUPPORTED' | 'STRONG_CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const jointResolution: Record<string, Status> = {
  pGapCommonExecutableAnchor: 'UNRESOLVED',
  pGapExactBoundary: 'UNRESOLVED',
  entryPendingLimitDuringCorrection: 'SOURCE_SUPPORTED',
  entryPriorCandleExtreme: 'STRONG_CANDIDATE',
  entryEqualsPGAPBoundary: 'UNRESOLVED',
  slSpikeOriginCandle: 'SOURCE_SUPPORTED',
  slExactPriceConvention: 'UNRESOLVED',
  genericThreeCandlePGAP: 'REJECTED',
  classicalHarmonicCAsEntry: 'REJECTED',
};

describe('SP2L joint P-Gap / Entry / SL source guardrails', () => {
  it('does not invent a common executable anchor across P-Gap, Entry, and SL', () => {
    expect(jointResolution.pGapCommonExecutableAnchor).toBe('UNRESOLVED');
    expect(jointResolution.entryEqualsPGAPBoundary).toBe('UNRESOLVED');
  });

  it('keeps pending-limit and Spike-origin SL semantics source-supported', () => {
    expect(jointResolution.entryPendingLimitDuringCorrection).toBe('SOURCE_SUPPORTED');
    expect(jointResolution.slSpikeOriginCandle).toBe('SOURCE_SUPPORTED');
  });

  it('keeps prior-candle extreme as a candidate, not a frozen executable price', () => {
    expect(jointResolution.entryPriorCandleExtreme).toBe('STRONG_CANDIDATE');
  });

  it('keeps exact P-Gap and exact SL price conventions unresolved', () => {
    expect(jointResolution.pGapExactBoundary).toBe('UNRESOLVED');
    expect(jointResolution.slExactPriceConvention).toBe('UNRESOLVED');
  });

  it('rejects external P-Gap and classical C-point imports', () => {
    expect(jointResolution.genericThreeCandlePGAP).toBe('REJECTED');
    expect(jointResolution.classicalHarmonicCAsEntry).toBe('REJECTED');
  });
});
