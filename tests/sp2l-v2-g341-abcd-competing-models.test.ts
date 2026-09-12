import { describe, expect, it } from 'vitest';
import {
  allModelsRemainNonCanonical,
  evaluateModel,
  G341_MODELS,
  G341_SOURCE_SEMANTIC_FIXTURE,
} from '../src/domain/research/sp2l-v2/G341AbcdCompetingModels.js';

describe('SP2L G341 competing AB=CD models (research only)', () => {
  it('keeps every unresolved geometry model explicitly non-canonical', () => {
    expect(allModelsRemainNonCanonical(G341_MODELS)).toBe(true);
    expect(G341_MODELS.every((model) => model.canonical === false)).toBe(true);
  });

  it('shows that anchor-selection hypotheses produce different A/B/C/D outputs', () => {
    const evaluations = G341_MODELS.map((model) => evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, model));
    const projections = new Set(evaluations.map((evaluation) => evaluation.projectedD));
    expect(projections.size).toBeGreaterThan(1);
  });

  it('keeps fill separate from the source correction reference', () => {
    const sourceModel = G341_MODELS[0]!;
    const fillModel = G341_MODELS[3]!;
    const source = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, sourceModel);
    const fill = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, fillModel);
    expect(source.cId).toBe('correction');
    expect(fill.cId).toBe('fill');
    expect(source.cId).not.toBe(fill.cId);
  });

  it('demonstrates parent and nested B-scale divergence', () => {
    const parent = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, G341_MODELS[0]!);
    const nested = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, G341_MODELS[2]!);
    expect(parent.bId).toBe('parent-b');
    expect(nested.bId).toBe('nested-b');
    expect(parent.bId).not.toBe(nested.bId);
    expect(parent.projectedD).not.toBe(nested.projectedD);
  });

  it('demonstrates price-field divergence without selecting wick or body semantics', () => {
    const wickLike = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, G341_MODELS[0]!);
    const closeLike = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, G341_MODELS[1]!);
    expect(wickLike.aPrice).not.toBe(closeLike.aPrice);
    expect(wickLike.bPrice).not.toBe(closeLike.bPrice);
    expect(wickLike.projectedD).not.toBe(closeLike.projectedD);
  });

  it('uses only translation of the AB price delta and introduces no tolerance', () => {
    const result = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, G341_MODELS[0]!);
    expect(result.projectedD).toBe(result.cPrice + (result.bPrice - result.aPrice));
    expect(Object.keys(G341_MODELS[0]!)).not.toContain('tolerance');
  });
});
