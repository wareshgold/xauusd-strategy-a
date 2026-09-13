import { describe, expect, it } from 'vitest';
import { G376_FIXTURES, g376AllNonCanonical, runG376 } from '../src/domain/research/sp2l-v2/G376HypothesisFixtureRunner.js';

describe('G376 machine-executable hypothesis fixture runner', () => {
  it('contains all 16 G369 minimal-pair fixtures', () => {
    expect(G376_FIXTURES).toHaveLength(16);
    expect(new Set(G376_FIXTURES.map((fixture) => fixture.family))).toEqual(new Set(['PGAP','ABCD','ENTRY','SL','TP']));
  });

  it('preserves non-canonical status', () => {
    expect(g376AllNonCanonical()).toBe(true);
  });

  it('returns deterministic, declared classifications', () => {
    const first = runG376();
    const second = runG376();
    expect(first).toEqual(second);
    expect(first.every((fixture) => ['DISTINCT','EQUIVALENT','SOURCE-CONFLICT','UNDERDETERMINED'].includes(fixture.expected))).toBe(true);
  });

  it('keeps source-conflict and underdetermined cases explicit', () => {
    expect(G376_FIXTURES.some((fixture) => fixture.expected === 'SOURCE-CONFLICT')).toBe(true);
    expect(G376_FIXTURES.some((fixture) => fixture.expected === 'UNDERDETERMINED')).toBe(true);
  });
});
