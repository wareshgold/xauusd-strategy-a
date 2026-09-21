import { describe, expect, it } from 'vitest';
import {
  UNRESOLVED_SYNTHETIC_FIXTURES,
  evaluateUnresolvedFixture,
} from '../../research/harness/sp2l_unresolved_synthetic_fixtures.js';

describe('SP2L unresolved synthetic fixture gate', () => {
  it('covers every unresolved feature', () => {
    const expected = new Set([
      'F08', 'F09', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'P-GAP', 'ROUND-LEVEL',
    ]);
    const actual = new Set(UNRESOLVED_SYNTHETIC_FIXTURES.map((fixture) => fixture.feature));
    expect(actual).toEqual(expected);
  });

  it('keeps every unresolved fixture non-canonical', () => {
    for (const fixture of UNRESOLVED_SYNTHETIC_FIXTURES) {
      const result = evaluateUnresolvedFixture(fixture);
      expect(result.canonicalEligible).toBe(false);
      expect(result.sourceState).toBe('UNRESOLVED');
      expect(result.preservedCandidates).toEqual(fixture.candidates);
      expect(result.preservedEvents).toEqual(fixture.events);
    }
  });

  it('keeps event distinctions explicit', () => {
    const f11 = UNRESOLVED_SYNTHETIC_FIXTURES.find((x) => x.id === 'F11-006');
    const f12 = UNRESOLVED_SYNTHETIC_FIXTURES.find((x) => x.id === 'F12-002');
    expect(f11?.events).toEqual(['touch', 'breach', 'close', 'fill']);
    expect(f12?.events).toEqual(['trigger', 'activation']);
  });

  it('does not silently introduce bullish-to-bearish symmetry', () => {
    const bearish = UNRESOLVED_SYNTHETIC_FIXTURES.filter(
      (x) => x.direction === 'SELL' && ['F08-004', 'F15-001', 'F15-003'].includes(x.id),
    );
    expect(bearish).toHaveLength(3);
    for (const fixture of bearish) {
      expect(evaluateUnresolvedFixture(fixture).canonicalEligible).toBe(false);
    }
  });

  it('does not let fixture evaluation mutate canonical eligibility', () => {
    expect(UNRESOLVED_SYNTHETIC_FIXTURES.every((fixture) => fixture.canonicalEligible === false)).toBe(true);
  });
});
