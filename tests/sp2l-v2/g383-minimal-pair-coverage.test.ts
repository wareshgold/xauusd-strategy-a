import { describe, expect, it } from 'vitest';
import { G383_PAIRS, g383AllNonCanonical, g383AllPairsStable, g383DimensionsCovered, g383GateDecision } from '../../src/domain/research/sp2l-v2/G383MinimalPairCoverage.js';

describe('G383 minimal-pair state perturbation coverage', () => {
  it('contains twelve controlled one-transition perturbations', () => {
    expect(G383_PAIRS).toHaveLength(12);
  });
  it('covers every required unresolved state dimension', () => {
    expect(g383DimensionsCovered()).toBe(true);
  });
  it('keeps expected classifications deterministic', () => {
    expect(g383AllPairsStable()).toBe(true);
  });
  it('preserves non-canonical status', () => {
    expect(g383AllNonCanonical()).toBe(true);
  });
  it('keeps the frozen-geometry gate blocked', () => {
    expect(g383GateDecision()).toBe('FROZEN-GEOMETRY-BLOCKED');
  });
});
