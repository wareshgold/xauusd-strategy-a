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

  it('shows that a local distractor can change a nearest-swing hypothesis while source anchors remain explicit', () => {
    const baseline = evaluateFixture(G342_BASELINE);
    const distracted = evaluateFixture(G342_NEAREST_SWING_DISTRACTOR);
    const baselineNearest = baseline.find((r) => r.modelId.startsWith('NEAREST_SWING'))!;
    const distractedNearest = distracted.find((r) => r.modelId.startsWith('NEAREST_SWING'))!;
    expect(baselineNearest.aId).toBe('swing-near-b');
    expect(distractedNearest.aId).toBe('swing-near-b');
    expect(distractedNearest.projectedD).not.toBe(baselineNearest.projectedD);
  });

  it('shows explicit price-field sensitivity at the same semantic anchors', () => {
    const results = evaluateFixture(G342_PRICE_FIELD_DISCRIMINATOR);
    const wick = results.find((r) => r.modelId === 'SOURCE_DEEP_LOW_TO_PARENT_HIGH__CORRECTION_LOW__WICK')!;
    const close = results.find((r) => r.modelId === 'BREAKOUT_CLOSE_TO_PARENT_CLOSE__CORRECTION_CLOSE__BODY')!;
    expect(wick.aId).toBe('deep-origin');
    expect(close.aId).toBe('breakout');
    expect(wick.projectedD).not.toBe(close.projectedD);
  });

  it('shows parent/nested scale remains a distinct unresolved dimension', () => {
    const results = evaluateFixture(G342_NESTED_PARENT_DISCRIMINATOR);
    const parent = results.find((r) => r.modelId.startsWith('SOURCE_DEEP_LOW_TO_PARENT_HIGH'))!;
    const nested = results.find((r) => r.modelId.startsWith('NEAREST_SWING_TO_NESTED_HIGH'))!;
    expect(parent.bId).toBe('parent-b');
    expect(nested.bId).toBe('nested-b');
    expect(parent.projectedD).not.toBe(nested.projectedD);
  });

  it('identifies divergence without ranking models or introducing optimization criteria', () => {
    const differing = differingModelIds(G342_BASELINE);
    expect(differing.length).toBeGreaterThan(0);
    expect(differing).not.toContain('CANONICAL');
  });
});
