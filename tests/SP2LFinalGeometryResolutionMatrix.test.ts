import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'STRONGEST_CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const resolution = {
  entryDirection: 'SOURCE_CONFIRMED' as Resolution,
  entryPriorExtremeSemantic: 'SOURCE_CONFIRMED' as Resolution,
  entryRelevantCandleIdentity: 'UNRESOLVED' as Resolution,
  pendingLimitExecution: 'SOURCE_CONFIRMED' as Resolution,
  pGapSemantic: 'SOURCE_CONFIRMED' as Resolution,
  pGapExactBoundary: 'UNRESOLVED' as Resolution,
  pGapExactTiming: 'UNRESOLVED' as Resolution,
  pGapGenericFVG: 'REJECTED' as Resolution,
  slOriginSemantic: 'SOURCE_CONFIRMED' as Resolution,
  slExactExecutablePrice: 'UNRESOLVED' as Resolution,
  leg1EqualLegSemantic: 'SOURCE_CONFIRMED' as Resolution,
  leg1ExactOHLCAnchor: 'UNRESOLVED' as Resolution,
  classicalABCDAnchors: 'REJECTED' as Resolution,
  abEqualCdTolerance: 'UNRESOLVED' as Resolution,
  targetModuleRelation: 'UNRESOLVED' as Resolution,
};

describe('SP2L final geometry resolution matrix guardrails', () => {
  it('freezes only the safe Entry semantics', () => {
    expect(resolution.entryDirection).toBe('SOURCE_CONFIRMED');
    expect(resolution.entryPriorExtremeSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.entryRelevantCandleIdentity).toBe('UNRESOLVED');
    expect(resolution.pendingLimitExecution).toBe('SOURCE_CONFIRMED');
  });

  it('keeps P-Gap semantic separate from exact geometry and rejects generic FVG import', () => {
    expect(resolution.pGapSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.pGapExactBoundary).toBe('UNRESOLVED');
    expect(resolution.pGapExactTiming).toBe('UNRESOLVED');
    expect(resolution.pGapGenericFVG).toBe('REJECTED');
  });

  it('freezes only the structural SL meaning', () => {
    expect(resolution.slOriginSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.slExactExecutablePrice).toBe('UNRESOLVED');
  });

  it('preserves equal-leg meaning without inventing OHLC anchors or tolerance', () => {
    expect(resolution.leg1EqualLegSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.leg1ExactOHLCAnchor).toBe('UNRESOLVED');
    expect(resolution.classicalABCDAnchors).toBe('REJECTED');
    expect(resolution.abEqualCdTolerance).toBe('UNRESOLVED');
  });

  it('keeps target-module relation unresolved', () => {
    expect(resolution.targetModuleRelation).toBe('UNRESOLVED');
  });

  it('cannot unlock Frozen Geometry while primary blockers remain unresolved', () => {
    const frozenGeometry =
      resolution.pGapExactBoundary === 'SOURCE_CONFIRMED' &&
      resolution.pGapExactTiming === 'SOURCE_CONFIRMED' &&
      resolution.entryRelevantCandleIdentity === 'SOURCE_CONFIRMED' &&
      resolution.slExactExecutablePrice === 'SOURCE_CONFIRMED' &&
      resolution.leg1ExactOHLCAnchor === 'SOURCE_CONFIRMED' &&
      resolution.abEqualCdTolerance === 'SOURCE_CONFIRMED';

    expect(frozenGeometry).toBe(false);
  });
});
