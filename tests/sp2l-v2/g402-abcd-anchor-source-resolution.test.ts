import { describe, expect, it } from 'vitest';
import {
  G402_HYPOTHESES,
  G402_MINIMAL_PAIRS,
  G402_STATUS,
  g402AllHypothesesRemainNonCanonical,
  g402DoesNotInventExecutableGeometry
} from '../../src/domain/research/sp2l-v2/G402AbcdAnchorSourceResolution.js';

describe('G402 AB=CD anchor source resolution', () => {
  it('keeps every competing anchor interpretation non-canonical', () => {
    expect(g402AllHypothesesRemainNonCanonical()).toBe(true);
    expect(G402_HYPOTHESES.every((hypothesis) => hypothesis.canonical === false)).toBe(true);
  });

  it('preserves the source-confirmed AB=CD relationship without freezing geometry', () => {
    expect(G402_STATUS.relationship).toBe('SOURCE-CONFIRMED');
    expect(G402_STATUS.status).toBe('UNRESOLVED');
    expect(g402DoesNotInventExecutableGeometry()).toBe(true);
  });

  it('keeps the seven discriminating dimensions explicit', () => {
    expect(new Set(G402_HYPOTHESES.map((hypothesis) => hypothesis.dimension))).toEqual(
      new Set(['A_ANCHOR', 'B_ANCHOR', 'C_ANCHOR', 'D_ANCHOR', 'PRICE_FIELD', 'WICK_BODY_SEMANTICS', 'ABCD_TOLERANCE'])
    );
  });

  it('defines minimal-pair research without promoting a winner', () => {
    expect(G402_MINIMAL_PAIRS).toHaveLength(7);
    expect(G402_MINIMAL_PAIRS.every((pair) => pair.startsWith('ABCD-MP-'))).toBe(true);
  });

  it('does not treat pending-order fill as geometric C', () => {
    const fillHypothesis = G402_HYPOTHESES.find((hypothesis) => hypothesis.id === 'ABCD-C-H2');
    expect(fillHypothesis?.canonical).toBe(false);
  });

  it('does not invent an AB=CD tolerance', () => {
    expect(G402_STATUS.canonicalTolerance).toBeNull();
  });
});
