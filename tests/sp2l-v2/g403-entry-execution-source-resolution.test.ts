import { describe, expect, it } from 'vitest';
import {
  G403_ENTRY_HYPOTHESES,
  G403_MINIMAL_PAIRS,
  G403_STATUS,
  g403AllHypothesesRemainNonCanonical,
  g403DoesNotInventExecutableEntryGeometry
} from '../../src/domain/research/sp2l-v2/G403EntryExecutionSourceResolution.js';

describe('G403 pending-limit entry execution source resolution', () => {
  it('keeps every entry interpretation non-canonical', () => {
    expect(g403AllHypothesesRemainNonCanonical()).toBe(true);
    expect(G403_ENTRY_HYPOTHESES.every((item) => item.canonical === false)).toBe(true);
  });

  it('does not invent executable entry geometry or fill semantics', () => {
    expect(g403DoesNotInventExecutableEntryGeometry()).toBe(true);
    expect(G403_STATUS.canonicalEntryPrice).toBeNull();
    expect(G403_STATUS.canonicalTrigger).toBeNull();
    expect(G403_STATUS.canonicalPersistenceRule).toBeNull();
    expect(G403_STATUS.canonicalFillSemantics).toBeNull();
    expect(G403_STATUS.canonicalPreFillInvalidation).toBeNull();
  });

  it('enumerates the five source-discrimination minimal pairs', () => {
    expect(G403_MINIMAL_PAIRS.map((pair) => pair.id)).toEqual([
      'ENTRY-MP-01', 'ENTRY-MP-02', 'ENTRY-MP-03', 'ENTRY-MP-04', 'ENTRY-MP-05'
    ]);
  });

  it('explicitly keeps geometric C versus executable fill price unresolved', () => {
    const pair = G403_MINIMAL_PAIRS.find((item) => item.id === 'ENTRY-MP-01');
    expect(pair?.expectedResearchQuestion).toContain('limit price with C');
    expect(G403_STATUS.status).toBe('UNRESOLVED');
  });
});
