import { describe, expect, it } from 'vitest';
import { SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES } from './fixtures/SP2LPGAPVisualResolution.fixtures.js';

describe('SP2L P-Gap visual resolution', () => {
  it('preserves three accepted-looking and one rejected source constructions', () => {
    expect(SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES.map((f) => f.id)).toEqual(['V1', 'V2', 'V3', 'REJECTED']);
  });

  it('records non-overlap/gap evidence only for accepted-looking constructions', () => {
    for (const fixture of SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES.filter((f) => f.id !== 'REJECTED')) {
      expect(fixture.nonOverlapEvidence).toBe(true);
      expect(fixture.validBreakoutEvidence).toBe(true);
    }
    const rejected = SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES.find((f) => f.id === 'REJECTED');
    expect(rejected?.nonOverlapEvidence).toBe(false);
  });

  it('does not promote any visual rectangle into an executable OHLC formula', () => {
    for (const fixture of SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES) {
      expect(fixture.exactBoundaryResolved).toBe(false);
      expect(fixture.exactCandleTimingResolved).toBe(false);
      expect(fixture.minimumGapResolved).toBe(false);
      expect(fixture.touchEqualityResolved).toBe(false);
    }
  });
});