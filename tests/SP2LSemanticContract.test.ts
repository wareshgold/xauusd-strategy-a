import { describe, expect, it } from 'vitest';
import {
  SP2L_SEMANTIC_CONTRACT,
  SP2L_SEMANTIC_CONTRACT_VERSION,
} from '../src/domain/strategy-a/SP2LSemanticContract';

describe('SP2L frozen semantic contract', () => {
  it('pins the source-aligned sequence and execution semantics', () => {
    expect(SP2L_SEMANTIC_CONTRACT.identity).toBe('SPIKE_2_LEG');
    expect(SP2L_SEMANTIC_CONTRACT.sequence).toEqual([
      'SPIKE',
      'CORRECTION',
      'SECOND_LEG',
    ]);
    expect(SP2L_SEMANTIC_CONTRACT.validSpikeRequiresPGAP).toBe(true);
    expect(SP2L_SEMANTIC_CONTRACT.entry).toBe('PENDING_LIMIT');
    expect(SP2L_SEMANTIC_CONTRACT.baseTarget).toBe('ONE_TO_ONE');
    expect(SP2L_SEMANTIC_CONTRACT.legRelationship).toBe('AB_EQUAL_CD');
  });

  it('pins bullish/bearish correction semantics', () => {
    expect(SP2L_SEMANTIC_CONTRACT.correctionReference).toEqual({
      BUY: 'PREVIOUS_OR_RELEVANT_LOW',
      SELL: 'PREVIOUS_OR_RELEVANT_HIGH',
    });
  });

  it('keeps unresolved executable geometry explicitly unresolved', () => {
    expect(SP2L_SEMANTIC_CONTRACT.unresolvedGeometry).toEqual(expect.arrayContaining([
      'P_GAP_OHLC_BOUNDARY',
      'P_GAP_CANDLE_TIMING',
      'ENTRY_PRICE_FORMULA',
      'SL_WICK_BODY_CONVENTION',
      'LEG1_EXACT_ANCHORS',
      'AB_CD_TOLERANCE',
    ]));
  });

  it('keeps non-source shortcuts outside the canonical contract', () => {
    expect(SP2L_SEMANTIC_CONTRACT.forbiddenCanonicalShortcuts).toEqual(expect.arrayContaining([
      'GENERIC_FVG_AS_P_GAP',
      'CLASSICAL_ABCD_FIBONACCI_MAPPING',
      'MARKET_CLOSE_RECLAIM_AS_ENTRY',
      'FIFTY_PERCENT_RETRACEMENT_AS_BASE_ENTRY',
    ]));
  });

  it('has an explicit semantic-contract version', () => {
    expect(SP2L_SEMANTIC_CONTRACT_VERSION).toBe('2026-09-08.v1');
  });
});
