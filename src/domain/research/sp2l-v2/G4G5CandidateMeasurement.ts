/**
 * G4/G5 candidate measurement helper (research-only).
 *
 * Measures Leg 1 magnitude for each G4 endpoint family and Leg 2 magnitude
 * for each G5 origin candidate on a given synthetic fixture chart. This tool
 * deliberately NEVER selects a canonical family or candidate: it reports all
 * alternatives side by side so the source-visual evidence (once extracted)
 * can identify the correct one. No historical performance is used anywhere.
 *
 * Guardrails enforced here (from Phases 34-37):
 * - fail closed when a required anchor is missing (ANCHOR_MISSING_*);
 * - reject a Leg 2 origin placed before the correction begins;
 * - PENDING_LIMIT and ACTUAL_FILL are execution concepts and are excluded
 *   from canonical C candidates;
 * - non-finite candle geometry throws instead of silently measuring;
 * - no Leg 2 equality tolerance is fitted (G6 remains separate).
 */

import { anchorByConcept, anchorErrorCode, type FixtureAnchorPoint, type G4G5FixtureChart } from './G4G5DiscriminatingFixtures.js';

export type G4EndpointFamily =
  | 'STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME'
  | 'BREAKOUT_LEVEL_TO_SPIKE_EXTREME'
  | 'SPIKE_START_TO_SPIKE_END'
  | 'RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME'
  | 'STRUCTURAL_POINT_TO_STRUCTURAL_POINT';

export type G5OriginCandidate =
  | 'CORRECTION_EXTREME'
  | 'STRUCTURAL_HL_LH'
  | 'PENDING_LIMIT'
  | 'ACTUAL_FILL'
  | 'OTHER_VISUAL_POINT';

export const G4_ENDPOINT_FAMILIES: readonly G4EndpointFamily[] = [
  'STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME',
  'BREAKOUT_LEVEL_TO_SPIKE_EXTREME',
  'SPIKE_START_TO_SPIKE_END',
  'RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME',
  'STRUCTURAL_POINT_TO_STRUCTURAL_POINT',
];

export const G5_ORIGIN_CANDIDATES: readonly G5OriginCandidate[] = [
  'CORRECTION_EXTREME',
  'STRUCTURAL_HL_LH',
  'OTHER_VISUAL_POINT',
  'PENDING_LIMIT',
  'ACTUAL_FILL',
];

export const NON_CANONICAL_G5_CANDIDATES: readonly G5OriginCandidate[] = [
  'PENDING_LIMIT',
  'ACTUAL_FILL',
];

const G4_ANCHOR_MAP: Record<G4EndpointFamily, { start: string; end: string }> = {
  STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME: { start: 'firstStructuralLow', end: 'spikeExtreme' },
  BREAKOUT_LEVEL_TO_SPIKE_EXTREME: { start: 'breakoutLevel', end: 'spikeExtreme' },
  SPIKE_START_TO_SPIKE_END: { start: 'spikeStart', end: 'spikeExtreme' },
  RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME: { start: 'relevantCandleOpen', end: 'spikeExtreme' },
  STRUCTURAL_POINT_TO_STRUCTURAL_POINT: { start: 'teacherPointA', end: 'teacherPointB' },
};

const G5_ANCHOR_MAP: Record<G5OriginCandidate, string> = {
  CORRECTION_EXTREME: 'correctionExtreme',
  STRUCTURAL_HL_LH: 'structuralHL',
  OTHER_VISUAL_POINT: 'otherVisualPoint',
  PENDING_LIMIT: 'pendingLimit',
  ACTUAL_FILL: 'fill',
};

export interface Leg1CandidateMeasurement {
  family: G4EndpointFamily;
  start: FixtureAnchorPoint;
  end: FixtureAnchorPoint;
  magnitude: number;
}

export interface Leg2CandidateMeasurement {
  candidate: G5OriginCandidate;
  canonicalStatus: 'ALIVE' | 'EXCLUDED_NON_CANONICAL';
  origin: FixtureAnchorPoint;
  magnitude: number;
}

export interface G4G5CandidateReport {
  chartId: string;
  direction: 'BULLISH' | 'BEARISH';
  leg1Candidates: Leg1CandidateMeasurement[];
  leg2Candidates: Leg2CandidateMeasurement[];
  canonicalSelection: null;
  notes: string[];
}

function assertFiniteChart(chart: G4G5FixtureChart): void {
  for (const c of chart.candles) {
    if (!Number.isFinite(c.open) || !Number.isFinite(c.high) || !Number.isFinite(c.low) || !Number.isFinite(c.close)) {
      throw new Error('CANDLE_GEOMETRY_MUST_BE_FINITE');
    }
  }
}

