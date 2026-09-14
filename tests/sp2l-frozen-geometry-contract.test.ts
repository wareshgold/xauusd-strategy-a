import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const manifestPath = resolve(process.cwd(), 'research/fixtures/sp2l_frozen_geometry_contract_v1.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8')) as {
  schema: string;
  canonical_geometry: boolean;
  gate_state: string;
  confirmed_semantics: string[];
  unresolved_geometry: string[];
  forbidden_inference: string[];
  promotion_requirements: string[];
};

describe('SP2L frozen-geometry contract', () => {
  it('keeps canonical geometry frozen until source resolution is promoted', () => {
    expect(manifest.schema).toBe('sp2l.frozen_geometry_contract.v1');
    expect(manifest.canonical_geometry).toBe(false);
    expect(manifest.gate_state).toBe(
      'SOURCE_RESOLUTION_STOPPED_PENDING_NEW_TIER1_TIER2_DISCRIMINATOR',
    );
  });

  it('retains every known executable geometry blocker as unresolved', () => {
    expect(manifest.unresolved_geometry).toEqual(
      expect.arrayContaining([
        'P_GAP_OHLC_AND_CANDLE_INDEX',
        'ENTRY_PRICE_ANCHOR',
        'LEG_2_START_BOUNDARY',
        'SPIKE_ORIGIN_INVALIDATION_BOUNDARY',
        'PENDING_ORDER_REFRESH_CONDITION',
        'ONE_TWO_THREE_CANDLE_TRIGGER_CLASSIFIER',
        'ABCD_A_B_C_D_ANCHORS',
        'ABCD_EQUALITY_TOLERANCE',
        '2X_TP1_TP2_EXECUTABLE_FORMULAS',
        'BEARISH_MIRROR_GEOMETRY',
      ]),
    );
  });

  it('requires source evidence and manual promotion before canonicalization', () => {
    expect(manifest.promotion_requirements).toEqual(
      expect.arrayContaining([
        'tier1_or_tier2_discriminator',
        'manual_approval',
        'explicit_canonicalization_before_engine_consumption',
      ]),
    );
  });

  it('does not silently remove forbidden inference protections', () => {
    expect(manifest.forbidden_inference).toEqual(
      expect.arrayContaining([
        'generic_three_candle_imbalance_as_P_GAP',
        'internet_standard_ABCD_or_fibonacci_anchors',
        'invented_tolerances_or_buffers',
        'invented_fill_or_intrabar_semantics',
      ]),
    );
  });
});
