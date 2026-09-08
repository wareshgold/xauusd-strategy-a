import { describe, expect, it } from 'vitest';
import { SP2L_PGAP_TIMING_RESOLUTION_FIXTURES } from './fixtures/SP2LPGAPTimingResolution.fixtures.js';

describe('SP2L P-Gap timing and candle identity', () => {
  it('preserves three distinct source-described timing constructions', () => {
    expect(SP2L_PGAP_TIMING_RESOLUTION_FIXTURES.map((f) => f.id)).toEqual(['V1', 'V2', 'V3']);
  });

  it('keeps the source-safe invariant that P-Gap evidence belongs to the Spike/breakout sequence', () => {
    for (const fixture of SP2L_PGAP_TIMING_RESOLUTION_FIXTURES) {
      expect(fixture.gapMustBeWithinSpikeSequence).toBe(true);
    }
  });

  it('does not promote timing observations into a fixed candle index or three-candle formula', () => {
    for (const fixture of SP2L_PGAP_TIMING_RESOLUTION_FIXTURES) {
      expect(fixture.exactCandleIndexResolved).toBe(false);
      expect(fixture.exactBoundaryResolved).toBe(false);
      expect(fixture.threeCandleFormulaCanonical).toBe(false);
    }
  });
});
