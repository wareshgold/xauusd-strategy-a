import { describe, expect, it } from 'vitest';
import { SP2L_SEMANTIC_FIXTURES } from './fixtures/SP2LSemanticContract.fixtures';

describe('SP2L frozen semantic contract', () => {
  it('contains both directional canonical examples', () => {
    expect(SP2L_SEMANTIC_FIXTURES.map((f) => f.id)).toEqual(
      expect.arrayContaining(['SEM-BULL-VALID', 'SEM-BEAR-VALID']),
    );
  });

  it('requires source-defined P-Gap for a canonical Spike', () => {
    const noGap = SP2L_SEMANTIC_FIXTURES.find((f) => f.id === 'SEM-NO-PGAP');
    expect(noGap).toBeDefined();
    expect(noGap?.sharpDirectionalMovement).toBe(true);
    expect(noGap?.validPGAPresent).toBe(false);

    const valid = SP2L_SEMANTIC_FIXTURES.find((f) => f.id === 'SEM-BULL-VALID');
    expect(valid?.validPGAPresent).toBe(true);
  });

  it('requires pending-limit semantics for the canonical base entry', () => {
    const marketReclaimOnly = SP2L_SEMANTIC_FIXTURES.find(
      (f) => f.id === 'SEM-MARKET-RECLAIM-ONLY',
    );
    expect(marketReclaimOnly?.pendingLimitPrepared).toBe(false);

    const valid = SP2L_SEMANTIC_FIXTURES.find((f) => f.id === 'SEM-BULL-VALID');
    expect(valid?.pendingLimitPrepared).toBe(true);
  });

  it('keeps the base target at source-confirmed 1:1', () => {
    for (const fixture of SP2L_SEMANTIC_FIXTURES) {
      expect(fixture.expectedBaseTargetR).toBe(1);
    }
  });

  it('requires correction, structural invalidation, and equal-leg semantics for valid examples', () => {
    for (const id of ['SEM-BULL-VALID', 'SEM-BEAR-VALID']) {
      const fixture = SP2L_SEMANTIC_FIXTURES.find((f) => f.id === id);
      expect(fixture).toBeDefined();
      expect(fixture?.correctionReachesReference).toBe(true);
      expect(fixture?.structuralInvalidationDefined).toBe(true);
      expect(fixture?.leg2MatchesLeg1Semantically).toBe(true);
    }
  });

  it('does not encode unresolved executable geometry', () => {
    for (const fixture of SP2L_SEMANTIC_FIXTURES) {
      expect('entryPrice' in fixture).toBe(false);
      expect('stopPrice' in fixture).toBe(false);
      expect('pgapStartPrice' in fixture).toBe(false);
      expect('pgapEndPrice' in fixture).toBe(false);
      expect('abCdTolerance' in fixture).toBe(false);
    }
  });
});
