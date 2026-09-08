/**
 * Frozen semantic contract for Strategy A / SP2L.
 *
 * This file intentionally contains semantic states, not executable OHLC
 * geometry. Any value marked unresolved must be resolved from source before
 * it can become production logic.
 */

export const SP2L_SEMANTIC_CONTRACT_VERSION = '2026-09-08.v1';

export const SP2L_SEMANTIC_CONTRACT = Object.freeze({
  identity: 'SPIKE_2_LEG',
  sequence: ['SPIKE', 'CORRECTION', 'SECOND_LEG'] as const,
  validSpikeRequiresPGAP: true,
  entry: 'PENDING_LIMIT' as const,
  correctionReference: {
    BUY: 'PREVIOUS_OR_RELEVANT_LOW' as const,
    SELL: 'PREVIOUS_OR_RELEVANT_HIGH' as const,
  },
  stop: 'BEHIND_SPIKE_ORIGIN_CANDLE' as const,
  legRelationship: 'AB_EQUAL_CD' as const,
  baseTarget: 'ONE_TO_ONE' as const,
  forbiddenCanonicalShortcuts: [
    'GENERIC_FVG_AS_P_GAP',
    'CLASSICAL_ABCD_FIBONACCI_MAPPING',
    'MARKET_CLOSE_RECLAIM_AS_ENTRY',
    'FIFTY_PERCENT_RETRACEMENT_AS_BASE_ENTRY',
  ] as const,
  unresolvedGeometry: [
    'P_GAP_OHLC_BOUNDARY',
    'P_GAP_CANDLE_TIMING',
    'P_GAP_TOUCH_RULE',
    'P_GAP_MINIMUM_SIZE',
    'ENTRY_CANDLE_IDENTITY',
    'ENTRY_PRICE_FORMULA',
    'SL_WICK_BODY_CONVENTION',
    'SL_BUFFER',
    'LEG1_EXACT_ANCHORS',
    'AB_CD_TOLERANCE',
  ] as const,
} as const);