export function resolveG4Anchors(
  chart: G4G5FixtureChart,
  family: G4EndpointFamily,
): { start: FixtureAnchorPoint; end: FixtureAnchorPoint } {
  assertFiniteChart(chart);
  const { start, end } = G4_ANCHOR_MAP[family];
  return { start: anchorByConcept(chart, start), end: anchorByConcept(chart, end) };
}

/** Leg 1 magnitude for one G4 endpoint family. */
export function measureLeg1(chart: G4G5FixtureChart, family: G4EndpointFamily): number {
  const { start, end } = resolveG4Anchors(chart, family);
  return Math.abs(end.price - start.price);
}

/** Leg 2 magnitude for one G5 origin candidate (Leg 2 end from chart.leg2End). */
export function measureLeg2(chart: G4G5FixtureChart, candidate: G5OriginCandidate): number {
  assertFiniteChart(chart);
  const origin = anchorByConcept(chart, G5_ANCHOR_MAP[candidate]);
  if (origin.index < chart.correctionStartIndex) {
    throw new Error('LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION');
  }
  const leg2End = anchorByConcept(chart, 'leg2End');
  if (leg2End.index <= chart.correctionStartIndex) {
    throw new Error('LEG2_END_MUST_FOLLOW_CORRECTION');
  }
  return Math.abs(leg2End.price - origin.price);
}

/** Explicit segment magnitude for scoped measurements (e.g. parent vs nested). */
export function measureExplicitSegment(startPrice: number, endPrice: number): number {
  if (!Number.isFinite(startPrice) || !Number.isFinite(endPrice)) {
    throw new Error('SEGMENT_PRICE_MUST_BE_FINITE');
  }
  return Math.abs(endPrice - startPrice);
}

/**
 * Structural eligibility audit of a fixture. Returns reasons without
 * selecting anything; throws only for non-finite candle geometry.
 */
export function assessFixture(chart: G4G5FixtureChart): { eligible: boolean; reasons: string[] } {
  assertFiniteChart(chart);
  const reasons: string[] = [];

  if (!chart.rangePresent) {
    reasons.push('SPIKE_REQUIRES_CONTEXT_RANGE');
  }

  for (const concept of ['breakoutLevel', 'spikeExtreme', 'firstStructuralLow'] as const) {
    if (!chart.anchors.some((a) => a.concept === concept)) {
      reasons.push(`ANCHOR_MISSING_${anchorErrorCode(concept)}`);
    }
  }

  const structuralLow = chart.anchors.find((a) => a.concept === 'firstStructuralLow');
  if (structuralLow && chart.correctionStartIndex <= structuralLow.index) {
    reasons.push('CORRECTION_MUST_BEGIN_AFTER_STRUCTURAL_REFERENCE');
  }

  const leg2End = chart.anchors.find((a) => a.concept === 'leg2End');
  if (!leg2End) {
    reasons.push('ANCHOR_MISSING_LEG2_END');
  } else if (leg2End.index <= chart.correctionStartIndex) {
    reasons.push('LEG2_END_MUST_FOLLOW_CORRECTION');
  }

  return { eligible: reasons.length === 0, reasons };
}

/**
 * Side-by-side report of every G4 family and every G5 candidate without
 * selecting a canonical one. PENDING_LIMIT and ACTUAL_FILL are reported but
 * marked EXCLUDED_NON_CANONICAL (Phase 36/37 identity separation).
 */
export function reportCandidates(chart: G4G5FixtureChart): G4G5CandidateReport {
  const leg1Candidates: Leg1CandidateMeasurement[] = G4_ENDPOINT_FAMILIES.map((family) => {
    const { start, end } = resolveG4Anchors(chart, family);
    return { family, start, end, magnitude: Math.abs(end.price - start.price) };
  });

  const leg2Candidates: Leg2CandidateMeasurement[] = G5_ORIGIN_CANDIDATES.map((candidate) => {
    const origin = anchorByConcept(chart, G5_ANCHOR_MAP[candidate]);
    if (origin.index < chart.correctionStartIndex) {
      throw new Error('LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION');
    }
    const leg2End = anchorByConcept(chart, 'leg2End');
    return {
      candidate,
      canonicalStatus: NON_CANONICAL_G5_CANDIDATES.includes(candidate) ? 'EXCLUDED_NON_CANONICAL' : 'ALIVE',
      origin,
      magnitude: Math.abs(leg2End.price - origin.price),
    };
  });

  return {
    chartId: chart.id,
    direction: chart.direction,
    leg1Candidates,
    leg2Candidates,
    canonicalSelection: null,
    notes: [
      'No canonical G4/G5 selection is made by this tool; source-visual evidence decides.',
      'PENDING_LIMIT and ACTUAL_FILL are execution concepts and are excluded from canonical C candidates.',
      'No Leg 2 equality tolerance is fitted; G6 remains separate.',
    ],
  };
}