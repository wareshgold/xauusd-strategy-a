import { describe, expect, it } from 'vitest';
import {
  G355_FIXTURES,
  g355AllFixturesRemainNonCanonical,
  g355GenericGapEvidenceIsNotPgapPromotion,
  g355HasBothSourceSupportedTimingVariants,
  g355KeepsTaxonomySeparated,
} from '../src/domain/research/sp2l-v2/G355PgapSyntheticDiscrimination.js';

describe('G355 P-Gap synthetic discrimination', () => {
  it('contains the full source-disciplined fixture matrix', () => {
    expect(G355_FIXTURES).toHaveLength(14);
    expect(new Set(G355_FIXTURES.map((fixture) => fixture.family)).size).toBe(8);
  });

  it('keeps every fixture explicitly non-canonical', () => {
    expect(g355AllFixturesRemainNonCanonical()).toBe(true);
  });

  it('does not promote generic gap geometry into P-GAP', () => {
    const genericGap = G355_FIXTURES.find((fixture) => fixture.id === 'PG-01');
    expect(genericGap).toBeDefined();
    expect(g355GenericGapEvidenceIsNotPgapPromotion(genericGap!)).toBe(true);
  });

  it('represents both source-described SP2L P-GAP timing variants', () => {
    expect(g355HasBothSourceSupportedTimingVariants()).toBe(true);
  });

  it('keeps Breakout Gap and Pressure Gap as distinct research classifications', () => {
    expect(g355KeepsTaxonomySeparated()).toBe(true);
  });

  it('keeps unresolved endpoint/threshold/tolerance/anchor questions represented', () => {
    expect(G355_FIXTURES.some((fixture) => fixture.id === 'PG-07')).toBe(true);
    expect(G355_FIXTURES.some((fixture) => fixture.id === 'PG-08')).toBe(true);
    expect(G355_FIXTURES.some((fixture) => fixture.id === 'PG-09')).toBe(true);
    expect(G355_FIXTURES.some((fixture) => fixture.id === 'PG-10')).toBe(true);
    expect(G355_FIXTURES.some((fixture) => fixture.id === 'PG-14')).toBe(true);
  });
});
