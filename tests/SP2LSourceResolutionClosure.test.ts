import { describe, expect, it } from 'vitest';
import { SP2L_SEMANTIC_CONTRACT } from '../src/domain/strategy-a/SP2LSemanticContract.js';

describe('SP2L source-resolution closure guardrails', () => {
  it('keeps the semantic contract executable-state free', () => {
    expect(SP2L_SEMANTIC_CONTRACT.identity).toBe('SPIKE_2_LEG');
    expect(SP2L_SEMANTIC_CONTRACT.entry).toBe('PENDING_LIMIT');
    expect(SP2L_SEMANTIC_CONTRACT.stop).toBe('BEHIND_SPIKE_ORIGIN_CANDLE');
    expect(SP2L_SEMANTIC_CONTRACT.legRelationship).toBe('AB_EQUAL_CD');
    expect(SP2L_SEMANTIC_CONTRACT.baseTarget).toBe('ONE_TO_ONE');
  });

  it('keeps every unresolved geometry field explicitly unresolved', () => {
    const required = [
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
    ] as const;

    for (const field of required) {
      expect(SP2L_SEMANTIC_CONTRACT.unresolvedGeometry).toContain(field);
    }
  });

  it('does not authorize forbidden canonical shortcuts', () => {
    expect(SP2L_SEMANTIC_CONTRACT.forbiddenCanonicalShortcuts).toEqual(
      expect.arrayContaining([
        'GENERIC_FVG_AS_P_GAP',
        'CLASSICAL_ABCD_FIBONACCI_MAPPING',
        'MARKET_CLOSE_RECLAIM_AS_ENTRY',
        'FIFTY_PERCENT_RETRACEMENT_AS_BASE_ENTRY',
      ]),
    );
  });
});
