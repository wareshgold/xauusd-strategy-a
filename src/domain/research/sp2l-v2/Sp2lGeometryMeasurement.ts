export interface Sp2lLegMeasurementInput {
  leg1StartPrice: number;
  leg1EndPrice: number;
  leg2StartPrice: number;
  leg2EndPrice: number;
}

export interface Sp2lLegMeasurement {
  leg1Magnitude: number;
  leg2Magnitude: number;
  leg2ToLeg1Ratio: number | null;
  equalityRelation: 'APPROXIMATELY_EQUAL_CANDIDATE' | 'NOT_EQUAL_CANDIDATE' | 'UNDETERMINED';
  equalityTolerance: number | null;
}

function assertFinitePrice(name: string, value: number): void {
  if (!Number.isFinite(value)) {
    throw new Error(`${name}_MUST_BE_FINITE`);
  }
}

/**
 * Research-only measurement helper.
 *
 * The caller must supply the source-selected endpoints. This helper deliberately
 * does not select A/B/C points, infer a correction origin, or fit an equality
 * tolerance from historical outcomes.
 */
export function measureSp2lLegs(input: Sp2lLegMeasurementInput): Sp2lLegMeasurement {
  assertFinitePrice('LEG1_START_PRICE', input.leg1StartPrice);
  assertFinitePrice('LEG1_END_PRICE', input.leg1EndPrice);
  assertFinitePrice('LEG2_START_PRICE', input.leg2StartPrice);
  assertFinitePrice('LEG2_END_PRICE', input.leg2EndPrice);

  const leg1Magnitude = Math.abs(input.leg1EndPrice - input.leg1StartPrice);
  const leg2Magnitude = Math.abs(input.leg2EndPrice - input.leg2StartPrice);

  if (leg1Magnitude === 0) {
    return {
      leg1Magnitude,
      leg2Magnitude,
      leg2ToLeg1Ratio: null,
      equalityRelation: 'UNDETERMINED',
      equalityTolerance: null,
    };
  }

  return {
    leg1Magnitude,
    leg2Magnitude,
    leg2ToLeg1Ratio: leg2Magnitude / leg1Magnitude,
    equalityRelation: leg2Magnitude === leg1Magnitude
      ? 'APPROXIMATELY_EQUAL_CANDIDATE'
      : 'NOT_EQUAL_CANDIDATE',
    equalityTolerance: null,
  };
}
