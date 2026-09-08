import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'STRONGEST_CANDIDATE' | 'UNRESOLVED' | 'REJECTED';

const resolution = {
  entryPriorExtremeSemantic: 'SOURCE_CONFIRMED' as Resolution,
  immediatePreviousCandleUniversal: 'STRONGEST_CANDIDATE' as Resolution,
  universalEntryIndex: 'UNRESOLVED' as Resolution,
  pendingLimit: 'SOURCE_CONFIRMED' as Resolution,
  pGapBreakoutAssociated: 'SOURCE_CONFIRMED' as Resolution,
  pGapWickNonOverlap: 'STRONGEST_CANDIDATE' as Resolution,
  pGapExactOHLCBoundary: 'UNRESOLVED' as Resolution,
  pGapExactTiming: 'UNRESOLVED' as Resolution,
  pGapEqualsEntry: 'REJECTED' as Resolution,
  genericFVGCanonical: 'REJECTED' as Resolution,
  slOriginSemantic: 'SOURCE_CONFIRMED' as Resolution,
  slExecutablePrice: 'UNRESOLVED' as Resolution,
};

describe('SP2L Entry / P-Gap joint source-resolution guardrails', () => {
  it('preserves prior-extreme entry semantics', () => {
    expect(resolution.entryPriorExtremeSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.pendingLimit).toBe('SOURCE_CONFIRMED');
  });

  it('does not promote immediate previous candle to a universal index', () => {
    expect(resolution.immediatePreviousCandleUniversal).toBe('STRONGEST_CANDIDATE');
    expect(resolution.universalEntryIndex).toBe('UNRESOLVED');
  });

  it('keeps P-Gap as a breakout-associated condition', () => {
    expect(resolution.pGapBreakoutAssociated).toBe('SOURCE_CONFIRMED');
    expect(resolution.pGapWickNonOverlap).toBe('STRONGEST_CANDIDATE');
  });

  it('keeps exact P-Gap geometry and timing unresolved', () => {
    expect(resolution.pGapExactOHLCBoundary).toBe('UNRESOLVED');
    expect(resolution.pGapExactTiming).toBe('UNRESOLVED');
  });

  it('forbids collapsing P-Gap into Entry or generic FVG', () => {
    expect(resolution.pGapEqualsEntry).toBe('REJECTED');
    expect(resolution.genericFVGCanonical).toBe('REJECTED');
  });

  it('preserves structural SL semantics without inventing price', () => {
    expect(resolution.slOriginSemantic).toBe('SOURCE_CONFIRMED');
    expect(resolution.slExecutablePrice).toBe('UNRESOLVED');
  });
});
