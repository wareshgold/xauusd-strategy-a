import { describe, expect, it } from 'vitest';
import { SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES } from './fixtures/SP2LEntryPriceGeometry.fixtures.js';

describe('SP2L entry price geometry discrimination', () => {
  it('contains mirrored BUY and SELL fixtures with separated extreme anchors', () => {
    expect(SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES.map((f) => f.id)).toEqual(
      expect.arrayContaining(['EPG-BUY-DISTINCT-ALL-EXTREMES', 'EPG-SELL-DISTINCT-ALL-EXTREMES']),
    );
  });

  it('keeps wick-vs-body interpretation explicitly unresolved', () => {
    for (const id of ['EPG-BUY-WICK-BODY-DISCRIMINATION', 'EPG-SELL-WICK-BODY-DISCRIMINATION']) {
      const fixture = SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES.find((f) => f.id === id);
      expect(fixture).toBeDefined();
      expect(fixture?.expectedHypothesisValues.H1_PREVIOUS_CANDLE_EXTREME).toBe('UNRESOLVED');
      expect(fixture?.expectedHypothesisValues.H4_PREVIOUS_CANDLE_BODY_EDGE).toBe('UNRESOLVED');
    }
  });

  it('keeps previous-candle vs first-correction-candle anchor unresolved', () => {
    const fixture = SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES.find(
      (f) => f.id === 'EPG-BUY-NEW-CORRECTION-LOW',
    );

    expect(fixture).toBeDefined();
    expect(fixture?.expectedHypothesisValues.H1_PREVIOUS_CANDLE_EXTREME).toBe('UNRESOLVED');
    expect(fixture?.expectedHypothesisValues.H2_FIRST_CORRECTION_CANDLE_EXTREME).toBe('UNRESOLVED');
  });

  it('never promotes an executable entry price from synthetic geometry alone', () => {
    for (const fixture of SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES) {
      expect(fixture.sourceSemantic).toBe('PENDING_LIMIT_DURING_CORRECTION');
      for (const value of Object.values(fixture.expectedHypothesisValues)) {
        expect(value).toBe('UNRESOLVED');
      }
    }
  });

  it('covers both direction mirrors', () => {
    expect(SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES.some((f) => f.direction === 'BUY')).toBe(true);
    expect(SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES.some((f) => f.direction === 'SELL')).toBe(true);
  });
});
