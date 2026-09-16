import { FixtureExpectation } from './sp2l_fixture_runner_v1';

/**
 * Source-discrimination manifest only. These cases describe what must be tested;
 * they do not select unresolved geometry or create production signals.
 */
export const SP2L_F09_F14_FIXTURES: FixtureExpectation[] = [
  { id: 'F09_ENTRY_VS_LEG2_START', expected: 'entry anchor remains source-unresolved' },
  { id: 'F10_STOP_ANCHOR', expected: 'structural invalidation is separate from entry; exact OHLC unresolved' },
  { id: 'F11_LIMIT_REFRESH', expected: 'delete/re-place behavior is represented; threshold unresolved' },
  { id: 'F12_TRIGGER_FAMILY', expected: '1/2/3-candle and bar/key-bar variants remain source-described' },
  { id: 'F13_2X_ANCHOR', expected: 'optional second position is represented; exact formula unresolved' },
  { id: 'F14_ABCD_ANCHOR', expected: 'Leg2≈Leg1 magnitude relation is represented; A/B/C/D unresolved' },
];

export const SP2L_PGAP_FIXTURE: FixtureExpectation = {
  id: 'PGAP_EXACT_FORMULA',
  expected: 'exact P-Gap OHLC construction remains unresolved',
};
