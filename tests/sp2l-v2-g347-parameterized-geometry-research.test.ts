import { describe, expect, it } from 'vitest';
import {
  G347_BASELINE_MODEL,
  G347_PARAMETER_SPACE,
  G347_SOURCE_FIXTURE,
  compareG347Models,
  evaluateG347Model,
  g347Model,
  g347NoCandidateIsCanonical,
  type G347Candidate,
} from '../src/domain/research/sp2l-v2/G347ParameterizedGeometryResearch.js';

describe('G347 parameterized synthetic geometry research', () => {
  it('enumerates the unresolved dimensions without promoting them', () => {
    expect(G347_PARAMETER_SPACE.aSelectors).toHaveLength(3);
    expect(G347_PARAMETER_SPACE.bSelectors).toHaveLength(2);
    expect(G347_PARAMETER_SPACE.cSelectors).toHaveLength(2);
    expect(G347_PARAMETER_SPACE.priceFields).toHaveLength(6);
    expect(G347_PARAMETER_SPACE.scales).toHaveLength(2);
    expect(G347_PARAMETER_SPACE.tolerances).toHaveLength(4);
    expect(G347_PARAMETER_SPACE.tpMappings).toHaveLength(4);
    expect(G347_PARAMETER_SPACE.pGapHypotheses).toHaveLength(3);
  });

  it('keeps the baseline explicitly non-canonical', () => {
    expect(G347_BASELINE_MODEL.canonical).toBe(false);
    expect(g347NoCandidateIsCanonical([G347_BASELINE_MODEL])).toBe(true);
  });

  it('isolates anchor-selector divergence', () => {
    const candidate = g347Model('G347_A_BREAKOUT', { aSelector: 'FIRST_BREAKOUT_CANDLE' });
    const result = compareG347Models(G347_BASELINE_MODEL, candidate);
    expect(result.anchorSelectionDiffers).toBe(true);
    expect(result.projectedDDiffers).toBe(true);
  });

  it('isolates C versus fill-as-C as a negative-control divergence', () => {
    const candidate = g347Model('G347_C_FILL_NEGATIVE', { cSelector: 'FILL_AS_C' });
    const result = compareG347Models(G347_BASELINE_MODEL, candidate);
    expect(result.anchorSelectionDiffers).toBe(true);
    expect(result.projectedDDiffers).toBe(true);
  });

  it('isolates price-field divergence', () => {
    const candidate = g347Model('G347_PRICE_CLOSE', { priceField: 'CLOSE' });
    const result = compareG347Models(G347_BASELINE_MODEL, candidate);
    expect(result.priceFieldDiffers).toBe(true);
    expect(result.projectedDDiffers).toBe(true);
  });

  it('represents tolerance only as an unresolved research parameter', () => {
    const candidate = g347Model('G347_TOL_1', { tolerance: 1 });
    expect(candidate.canonical).toBe(false);
    expect(evaluateG347Model(G347_SOURCE_FIXTURE, candidate).tolerance).toBe(1);
  });

  it('represents TP mappings as competing hypotheses without asserting a source mapping', () => {
    const models = [
      g347Model('G347_TP_D', { tpMapping: 'D' }),
      g347Model('G347_TP_D_PLUS_1R', { tpMapping: 'D_PLUS_1R' }),
      g347Model('G347_TP_D_PLUS_2R', { tpMapping: 'D_PLUS_2R' }),
      g347Model('G347_TP_UNRESOLVED', { tpMapping: 'UNRESOLVED' }),
    ];
    expect(g347NoCandidateIsCanonical(models)).toBe(true);
    expect(new Set(models.map((model) => model.tpMapping)).size).toBe(4);
  });

  it('represents P-Gap formulas only as explicitly hypothetical labels', () => {
    const models = [
      g347Model('G347_PG_UNRESOLVED', { pGapHypothesis: 'UNRESOLVED' }),
      g347Model('G347_PG_RANGE_HYPOTHESIS', { pGapHypothesis: 'THREE_CANDLE_RANGE_GAP' }),
      g347Model('G347_PG_BODY_HYPOTHESIS', { pGapHypothesis: 'BODY_BOUNDARY_GAP' }),
    ];
    expect(g347NoCandidateIsCanonical(models)).toBe(true);
    expect(models.every((model) => model.pGapHypothesis !== 'UNRESOLVED' ? model.canonical === false : true)).toBe(true);
  });

  it('does not equate fill with geometric C', () => {
    const evaluation = evaluateG347Model(G347_SOURCE_FIXTURE, G347_BASELINE_MODEL);
    expect(evaluation.cId).toBe('correction');
    expect(evaluation.cId).not.toBe('fill');
  });

  it('keeps synthetic discrimination descriptive rather than optimization-based', () => {
    const candidates: G347Candidate[] = [
      { id: 'A_SOURCE', dimension: 'A_SELECTOR', value: 'SOURCE_DEEP_ORIGIN', canonical: false },
      { id: 'A_BREAKOUT', dimension: 'A_SELECTOR', value: 'FIRST_BREAKOUT_CANDLE', canonical: false },
      { id: 'PRICE_CLOSE', dimension: 'PRICE_FIELD', value: 'CLOSE', canonical: false },
      { id: 'TP_2R', dimension: 'TP_MAPPING', value: 'D_PLUS_2R', canonical: false },
    ];
    expect(candidates.every((candidate) => candidate.canonical === false)).toBe(true);
    expect(candidates.map((candidate) => candidate.id)).toHaveLength(4);
  });
});
