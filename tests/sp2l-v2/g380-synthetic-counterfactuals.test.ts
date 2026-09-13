import { describe, expect, it } from 'vitest';
import { G380_FIXTURES, g380AllNonCanonical, g380ExpectedClassificationsMatch, runG380 } from '../../src/domain/research/sp2l-v2/G380SyntheticCounterfactuals.js';

describe('G380 synthetic counterfactual executor', () => {
  it('executes the complete fixture matrix', () => {
    expect(runG380()).toHaveLength(G380_FIXTURES.length);
    expect(G380_FIXTURES).toHaveLength(10);
  });

  it('matches the predeclared discrimination expectations', () => {
    expect(g380ExpectedClassificationsMatch()).toBe(true);
  });

  it('keeps fixtures and observations non-canonical', () => {
    expect(g380AllNonCanonical()).toBe(true);
  });

  it('produces both equivalent and distinct counterfactual outcomes', () => {
    const results = runG380();
    expect(results.some((r) => r.classification === 'DISTINCT')).toBe(true);
    expect(results.some((r) => r.classification === 'EQUIVALENT')).toBe(true);
  });
});
