export type SemanticDirection = 'BUY' | 'SELL';

export interface SemanticFixture {
  readonly id: string;
  readonly direction: SemanticDirection;
  readonly contextPresent: boolean;
  readonly validPGAPresent: boolean;
  readonly sharpDirectionalMovement: boolean;
  readonly correctionReachesReference: boolean;
  readonly pendingLimitPrepared: boolean;
  readonly structuralInvalidationDefined: boolean;
  readonly leg2MatchesLeg1Semantically: boolean;
  readonly expectedBaseTargetR: 1;
  readonly notes: string;
}

/**
 * Semantic-only fixtures intentionally avoid executable OHLC prices.
 * They test the frozen meaning contract without selecting unresolved geometry.
 */
export const SP2L_SEMANTIC_FIXTURES: readonly SemanticFixture[] = [
  {
    id: 'SEM-BULL-VALID',
    direction: 'BUY',
    contextPresent: true,
    validPGAPresent: true,
    sharpDirectionalMovement: true,
    correctionReachesReference: true,
    pendingLimitPrepared: true,
    structuralInvalidationDefined: true,
    leg2MatchesLeg1Semantically: true,
    expectedBaseTargetR: 1,
    notes: 'Canonical bullish semantic sequence.',
  },
  {
    id: 'SEM-BEAR-VALID',
    direction: 'SELL',
    contextPresent: true,
    validPGAPresent: true,
    sharpDirectionalMovement: true,
    correctionReachesReference: true,
    pendingLimitPrepared: true,
    structuralInvalidationDefined: true,
    leg2MatchesLeg1Semantically: true,
    expectedBaseTargetR: 1,
    notes: 'Canonical bearish mirror semantic sequence.',
  },
  {
    id: 'SEM-NO-PGAP',
    direction: 'BUY',
    contextPresent: true,
    validPGAPresent: false,
    sharpDirectionalMovement: true,
    correctionReachesReference: true,
    pendingLimitPrepared: true,
    structuralInvalidationDefined: true,
    leg2MatchesLeg1Semantically: true,
    expectedBaseTargetR: 1,
    notes: 'Sharp movement without source-defined P-Gap is not a valid canonical Spike.',
  },
  {
    id: 'SEM-MARKET-RECLAIM-ONLY',
    direction: 'BUY',
    contextPresent: true,
    validPGAPresent: true,
    sharpDirectionalMovement: true,
    correctionReachesReference: true,
    pendingLimitPrepared: false,
    structuralInvalidationDefined: true,
    leg2MatchesLeg1Semantically: true,
    expectedBaseTargetR: 1,
    notes: 'Market close-reclaim without a pending limit is not canonical entry semantics.',
  },
  {
    id: 'SEM-50PCT-ONLY',
    direction: 'BUY',
    contextPresent: true,
    validPGAPresent: true,
    sharpDirectionalMovement: true,
    correctionReachesReference: true,
    pendingLimitPrepared: true,
    structuralInvalidationDefined: true,
    leg2MatchesLeg1Semantically: true,
    expectedBaseTargetR: 1,
    notes: 'A 50% add-on/management idea must not replace the base source entry semantic.',
  },
];
