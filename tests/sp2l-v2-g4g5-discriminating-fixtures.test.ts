import { describe, expect, it } from 'vitest';
import {
  BEAR_MIRROR_FIXTURE,
  BULL_FOUR_ANCHOR_FIXTURE,
  EXPECTED_BULL_G4_MAGNITUDES,
  EXPECTED_BULL_G5_MAGNITUDES,
  EXPECTED_NESTED_MAGNITUDES,
  NEG_C_BEFORE_CORRECTION_FIXTURE,
  NEG_MISSING_STRUCTURAL_REFERENCE_FIXTURE,
  NEG_NON_FINITE_FIXTURE,
  NEG_NO_RANGE_FIXTURE,
  NESTED_LEG_FIXTURE,
} from '../src/domain/research/sp2l-v2/G4G5DiscriminatingFixtures.js';
import {
  assessFixture,
  G4_ENDPOINT_FAMILIES,
  measureExplicitSegment,
  measureLeg1,
  measureLeg2,
  reportCandidates,
} from '../src/domain/research/sp2l-v2/G4G5CandidateMeasurement.js';
import { resolveSameCandleTouch } from '../src/domain/research/sp2l-v2/Sp2lSemanticState.js';

describe('SP2L V2 G4/G5 discriminating fixtures (non-production)', () => {
  it('produces the hand-computed distinct Leg 1 magnitudes for every G4 family on the bull fixture', () => {
    for (const family of G4_ENDPOINT_FAMILIES) {
      expect(measureLeg1(BULL_FOUR_ANCHOR_FIXTURE, family)).toBe(EXPECTED_BULL_G4_MAGNITUDES[family]);
    }

    const magnitudes = G4_ENDPOINT_FAMILIES.map((f) => measureLeg1(BULL_FOUR_ANCHOR_FIXTURE, f));
    expect(new Set(magnitudes).size).toBe(G4_ENDPOINT_FAMILIES.length);
  });

  it('produces the hand-computed distinct Leg 2 magnitudes for every G5 candidate on the bull fixture', () => {
    const candidates = ['CORRECTION_EXTREME', 'STRUCTURAL_HL_LH', 'OTHER_VISUAL_POINT', 'PENDING_LIMIT', 'ACTUAL_FILL'] as const;
    for (const candidate of candidates) {
      expect(measureLeg2(BULL_FOUR_ANCHOR_FIXTURE, candidate)).toBe(EXPECTED_BULL_G5_MAGNITUDES[candidate]);
    }
  });

  it('reports all candidates side by side without selecting a canonical one', () => {
    const report = reportCandidates(BULL_FOUR_ANCHOR_FIXTURE);
    expect(report.canonicalSelection).toBeNull();
    expect(report.leg1Candidates).toHaveLength(G4_ENDPOINT_FAMILIES.length);
    expect(report.leg2Candidates).toHaveLength(5);

    const status = Object.fromEntries(report.leg2Candidates.map((c) => [c.candidate, c.canonicalStatus]));
    expect(status.CORRECTION_EXTREME).toBe('ALIVE');
    expect(status.STRUCTURAL_HL_LH).toBe('ALIVE');
    expect(status.OTHER_VISUAL_POINT).toBe('ALIVE');
    expect(status.PENDING_LIMIT).toBe('EXCLUDED_NON_CANONICAL');
    expect(status.ACTUAL_FILL).toBe('EXCLUDED_NON_CANONICAL');
  });

  it('mirrors the bull fixture into a bearish chart with identical magnitudes', () => {
    expect(BEAR_MIRROR_FIXTURE.direction).toBe('BEARISH');
    expect(BEAR_MIRROR_FIXTURE.anchors.find((a) => a.concept === 'spikeExtreme')?.element).toBe('LOW');

    for (const family of G4_ENDPOINT_FAMILIES) {
      expect(measureLeg1(BEAR_MIRROR_FIXTURE, family)).toBe(EXPECTED_BULL_G4_MAGNITUDES[family]);
    }
    for (const candidate of ['CORRECTION_EXTREME', 'STRUCTURAL_HL_LH', 'OTHER_VISUAL_POINT', 'PENDING_LIMIT', 'ACTUAL_FILL'] as const) {
      expect(measureLeg2(BEAR_MIRROR_FIXTURE, candidate)).toBe(EXPECTED_BULL_G5_MAGNITUDES[candidate]);
    }
  });

  it('distinguishes the parent 2Leg from the nested 2Leg and their targets', () => {
    const parentLeg1 = measureExplicitSegment(
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'parentA')!.price,
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'parentB')!.price,
    );
    const parentLeg2 = measureExplicitSegment(
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'parentCorrectionExtreme')!.price,
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'parentLeg2End')!.price,
    );
    const nestedLeg1 = measureExplicitSegment(
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'nestedA')!.price,
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'nestedB')!.price,
    );
    const nestedLeg2 = measureExplicitSegment(
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'nestedCorrectionExtreme')!.price,
      NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'nestedTP')!.price,
    );

    expect(parentLeg1).toBe(EXPECTED_NESTED_MAGNITUDES.parentLeg1);
    expect(parentLeg2).toBe(EXPECTED_NESTED_MAGNITUDES.parentLeg2);
    expect(nestedLeg1).toBe(EXPECTED_NESTED_MAGNITUDES.nestedLeg1);
    expect(nestedLeg2).toBe(EXPECTED_NESTED_MAGNITUDES.nestedLeg2);

    expect(parentLeg1).not.toBe(nestedLeg1);

    const nestedTp = NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'nestedTP')!.price;
    const parentTp1 = NESTED_LEG_FIXTURE.anchors.find((a) => a.concept === 'parentLeg2End')!.price;
    expect(nestedTp).not.toBe(parentTp1);
  });

  it('marks a fixture without a preceding range as ineligible', () => {
    const audit = assessFixture(NEG_NO_RANGE_FIXTURE);
    expect(audit.eligible).toBe(false);
    expect(audit.reasons).toContain('SPIKE_REQUIRES_CONTEXT_RANGE');
  });

  it('fails closed when the first structural reference anchor is missing', () => {
    expect(() =>
      measureLeg1(NEG_MISSING_STRUCTURAL_REFERENCE_FIXTURE, 'STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME'),
    ).toThrow(/ANCHOR_MISSING_FIRST_STRUCTURAL_LOW/);
  });

  it('rejects a Leg 2 origin that precedes the correction', () => {
    expect(() => measureLeg2(NEG_C_BEFORE_CORRECTION_FIXTURE, 'OTHER_VISUAL_POINT')).toThrow(
      'LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION',
    );
  });

  it('throws on non-finite candle geometry instead of silently measuring', () => {
    expect(() => assessFixture(NEG_NON_FINITE_FIXTURE)).toThrow('CANDLE_GEOMETRY_MUST_BE_FINITE');
  });

  it('uniquely identifies each G4 family from its magnitude (frame-ready lookup)', () => {
    for (const target of Object.values(EXPECTED_BULL_G4_MAGNITUDES)) {
      const matches = G4_ENDPOINT_FAMILIES.filter((f) => measureLeg1(BULL_FOUR_ANCHOR_FIXTURE, f) === target);
      expect(matches).toHaveLength(1);
    }
  });

  it('keeps same-candle entry/SL/TP ordering an explicit simulator policy', () => {
    const touches = { entry: true, stop: true, tp1: true };
    expect(resolveSameCandleTouch('SL_FIRST', touches)).toBe('STOP');
    expect(resolveSameCandleTouch('TP_FIRST', touches)).toBe('TP1');
    expect(resolveSameCandleTouch('AMBIGUOUS', touches)).toBe('AMBIGUOUS');
  });
});