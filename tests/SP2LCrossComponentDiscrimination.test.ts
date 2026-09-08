import { describe, expect, it } from 'vitest';
import { SP2L_CROSS_COMPONENT_FIXTURES } from './fixtures/SP2LCrossComponent.fixtures.js';

describe('SP2L cross-component discrimination', () => {
  it('covers complete bullish and bearish component chains', () => {
    const complete = SP2L_CROSS_COMPONENT_FIXTURES.filter((f) => f.stages.length >= 8);
    expect(complete.some((f) => f.direction === 'BULLISH')).toBe(true);
    expect(complete.some((f) => f.direction === 'BEARISH')).toBe(true);
    expect(complete.every((f) => f.stages.includes('P_GAP'))).toBe(true);
    expect(complete.every((f) => f.stages.includes('PENDING_LIMIT'))).toBe(true);
  });

  it('requires source semantics to remain distinct from executable geometry', () => {
    for (const fixture of SP2L_CROSS_COMPONENT_FIXTURES) {
      expect(fixture.sourceConfirmed.length).toBeGreaterThan(0);
      expect(fixture.competingGeometry.length).toBeGreaterThan(0);
      expect(fixture.expectedGate).toBe('BLOCKED');
    }
  });

  it('does not permit cross-component consistency to manufacture missing anchors', () => {
    const allCompeting = SP2L_CROSS_COMPONENT_FIXTURES.flatMap((f) => f.competingGeometry).join('|');
    expect(allCompeting).toContain('origin wick vs origin body');
    expect(allCompeting).toContain('origin-to-extreme vs breakout-to-extreme');
    expect(allCompeting).toContain('exact AB=CD vs unspecified near-equality tolerance');
    expect(allCompeting).toContain('actual order fill price');
  });

  it('explicitly rejects importing classical Fibonacci ABCD geometry', () => {
    const fixture = SP2L_CROSS_COMPONENT_FIXTURES.find((f) => f.id === 'XC-ABCD-NO-CLASSICAL-FIB');
    expect(fixture).toBeDefined();
    expect(fixture?.competingGeometry).toContain('classical harmonic A/B/C/Fibonacci mapping');
    expect(fixture?.sourceConfirmed).toContain('source explicitly frames AB=CD at candle level');
  });

  it('keeps the geometry gate blocked until every executable anchor is source-resolved', () => {
    expect(SP2L_CROSS_COMPONENT_FIXTURES.every((f) => f.expectedGate === 'BLOCKED')).toBe(true);
  });
});
