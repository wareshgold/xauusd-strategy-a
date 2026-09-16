import { describe, expect, it } from 'vitest';
import { SP2L_125R_GOLDEN_FIXTURE } from '../research/harness/sp2l_125r_golden_fixture_v1';

const EXPECTED = {
  fixtureId: 'SP2L-125R-2026-08-20-20:54:00',
  direction: 'SELL',
  entry: 4521.5838,
  stopLoss: 4521.61331,
  tp1: 4517.8892399999995,
  riskDistance: 0.02951,
  rMultiple: 125.19688241535353,
  sourceClassification: 'UNRESOLVED_AT_SOURCE_LEVEL',
} as const;

describe('SP2L 125R golden fixture', () => {
  it('preserves the exact persisted forensic observation', () => {
    expect(SP2L_125R_GOLDEN_FIXTURE).toEqual(EXPECTED);
  });

  it('remains research-only and carries no trading decision surface', () => {
    const forbidden = ['buy', 'sell', 'signal', 'order', 'position'];
    const keys = Object.keys(SP2L_125R_GOLDEN_FIXTURE).map((key) => key.toLowerCase());

    expect(keys.some((key) => forbidden.includes(key))).toBe(false);
  });

  it('does not reinterpret the 125R observation as source-confirmed geometry', () => {
    expect(SP2L_125R_GOLDEN_FIXTURE.sourceClassification).toBe('UNRESOLVED_AT_SOURCE_LEVEL');
  });
});
