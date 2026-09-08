import { describe, expect, it } from 'vitest';
import { SP2L_SYNTHETIC_DISCRIMINATION_FIXTURES } from './fixtures/SP2LSyntheticDiscrimination.fixtures.js';

describe('SP2L synthetic discrimination gate', () => {
  it('covers every currently unresolved executable field', () => {
    const fields = new Set(SP2L_SYNTHETIC_DISCRIMINATION_FIXTURES.map((fixture) => fixture.field));
    expect(fields).toEqual(new Set([
      'PGAP_BOUNDARY',
      'PGAP_CANDLE_IDENTITY',
      'PGAP_TOUCH_RULE',
      'ENTRY_CANDLE_IDENTITY',
      'ENTRY_PRICE_CONVENTION',
      'ENTRY_REVISION_SEMANTICS',
      'FILL_TOUCH_SEMANTICS',
      'SL_BOUNDARY',
      'SPIKE_ORIGIN_IDENTITY',
      'LEG1_ANCHORS',
      'AB_CD_TOLERANCE',
    ]));
  });

  it('requires source evidence before any hypothesis can be selected', () => {
    for (const fixture of SP2L_SYNTHETIC_DISCRIMINATION_FIXTURES) {
      expect(fixture.candidatesAreUnresolved).toBe(true);
      expect(fixture.sourceEvidenceRequiredToSelect).toBe(true);
      expect(fixture.productionEligible).toBe(false);
      expect(fixture.candidateHypotheses.length).toBeGreaterThan(1);
    }
  });

  it('keeps the synthetic gate independent of profitability', () => {
    for (const fixture of SP2L_SYNTHETIC_DISCRIMINATION_FIXTURES) {
      expect('backtestWinRate' in fixture).toBe(false);
      expect('expectancyR' in fixture).toBe(false);
      expect('profitFactor' in fixture).toBe(false);
    }
  });
});
