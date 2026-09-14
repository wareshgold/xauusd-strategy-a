import { describe, expect, it } from 'vitest';
import {
  G401_MINIMAL_PAIRS,
  G401_PGAP_HYPOTHESES,
  G401_STATUS,
  g401AllHypothesesRemainNonCanonical,
  g401DoesNotInventExecutableGeometry
} from '../../src/domain/research/sp2l-v2/G401PgapSourceResolution.js';

describe('G401 P-Gap source resolution', () => {
  it('keeps every P-Gap interpretation explicitly non-canonical', () => {
    expect(g401AllHypothesesRemainNonCanonical()).toBe(true);
    expect(G401_PGAP_HYPOTHESES.length).toBeGreaterThanOrEqual(4);
  });

  it('does not invent an executable P-Gap formula, threshold, or tolerance', () => {
    expect(g401DoesNotInventExecutableGeometry()).toBe(true);
    expect(G401_STATUS.status).toBe('UNRESOLVED');
  });

  it('covers the highest-information P-Gap minimal-pair dimensions', () => {
    expect(G401_MINIMAL_PAIRS.map((x) => x.id)).toEqual([
      'PG-MP-01',
      'PG-MP-02',
      'PG-MP-03',
      'PG-MP-04',
      'PG-MP-05'
    ]);
    expect(new Set(G401_MINIMAL_PAIRS.map((x) => x.changedDimension)).size).toBe(5);
  });

  it('treats generic gap evidence as a research discriminator, not P-Gap promotion', () => {
    const generic = G401_PGAP_HYPOTHESES.find((x) => x.id === 'PGAP-H1');
    expect(generic?.canonical).toBe(false);
    expect(generic?.discriminatedBy).toContain('source');
  });
});
