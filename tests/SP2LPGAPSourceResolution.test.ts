import { describe, expect, it } from 'vitest';

type Status = 'SOURCE_SUPPORTED_VARIANT' | 'CANDIDATE' | 'UNRESOLVED' | 'REJECTED_AS_CANONICAL';

const pGapResolution: Record<string, Status> = {
  breakoutAssociatedGap: 'CANDIDATE',
  multipleTemporalVariants: 'SOURCE_SUPPORTED_VARIANT',
  exactBoundary: 'UNRESOLVED',
  wickVsBody: 'UNRESOLVED',
  equalityTouch: 'UNRESOLVED',
  minimumGapSize: 'UNRESOLVED',
  genericThreeCandleImbalance: 'REJECTED_AS_CANONICAL',
};

describe('SP2L P-Gap source-resolution guardrails', () => {
  it('preserves the source-supported temporal variants', () => {
    expect(pGapResolution.multipleTemporalVariants).toBe('SOURCE_SUPPORTED_VARIANT');
  });

  it('does not freeze an exact P-Gap formula without source evidence', () => {
    expect(pGapResolution.exactBoundary).toBe('UNRESOLVED');
    expect(pGapResolution.wickVsBody).toBe('UNRESOLVED');
    expect(pGapResolution.equalityTouch).toBe('UNRESOLVED');
    expect(pGapResolution.minimumGapSize).toBe('UNRESOLVED');
  });

  it('rejects importing a generic three-candle imbalance as canonical P-Gap', () => {
    expect(pGapResolution.genericThreeCandleImbalance).toBe('REJECTED_AS_CANONICAL');
  });

  it('keeps breakout association distinct from a standalone gap detector', () => {
    expect(pGapResolution.breakoutAssociatedGap).toBe('CANDIDATE');
  });
});
