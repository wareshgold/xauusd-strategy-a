import { describe, expect, it } from 'vitest';

type Resolution =
  | 'SOURCE_CONFIRMED_SEMANTIC'
  | 'STRONG_CANDIDATE'
  | 'UNRESOLVED'
  | 'FORBIDDEN_IMPORT';

const resolution: Record<string, Resolution> = {
  bullishCorrectionReference: 'SOURCE_CONFIRMED_SEMANTIC',
  bearishCorrectionReference: 'SOURCE_CONFIRMED_SEMANTIC',
  pendingLimitExecution: 'SOURCE_CONFIRMED_SEMANTIC',
  exactEntryBuffer: 'UNRESOLVED',
  exactRelevantPreviousCandleAcrossVariants: 'UNRESOLVED',
  slReferencesSpikeOriginCandle: 'SOURCE_CONFIRMED_SEMANTIC',
  exactSLPriceConvention: 'UNRESOLVED',
  leg1Origin: 'UNRESOLVED',
  classicalCPointEntry: 'FORBIDDEN_IMPORT',
  closeReclaimEntry: 'FORBIDDEN_IMPORT',
  fixedPointSL: 'FORBIDDEN_IMPORT',
};

describe('SP2L source-resolution entry / SL semantics', () => {
  it('locks the source-confirmed correction references', () => {
    expect(resolution.bullishCorrectionReference).toBe('SOURCE_CONFIRMED_SEMANTIC');
    expect(resolution.bearishCorrectionReference).toBe('SOURCE_CONFIRMED_SEMANTIC');
  });

  it('locks pending-limit execution semantics without inventing a price buffer', () => {
    expect(resolution.pendingLimitExecution).toBe('SOURCE_CONFIRMED_SEMANTIC');
    expect(resolution.exactEntryBuffer).toBe('UNRESOLVED');
    expect(resolution.exactRelevantPreviousCandleAcrossVariants).toBe('UNRESOLVED');
  });

  it('locks SL to the spike-origin candle semantically while keeping exact price unresolved', () => {
    expect(resolution.slReferencesSpikeOriginCandle).toBe('SOURCE_CONFIRMED_SEMANTIC');
    expect(resolution.exactSLPriceConvention).toBe('UNRESOLVED');
  });

  it('keeps Leg-1 geometry unresolved', () => {
    expect(resolution.leg1Origin).toBe('UNRESOLVED');
  });

  it('blocks non-source imports', () => {
    expect(resolution.classicalCPointEntry).toBe('FORBIDDEN_IMPORT');
    expect(resolution.closeReclaimEntry).toBe('FORBIDDEN_IMPORT');
    expect(resolution.fixedPointSL).toBe('FORBIDDEN_IMPORT');
  });
});
