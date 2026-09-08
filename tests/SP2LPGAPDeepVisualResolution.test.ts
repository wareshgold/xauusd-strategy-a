import { describe, expect, it } from 'vitest';

type Status = 'SOURCE_SUPPORTED' | 'STRONG_CANDIDATE' | 'UNRESOLVED' | 'REJECTED_AS_CANONICAL';

const resolution: Record<string, Status> = {
  breakoutAssociatedNonOverlap: 'SOURCE_SUPPORTED',
  wickRangeCandidate: 'STRONG_CANDIDATE',
  bodyRange: 'UNRESOLVED',
  mixedBoundary: 'UNRESOLVED',
  exactCandlePair: 'UNRESOLVED',
  exactTiming: 'UNRESOLVED',
  equalityTouch: 'UNRESOLVED',
  minimumGap: 'UNRESOLVED',
  genericThreeCandleImbalance: 'REJECTED_AS_CANONICAL',
  gapEqualsEntry: 'UNRESOLVED',
};

describe('SP2L P-Gap deep visual resolution guardrails', () => {
  it('locks only the source-supported breakout-associated non-overlap semantic', () => {
    expect(resolution.breakoutAssociatedNonOverlap).toBe('SOURCE_SUPPORTED');
  });

  it('keeps wick-range as a candidate rather than silently freezing it', () => {
    expect(resolution.wickRangeCandidate).toBe('STRONG_CANDIDATE');
  });

  it('keeps body/mixed geometry unresolved', () => {
    expect(resolution.bodyRange).toBe('UNRESOLVED');
    expect(resolution.mixedBoundary).toBe('UNRESOLVED');
  });

  it('does not invent timing, pair, equality, or size rules', () => {
    expect(resolution.exactCandlePair).toBe('UNRESOLVED');
    expect(resolution.exactTiming).toBe('UNRESOLVED');
    expect(resolution.equalityTouch).toBe('UNRESOLVED');
    expect(resolution.minimumGap).toBe('UNRESOLVED');
  });

  it('rejects importing generic three-candle imbalance as canonical P-Gap', () => {
    expect(resolution.genericThreeCandleImbalance).toBe('REJECTED_AS_CANONICAL');
  });

  it('does not collapse P-Gap boundary into Entry', () => {
    expect(resolution.gapEqualsEntry).toBe('UNRESOLVED');
  });
});
