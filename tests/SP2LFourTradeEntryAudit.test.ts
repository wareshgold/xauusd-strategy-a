import { describe, expect, it } from 'vitest';
import { SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES } from './fixtures/SP2LFourTradeEntryAudit.fixtures.js';

describe('SP2L four-trade source entry audit', () => {
  it('preserves all four source-visible execution records', () => {
    expect(SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES.map((f) => f.id)).toEqual(['T1', 'T2', 'T3', 'T4']);
  });

  it('does not convert observed fills into resolved geometric entry prices', () => {
    for (const fixture of SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES) {
      expect(fixture.geometricEntryResolved).toBe(false);
    }
  });

  it('does not promote last-spike breakout to the canonical entry prerequisite', () => {
    for (const fixture of SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES) {
      expect(fixture.lastSpikeBreakoutRequired).toBe(false);
    }
  });

  it('keeps direction unresolved where the visible trade screenshot is insufficient', () => {
    for (const fixture of SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES) {
      expect(fixture.direction).toBe('UNRESOLVED');
    }
  });
});
