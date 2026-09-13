import { describe, expect, it } from 'vitest';
import { G381_DIMENSIONS, g381AllNonCanonical, g381GateDecision, g381HasSourceConflict, g381HasSourceUnderDetermination } from '../../src/domain/research/sp2l-v2/G381DiscriminationConsolidation.js';

describe('G381 discrimination consolidation', () => {
  it('covers the nine consolidated unresolved dimensions', () => {
    expect(G381_DIMENSIONS).toHaveLength(9);
  });

  it('preserves non-canonical status', () => {
    expect(g381AllNonCanonical()).toBe(true);
  });

  it('retains both underdetermination and source conflict', () => {
    expect(g381HasSourceUnderDetermination()).toBe(true);
    expect(g381HasSourceConflict()).toBe(true);
  });

  it('keeps the frozen-geometry gate blocked', () => {
    expect(g381GateDecision()).toBe('FROZEN-GEOMETRY-BLOCKED');
  });
});
