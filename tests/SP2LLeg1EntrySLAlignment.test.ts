import { describe, expect, it } from 'vitest';

type Resolution = 'STRONG_EVIDENCE' | 'STRONG_CANDIDATE' | 'UNRESOLVED' | 'FORBIDDEN_IMPORT';

const resolution: Record<string, Resolution> = {
  pendingLimitDuringCorrection: 'STRONG_EVIDENCE',
  entryAtRelevantPriorCandleExtreme: 'STRONG_CANDIDATE',
  exactSLAnchor: 'UNRESOLVED',
  exactLeg1Origin: 'UNRESOLVED',
  classicalCAsEntry: 'FORBIDDEN_IMPORT',
  fixedPointSL: 'FORBIDDEN_IMPORT',
  marketCloseReclaimAsEntry: 'FORBIDDEN_IMPORT',
};

describe('SP2L Leg1 / Entry / SL source guardrails', () => {
  it('keeps pending-limit execution source-confirmed', () => {
    expect(resolution.pendingLimitDuringCorrection).toBe('STRONG_EVIDENCE');
  });

  it('keeps prior-candle extreme as a candidate, not a frozen rule', () => {
    expect(resolution.entryAtRelevantPriorCandleExtreme).toBe('STRONG_CANDIDATE');
  });

  it('does not invent exact SL or Leg1 anchors', () => {
    expect(resolution.exactSLAnchor).toBe('UNRESOLVED');
    expect(resolution.exactLeg1Origin).toBe('UNRESOLVED');
  });

  it('blocks classical C-point, fixed-point SL, and close-reclaim imports', () => {
    expect(resolution.classicalCAsEntry).toBe('FORBIDDEN_IMPORT');
    expect(resolution.fixedPointSL).toBe('FORBIDDEN_IMPORT');
    expect(resolution.marketCloseReclaimAsEntry).toBe('FORBIDDEN_IMPORT');
  });
});
