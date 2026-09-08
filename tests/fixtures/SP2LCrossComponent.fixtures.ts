export interface CrossComponentFixture {
  readonly id: string;
  readonly direction: 'BULLISH' | 'BEARISH';
  readonly stages: readonly string[];
  readonly competingGeometry: readonly string[];
  readonly sourceConfirmed: readonly string[];
  readonly expectedGate: 'BLOCKED' | 'DISCRIMINATED';
}

/**
 * Research-only fixtures. These intentionally describe OHLC geometry choices
 * without selecting canonical executable prices. They are not imported by
 * production Strategy A code.
 */
export const SP2L_CROSS_COMPONENT_FIXTURES: readonly CrossComponentFixture[] = [
  {
    id: 'XC-BULL-PGAP-ENTRY-SL-LEG1',
    direction: 'BULLISH',
    stages: ['RANGE', 'BREAKOUT', 'FOLLOW_THROUGH', 'P_GAP', 'SPIKE', 'CORRECTION', 'PENDING_LIMIT', 'SL', 'LEG1', 'LEG2'],
    competingGeometry: [
      'P-Gap adjacent-wick boundary vs three-candle outer boundary',
      'previous low vs relevant structural low for pending limit',
      'origin wick vs origin body for invalidation',
      'origin-to-extreme vs breakout-to-extreme for Leg1',
      'exact AB=CD vs unspecified near-equality tolerance',
    ],
    sourceConfirmed: [
      'valid Spike requires P-Gap',
      'correction reaches previous/relevant low',
      'pending-limit entry is allowed during correction',
      'SL is tied to the Spike-origin candle',
      'Leg2 follows Leg1 with AB=CD/equal-leg semantics',
    ],
    expectedGate: 'BLOCKED',
  },
  {
    id: 'XC-BEAR-PGAP-ENTRY-SL-LEG1',
    direction: 'BEARISH',
    stages: ['RANGE', 'BREAKOUT', 'FOLLOW_THROUGH', 'P_GAP', 'SPIKE', 'CORRECTION', 'PENDING_LIMIT', 'SL', 'LEG1', 'LEG2'],
    competingGeometry: [
      'P-Gap bearish boundary alternatives',
      'previous high vs relevant structural high for pending limit',
      'origin wick vs origin body for invalidation',
      'origin-to-extreme vs breakout-to-extreme for Leg1',
      'exact AB=CD vs unspecified near-equality tolerance',
    ],
    sourceConfirmed: [
      'valid Spike requires P-Gap',
      'correction reaches previous/relevant high',
      'pending-limit entry is allowed during correction',
      'SL is tied to the Spike-origin candle',
      'Leg2 follows Leg1 with AB=CD/equal-leg semantics',
    ],
    expectedGate: 'BLOCKED',
  },
  {
    id: 'XC-ENTRY-SEMANTIC-NOT-PRICE',
    direction: 'BULLISH',
    stages: ['SPIKE', 'CORRECTION', 'PENDING_LIMIT'],
    competingGeometry: ['geometric reference level', 'actual order fill price'],
    sourceConfirmed: ['pending-limit semantics', 'correction-to-low semantics'],
    expectedGate: 'BLOCKED',
  },
  {
    id: 'XC-ABCD-NO-CLASSICAL-FIB',
    direction: 'BEARISH',
    stages: ['SPIKE', 'CORRECTION', 'LEG1', 'LEG2'],
    competingGeometry: ['source candle-level equal-leg relation', 'classical harmonic A/B/C/Fibonacci mapping'],
    sourceConfirmed: ['source explicitly frames AB=CD at candle level'],
    expectedGate: 'BLOCKED',
  },
];
