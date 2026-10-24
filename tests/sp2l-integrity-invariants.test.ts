import { describe, expect, it } from 'vitest';
import {
  assert125RPreserved,
  assertNoCanonicalPromotionFromPerformance,
  assertNoTradingDecisionSurface,
} from '../research/harness/sp2l_integrity_invariants_v1.js';

describe('SP2L integrity invariants', () => {
  it('accepts research-only objects without trading decision fields', () => {
    expect(assertNoTradingDecisionSurface({ fixtureId: 'F01', status: 'BLOCKED' }).ok).toBe(true);
  });

  it('fails closed on trading decision fields', () => {
    const result = assertNoTradingDecisionSurface({ fixtureId: 'F01', signal: 'BUY' });
    expect(result.ok).toBe(false);
  });

  it('blocks performance-based promotion of unresolved geometry', () => {
    const result = assertNoCanonicalPromotionFromPerformance({
      provenanceConfirmed: false,
      performanceUsedForPromotion: true,
    });
    expect(result.ok).toBe(false);
  });

  it('allows performance metrics after provenance is confirmed', () => {
    const result = assertNoCanonicalPromotionFromPerformance({
      provenanceConfirmed: true,
      performanceUsedForPromotion: true,
    });
    expect(result.ok).toBe(true);
  });

  it('preserves the 125R observation exactly', () => {
    const result = assert125RPreserved({
      originalR: 125,
      currentR: 125,
      originalClassification: 'UNTOUCHED',
      currentClassification: 'UNTOUCHED',
    });
    expect(result.ok).toBe(true);
  });

  it('fails if the 125R observation is changed', () => {
    const result = assert125RPreserved({
      originalR: 125,
      currentR: 124,
      originalClassification: 'UNTOUCHED',
      currentClassification: 'UNTOUCHED',
    });
    expect(result.ok).toBe(false);
  });
});
