import { describe, expect, it } from 'vitest';
import {
  differingModelIds,
  everyModelIsResearchOnly,
  evaluateFixture,
  G342_BASELINE,
  G342_NEAREST_SWING_DISTRACTOR,
  G342_PRICE_FIELD_DISCRIMINATOR,
  G342_NESTED_PARENT_DISCRIMINATOR,
} from '../src/domain/research/sp2l-v2/G342AbcdAdversarialDiscrimination.js';

describe('SP2L G342 adversarial AB=CD discrimination (research only)', () => {
  it('keeps all inherited models non-canonical', () => {
    expect(everyModelIsResearchOnly()).toBe(true);
  });

  it('shows local-swing sensitivity while source semantic anchors remain fixed', () => {
    const baseline = evaluateFixture(G342_BASELINE);
    const distracted = evaluateFixture(G342_NEAREST_SWING_DISTRACTOR);
    const baselineNearest = baseline.find((r) => r.modelId.startsWith('NEAREST_SWING'))!;
    const distractedNearest = distracted.find((r) => r.modelId.startsWith('NEAREST_SWING'))!;
    const baselineSource = baseline.find((r) => r.modelId.startsWith('SOURCE_DEEP_LOW'))!;
    const distractedSource = distracted.find((r) => r.modelId.startsWith('SOURCE_DEEP_LOW'))!;
    expect(baselineNearest.aId).toBe('swing-near-b');
    expect(distractedNearest.aId).toBe('swing-near-b');
    expect(distractedNearest.projectedD).not.toBe(baselineNearest.projectedD);
    expect(distractedSource.projectedD).toBe(baselineSource.projectedD);
  });

  it('shows explicit price-field sensitivity without selecting wick or body semantics', () => {
    const results = evaluateFixture(G342_PRICE_FIELD_DISCRIMINATOR);
    const low = results.find((r) => r.modelId === 'SOURCE_DEEP_LOW_TO_PARENT_HIGH__CORRECTION_LOW__WICK')!;
    const close = results.find((r) => r.modelId === 'BREAKOUT_CLOSE_TO_PARENT_CLOSE__CORRECTION_CLOSE__BODY')!;
    expect(low.aId).toBe('deep-origin');
    expect(close.aId).toBe('breakout');
    expect(low.projectedD).not.toBe(close.projectedD);
  });

  it('shows parent and nested scale divergence', () => {
    const results = evaluateFixture(G342_NESTED_PARENT_DISCRIMINATOR);
    const parent = results.find((r) => r.modelId.startsWith('SOURCE_DEEP_LOW_TO_PARENT_HIGH'))!;
    const nested = results.find((r) => r.modelId.startsWith('NEAREST_SWING_TO_NESTED_HIGH'))!;
    expect(parent.bId).toBe('parent-b');
    expect(nested.bId).toBe('nested-b');
    expect(parent.projectedD).not.toBe(nested.projectedD);
  });

  it('keeps correction reference distinct from fill-as-C', () => {
    const results = evaluateFixture(G342_BASELINE);
    const correction = results.find((r) => r.modelId === 'SOURCE_DEEP_LOW_TO_PARENT_HIGH__CORRECTION_LOW__WICK')!;
    const fill = results.find((r) => r.modelId === 'SOURCE_ORIGIN_TO_PARENT_HIGH__FILL_AS_C__WICK')!;
    expect(correction.cId).toBe('correction');
    expect(fill.cId).toBe('fill');
    expect(correction.cId).not.toBe(fill.cId);
    expect(correction.projectedD).not.toBe(fill.projectedD);
  });

  it('reports divergence only; it does not create a ranking or optimization score', () => {
    const differing = differingModelIds(G342_BASELINE);
    expect(differing.length).toBeGreaterThan(0);
    expect(differing.some((id) => id.includes('CANONICAL'))).toBe(false);
  });
});
