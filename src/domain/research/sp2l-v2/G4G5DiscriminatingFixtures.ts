/**
 * G4/G5 discriminating synthetic fixtures (research-only).
 *
 * These charts are deliberately synthetic. They contain NO XAUUSD historical
 * data and NO source measurements. Their only purpose is to prove that the
 * candidate measurement machinery can distinguish the G4 Leg1 endpoint
 * families and the G5 Leg2 origin candidates on the same chart, so that the
 * same machinery can later be trusted with source-extracted coordinates.
 *
 * Every fixture labels its structural points explicitly (anchors). The
 * fixtures do not select a canonical family or candidate; they only make the
 * alternatives measurable and distinct.
 */

export type FixtureDirection = 'BULLISH' | 'BEARISH';

export interface FixtureCandle {
  index: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export type OhlcElement = 'OPEN' | 'HIGH' | 'LOW' | 'CLOSE' | 'LEVEL';

export interface FixtureAnchorPoint {
  index: number;
  price: number;
  element: OhlcElement;
  concept: string;
}

export interface G4G5FixtureChart {
  id: string;
  direction: FixtureDirection;
  candles: FixtureCandle[];
  anchors: FixtureAnchorPoint[];
  correctionStartIndex: number;
  rangePresent: boolean;
}

/**
 * Deterministic mirror transform. Bearish candle i mirrors bullish candle i
 * around `mirrorPrice` with HIGH/LOW swapped so the OHLC geometry stays valid.
 * Anchor prices are mirrored the same way; LEVEL anchors keep their element.
 */
export function mirrorChart(chart: G4G5FixtureChart, mirrorPrice: number): G4G5FixtureChart {
  const mirror = (p: number): number => 2 * mirrorPrice - p;
  const elementMirror: Record<OhlcElement, OhlcElement> = {
    OPEN: 'OPEN',
    CLOSE: 'CLOSE',
    HIGH: 'LOW',
    LOW: 'HIGH',
    LEVEL: 'LEVEL',
  };

  return {
    id: `${chart.id}_BEAR_MIRROR`,
    direction: 'BEARISH',
    rangePresent: chart.rangePresent,
    correctionStartIndex: chart.correctionStartIndex,
    candles: chart.candles.map((c) => ({
      index: c.index,
      open: mirror(c.open),
      high: mirror(c.low),
      low: mirror(c.high),
      close: mirror(c.close),
    })),
    anchors: chart.anchors.map((a) => ({
      index: a.index,
      price: mirror(a.price),
      element: elementMirror[a.element],
      concept: a.concept,
    })),
  };
}

/** Returns a shallow copy of the chart with one anchor replaced (test helper). */
export function withAnchor(
  chart: G4G5FixtureChart,
  concept: string,
  anchor: FixtureAnchorPoint,
): G4G5FixtureChart {
  return {
    ...chart,
    anchors: chart.anchors.map((a) => (a.concept === concept ? anchor : a)),
  };
}

/** Returns a shallow copy of the chart with one anchor removed (test helper). */
export function withoutAnchor(chart: G4G5FixtureChart, concept: string): G4G5FixtureChart {
  return {
    ...chart,
    anchors: chart.anchors.filter((a) => a.concept !== concept),
  };
}

/** Converts a camelCase concept name into an UPPER_SNAKE error code. */
export function anchorErrorCode(concept: string): string {
  return concept.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toUpperCase();
}

export function anchorByConcept(chart: G4G5FixtureChart, concept: string): FixtureAnchorPoint {
  const found = chart.anchors.find((a) => a.concept === concept);
  if (!found) {
    throw new Error(`ANCHOR_MISSING_${anchorErrorCode(concept)}`);
  }
  return found;
}

/**
 * FIXTURE 1 — BULLISH FOUR-ANCHOR DISCRIMINATOR.
 *
 * Structure: range (0-4) -> breakout (5) -> FT (6) -> spike (7-8) ->
 * correction (9-12, pending BUY LIMIT at 2500, fill intrabar at index 11,
 * correction extreme low 2498) -> Leg 2 (13-14).
 *
 * The five G4 endpoint families and the G5 origin candidates all resolve to
 * different anchors and therefore produce different magnitudes on this single
 * chart (see EXPECTED_BULL_G4_MAGNITUDES / EXPECTED_BULL_G5_MAGNITUDES).
 */
export const BULL_FOUR_ANCHOR_FIXTURE: G4G5FixtureChart = {
  id: 'G4G5_FIXTURE_BULL_FOUR_ANCHOR',
  direction: 'BULLISH',
  rangePresent: true,
  correctionStartIndex: 9,
  candles: [
    { index: 0, open: 2495, high: 2500, low: 2494, close: 2498 },
    { index: 1, open: 2498, high: 2500, low: 2496, close: 2499 },
    { index: 2, open: 2499, high: 2501, low: 2497, close: 2500 },
    { index: 3, open: 2500, high: 2501, low: 2498, close: 2499 },
    { index: 4, open: 2499, high: 2502, low: 2498, close: 2500 },
    { index: 5, open: 2500, high: 2503, low: 2497, close: 2502 },
    { index: 6, open: 2502, high: 2506, low: 2501, close: 2505 },
    { index: 7, open: 2505, high: 2512, low: 2504, close: 2510 },
    { index: 8, open: 2510, high: 2518, low: 2509, close: 2517 },
    { index: 9, open: 2516, high: 2517, low: 2508, close: 2510 },
    { index: 10, open: 2510, high: 2512, low: 2502, close: 2506 },
    { index: 11, open: 2506, high: 2508, low: 2498, close: 2503 },
    { index: 12, open: 2503, high: 2507, low: 2501, close: 2505 },
    { index: 13, open: 2505, high: 2513, low: 2504, close: 2511 },
    { index: 14, open: 2511, high: 2519, low: 2510, close: 2518 },
  ],
  anchors: [
    { index: 4, price: 2500, element: 'LEVEL', concept: 'breakoutLevel' },
    { index: 5, price: 2497, element: 'LOW', concept: 'firstStructuralLow' },
    { index: 7, price: 2504, element: 'LOW', concept: 'spikeStart' },
    { index: 7, price: 2505, element: 'OPEN', concept: 'spikeStartOpen' },
    { index: 8, price: 2518, element: 'HIGH', concept: 'spikeExtreme' },
    { index: 8, price: 2510, element: 'OPEN', concept: 'relevantCandleOpen' },
    { index: 12, price: 2501, element: 'LOW', concept: 'teacherPointA' },
    { index: 8, price: 2518, element: 'HIGH', concept: 'teacherPointB' },
    { index: 11, price: 2498, element: 'LOW', concept: 'correctionExtreme' },
    { index: 12, price: 2501, element: 'LOW', concept: 'structuralHL' },
    { index: 9, price: 2500, element: 'LEVEL', concept: 'pendingLimit' },
    { index: 11, price: 2500, element: 'LEVEL', concept: 'fill' },
    { index: 12, price: 2502, element: 'LEVEL', concept: 'otherVisualPoint' },
    { index: 14, price: 2519, element: 'HIGH', concept: 'leg2End' },
  ],
};

/** Hand-computed expected Leg 1 magnitudes for the bullish fixture. */
export const EXPECTED_BULL_G4_MAGNITUDES = {
  STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME: 21, // |2518 - 2497|
  BREAKOUT_LEVEL_TO_SPIKE_EXTREME: 18, // |2518 - 2500|
  SPIKE_START_TO_SPIKE_END: 14, // |2518 - 2504|
  RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME: 8, // |2518 - 2510|
  STRUCTURAL_POINT_TO_STRUCTURAL_POINT: 17, // |2518 - 2501|
} as const;

/** Hand-computed expected Leg 2 magnitudes (Leg 2 end = 2519) for the bullish fixture. */
export const EXPECTED_BULL_G5_MAGNITUDES = {
  CORRECTION_EXTREME: 21, // |2519 - 2498|
  STRUCTURAL_HL_LH: 18, // |2519 - 2501|
  OTHER_VISUAL_POINT: 17, // |2519 - 2502|
  PENDING_LIMIT: 19, // |2519 - 2500|
  ACTUAL_FILL: 19, // |2519 - 2500| (same price as pending; identity separation)
} as const;

export const BEAR_MIRROR_PRICE = 2559;
export const BEAR_MIRROR_FIXTURE = mirrorChart(BULL_FOUR_ANCHOR_FIXTURE, BEAR_MIRROR_PRICE);

/**
 * FIXTURE 2 — BEARISH NESTED-LEG DISCRIMINATOR (source-shaped after the
 * 1:02:41-1:03:32 worked example: an outer leg containing its own 2Leg).
 *
 * Parent Leg 1: 2700 -> 2630 (magnitude 70).
 * Nested 2Leg inside it: nested Leg 1 2700 -> 2667 (33), nested correction
 * extreme 2692, nested Leg 2 2692 -> 2659 (33), nested TP = 2659.
 * Parent deep correction extreme: 2658. Parent Leg 2: 2658 -> 2588 (70),
 * parent TP1 = 2588.
 *
 * Discriminates scope: parent magnitudes (70) differ from nested magnitudes
 * (33), and nested TP (2659) differs from parent TP1 (2588).
 */
export const NESTED_LEG_FIXTURE: G4G5FixtureChart = {
  id: 'G4G5_FIXTURE_BEAR_NESTED_LEG',
  direction: 'BEARISH',
  rangePresent: true,
  correctionStartIndex: 8,
  candles: [
    { index: 0, open: 2700, high: 2701, low: 2699, close: 2700 },
    { index: 1, open: 2700, high: 2702, low: 2698, close: 2701 },
    { index: 2, open: 2701, high: 2702, low: 2694, close: 2695 },
    { index: 3, open: 2695, high: 2696, low: 2686, close: 2688 },
    { index: 4, open: 2688, high: 2689, low: 2667, close: 2670 },
    { index: 5, open: 2670, high: 2692, low: 2669, close: 2688 },
    { index: 6, open: 2688, high: 2689, low: 2659, close: 2662 },
    { index: 7, open: 2662, high: 2663, low: 2630, close: 2632 },
    { index: 8, open: 2632, high: 2658, low: 2631, close: 2654 },
    { index: 9, open: 2654, high: 2655, low: 2642, close: 2644 },
    { index: 10, open: 2644, high: 2645, low: 2588, close: 2590 },
  ],
  anchors: [
    { index: 0, price: 2700, element: 'LEVEL', concept: 'parentA' },
    { index: 7, price: 2630, element: 'LOW', concept: 'parentB' },
    { index: 2, price: 2700, element: 'LEVEL', concept: 'nestedA' },
    { index: 4, price: 2667, element: 'LOW', concept: 'nestedB' },
    { index: 5, price: 2692, element: 'HIGH', concept: 'nestedCorrectionExtreme' },
    { index: 6, price: 2659, element: 'LOW', concept: 'nestedTP' },
    { index: 8, price: 2658, element: 'HIGH', concept: 'parentCorrectionExtreme' },
    { index: 10, price: 2588, element: 'LOW', concept: 'parentLeg2End' },
  ],
};

export const EXPECTED_NESTED_MAGNITUDES = {
  parentLeg1: 70, // |2630 - 2700|
  parentLeg2: 70, // |2588 - 2658|
  nestedLeg1: 33, // |2667 - 2700|
  nestedLeg2: 33, // |2659 - 2692|
} as const;

/**
 * NEGATIVE FIXTURE 1 — no preceding range. A sharp move without context:
 * the spike family must be ineligible (source S2: spike requires context).
 */
export const NEG_NO_RANGE_FIXTURE: G4G5FixtureChart = {
  id: 'G4G5_FIXTURE_NEG_NO_RANGE',
  direction: 'BULLISH',
  rangePresent: false,
  correctionStartIndex: 5,
  candles: [
    { index: 0, open: 2500, high: 2505, low: 2499, close: 2504 },
    { index: 1, open: 2504, high: 2510, low: 2503, close: 2509 },
    { index: 2, open: 2509, high: 2518, low: 2508, close: 2517 },
    { index: 3, open: 2516, high: 2517, low: 2508, close: 2510 },
    { index: 4, open: 2510, high: 2512, low: 2502, close: 2506 },
    { index: 5, open: 2506, high: 2508, low: 2498, close: 2503 },
    { index: 6, open: 2503, high: 2507, low: 2501, close: 2505 },
  ],
  anchors: [
    { index: 0, price: 2500, element: 'LEVEL', concept: 'breakoutLevel' },
    { index: 0, price: 2499, element: 'LOW', concept: 'firstStructuralLow' },
    { index: 2, price: 2518, element: 'HIGH', concept: 'spikeExtreme' },
    { index: 6, price: 2519, element: 'HIGH', concept: 'leg2End' },
  ],
};

/**
 * NEGATIVE FIXTURE 2 — missing structural reference. The chart has a spike
 * and a correction but no labeled first-structural-low anchor, so the
 * STRUCTURAL_LOW_HIGH family must fail closed with ANCHOR_MISSING_*.
 */
export const NEG_MISSING_STRUCTURAL_REFERENCE_FIXTURE: G4G5FixtureChart = withoutAnchor(
  BULL_FOUR_ANCHOR_FIXTURE,
  'firstStructuralLow',
);

/**
 * NEGATIVE FIXTURE 3 — C placed before the correction begins. The visual
 * point is moved to index 8 (before correctionStartIndex 9); the measurement
 * must reject with LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION.
 */
export const NEG_C_BEFORE_CORRECTION_FIXTURE: G4G5FixtureChart = withAnchor(
  BULL_FOUR_ANCHOR_FIXTURE,
  'otherVisualPoint',
  { index: 8, price: 2509, element: 'LOW', concept: 'otherVisualPoint' },
);

/**
 * NEGATIVE FIXTURE 4 — non-finite candle geometry. Must throw
 * CANDLE_GEOMETRY_MUST_BE_FINITE instead of silently measuring.
 */
export const NEG_NON_FINITE_FIXTURE: G4G5FixtureChart = {
  ...BULL_FOUR_ANCHOR_FIXTURE,
  id: 'G4G5_FIXTURE_NEG_NON_FINITE',
  candles: BULL_FOUR_ANCHOR_FIXTURE.candles.map((c) =>
    c.index === 8 ? { ...c, low: Number.NaN } : c,
  ),
};