import { describe, expect, it } from 'vitest';
import { SP2L_ABCD_GEOMETRY_FIXTURES } from './fixtures/SP2LAbCdGeometry.fixtures.js';

describe('SP2L AB=CD geometry guardrails', () => {
  it('preserves the source-confirmed equal-leg semantic in both directions', () => {
    expect(SP2L_ABCD_GEOMETRY_FIXTURES.map((f) => f.direction)).toContain('BUY');
    expect(SP2L_ABCD_GEOMETRY_FIXTURES.map((f) => f.direction)).toContain('SELL');
    expect(SP2L_ABCD_GEOMETRY_FIXTURES.every((f) => f.sourceObservation === 'AB_EQUALS_CD')).toBe(true);
  });

  it('does not select executable A/B/C/D anchors from the source visuals', () => {
    for (const fixture of SP2L_ABCD_GEOMETRY_FIXTURES) {
      expect(fixture.sourceShowsExactAnchors).toBe(false);
      expect(fixture.sourceShowsExactTolerance).toBe(false);
      expect(fixture.selectedHypothesis).toBeNull();
    }
  });

  it('keeps classical Fibonacci A/B/C mapping explicitly non-canonical', () => {
    for (const fixture of SP2L_ABCD_GEOMETRY_FIXTURES) {
      expect(fixture.candidateHypotheses).toContain('H4_CLASSICAL_A_B_MAPPING');
    }
  });
});
