import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'STRONGEST_CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const resolution = {
  entryPriorExtremeSemantic: 'SOURCE_CONFIRMED' as Resolution,
  immediatePreviousCandleAsUniversalRule: 'STRONGEST_CANDIDATE' as Resolution,
  firstCorrectionCandleAsUniversalRule: 'UNRESOLVED' as Resolution,
  pGapEqualsEntry: 'REJECTED' as Resolution,
  pGapExactBoundary: 'UNRESOLVED' as Resolution,
  slBeyondSpikeOriginSemantic: 'SOURCE_CONFIRMED' as Resolution,
  slOriginWickPrice: 'STRONGEST_CANDIDATE' as Resolution,
  slExactExecutablePrice: 'UNRESOLVED' as Resolution,
  leg1OriginToExtreme: 'STRONGEST_CANDIDATE' as Resolution,
  leg1ExactOHLCAnchor: 'UNRESOLVED' as Resolution,
  classicalABCDAnchors: 'REJECTED' as Resolution,
  abEqualCdTolerance: 'UNRESOLVED' as Resolution,
  genericFVGAsCanonicalPGAP: 'REJECTED' as Resolution,
};

describe('SP2L multi-stage source resolution guardrails', () => {
  it('preserves the source-confirmed prior-extreme entry semantic', () => {
    expect(resolution.entryPriorExtremeSemantic).toBe('SOURCE_CONFIRMED');
  });

  it('does not freeze a universal entry candle index', () => {
    expect(resolution.immediatePreviousCandleAsUniversalRule).toBe('STRONGEST_CANDIDATE');
    expect(resolution.firstCorrectionCandleAsUniversalRule).toBe('UNRESOLVED');
  });

  it('keeps P-Gap separate from Entry', () => {
    expect(resolution.pGapEqualsEntry).toBe('REJECTED');
    expect(resolution.pGapExactBoundary).toBe('UNRESOLVED');
  });

  it('preserves structural SL semantics without inventing an executable price', () => {
    expect(resolution.slBeyondSpikeOriginSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.slOriginWickPrice).toBe('STRONGEST_CANDIDATE');
    expect(resolution.slExactExecutablePrice).toBe('UNRESOLVED');
  });

  it('keeps Leg-1 geometry unresolved at exact OHLC level', () => {
    expect(resolution.leg1OriginToExtreme).toBe('STRONGEST_CANDIDATE');
    expect(resolution.leg1ExactOHLCAnchor).toBe('UNRESOLVED');
  });

  it('forbids classical harmonic anchor import and invented AB=CD tolerance', () => {
    expect(resolution.classicalABCDAnchors).toBe('REJECTED');
    expect(resolution.abEqualCdTolerance).toBe('UNRESOLVED');
  });

  it('does not promote generic FVG into canonical P-Gap', () => {
    expect(resolution.genericFVGAsCanonicalPGAP).toBe('REJECTED');
  });
});
