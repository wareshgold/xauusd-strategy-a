import { describe, expect, it } from 'vitest';
import { SP2L_EXECUTABLE_GEOMETRY_FIXTURES } from './fixtures/SP2LExecutableGeometry.fixtures.js';

describe('SP2L executable geometry discrimination fixtures', () => {
  it('covers both directions and all unresolved executable components', () => {
    expect(SP2L_EXECUTABLE_GEOMETRY_FIXTURES.some((f) => f.direction === 'BULLISH')).toBe(true);
    expect(SP2L_EXECUTABLE_GEOMETRY_FIXTURES.some((f) => f.direction === 'BEARISH')).toBe(true);

    const text = SP2L_EXECUTABLE_GEOMETRY_FIXTURES.flatMap((f) => f.competingInterpretations).join('|');
    expect(text).toContain('immediately previous low');
    expect(text).toContain('immediately previous high');
    expect(text).toContain('origin low/wick');
    expect(text).toContain('origin high/wick');
    expect(text).toContain('Spike-origin → Spike-extreme');
    expect(text).toContain('exact AB = CD');
  });

  it('does not encode a canonical executable choice where source geometry is unresolved', () => {
    expect(
      SP2L_EXECUTABLE_GEOMETRY_FIXTURES
        .filter((f) => f.expectedResolution === 'UNRESOLVED')
        .length,
    ).toBe(SP2L_EXECUTABLE_GEOMETRY_FIXTURES.length);
  });

  it('keeps fixture data free of invented entry, stop, and gap prices', () => {
    for (const fixture of SP2L_EXECUTABLE_GEOMETRY_FIXTURES) {
      expect('entryPrice' in fixture).toBe(false);
      expect('stopPrice' in fixture).toBe(false);
      expect('pgapStartPrice' in fixture).toBe(false);
      expect('pgapEndPrice' in fixture).toBe(false);
      expect('abCdTolerance' in fixture).toBe(false);
    }
  });

  it('contains enough variation to prevent a single-anchor shortcut from passing all fixtures', () => {
    const multiCandidateFixtures = SP2L_EXECUTABLE_GEOMETRY_FIXTURES.filter(
      (f) => f.competingInterpretations.length >= 2,
    );
    expect(multiCandidateFixtures.length).toBeGreaterThanOrEqual(6);
  });
});
