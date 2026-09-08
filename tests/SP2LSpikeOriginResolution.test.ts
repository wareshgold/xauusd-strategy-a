import { describe, expect, it } from 'vitest';

type Resolution = 'STRONG_SEMANTIC' | 'CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const resolution: Record<string, Resolution> = {
  originRelativeToSpikeSequence: 'STRONG_SEMANTIC',
  fixedAbsoluteCandleIndex: 'REJECTED',
  gapCandleEqualsOrigin: 'REJECTED',
  exactSlPrice: 'UNRESOLVED',
  wickVsBodyForSl: 'UNRESOLVED',
  numericBuffer: 'UNRESOLVED',
  classicalAbcdOriginMapping: 'UNRESOLVED',
};

describe('SP2L spike-origin source-resolution guardrails', () => {
  it('keeps origin identity relative to the source-defined Spike sequence', () => {
    expect(resolution.originRelativeToSpikeSequence).toBe('STRONG_SEMANTIC');
  });

  it('does not freeze a universal candle number as Spike origin', () => {
    expect(resolution.fixedAbsoluteCandleIndex).toBe('REJECTED');
  });

  it('does not equate P-Gap timing with Spike-origin identity', () => {
    expect(resolution.gapCandleEqualsOrigin).toBe('REJECTED');
  });

  it('keeps exact SL geometry unresolved', () => {
    expect(resolution.exactSlPrice).toBe('UNRESOLVED');
    expect(resolution.wickVsBodyForSl).toBe('UNRESOLVED');
    expect(resolution.numericBuffer).toBe('UNRESOLVED');
  });

  it('does not import classical AB=CD anchor mapping', () => {
    expect(resolution.classicalAbcdOriginMapping).toBe('UNRESOLVED');
  });
});
