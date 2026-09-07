/**
 * G4/G5 source-extraction provenance schema + input layer (research-only).
 *
 * Stores the chart coordinates extracted from the Poorsamadi SP2L video
 * (see docs/research/G4_G5_VISUAL_FRAME_REQUEST_2026-09-07.md) as a
 * JSON-serializable record with provenance: point ID, video time, chart
 * candle timestamp, price, OHLC element, chart timeframe and direction.
 *
 * The record is the input layer for the Phase 38 measurement helpers:
 * `extractionToChart` builds a `G4G5FixtureChart` whose labeled anchors come
 * from the extracted points, and `reportExtractionCandidates` runs the G4/G5
 * measurements on it, reporting MISSING_EVIDENCE instead of failing closed
 * when a segment simply did not expose a particular anchor.
 *
 * UNREADABLE points (price null) are preserved for provenance but excluded
 * from measurement.
 */

import {
  type G4G5FixtureChart,
  type OhlcElement,
} from './G4G5DiscriminatingFixtures.js';
import {
  G4_ENDPOINT_FAMILIES,
  G5_ORIGIN_CANDIDATES,
  NON_CANONICAL_G5_CANDIDATES,
  measureLeg1,
  measureLeg2,
  type G4EndpointFamily,
  type G5OriginCandidate,
} from './G4G5CandidateMeasurement.js';

export type SourceSegment = 'SEGMENT_1' | 'SEGMENT_2' | 'SEGMENT_3';
export type SourcePointGate = 'G1' | 'G2' | 'G4' | 'G5' | 'G6' | 'NESTED_LEG';
export type PointCategory =
  | 'LEG1_START'
  | 'LEG1_END'
  | 'CORRECTION'
  | 'LEG2_END'
  | 'EXECUTION'
  | 'STRUCTURAL_SEQUENCE';
export type ExtractionOhlcElement = OhlcElement | 'UNREADABLE';
export type ExtractionTimeframe = 'M1' | 'M5' | 'UNKNOWN';
export type ExtractionDirection = 'BUY' | 'SELL' | 'UNKNOWN';

export interface SourcePointSpec {
  pointId: string;
  segment: SourceSegment;
  category: PointCategory;
  gate: SourcePointGate;
  purpose: string;
  /** Measurement anchor concept this point feeds (null = sequence evidence only). */
  anchorConcept: string | null;
  /** Expected count for multi-point sequence evidence (e.g. S2-1 = 4 lower highs). */
  sequenceSize: number | null;
}

export const G4G5_SOURCE_POINT_REGISTRY: readonly SourcePointSpec[] = [
  // Segment 1 — 36:59-37:08 (spike -> correction -> Leg 2 equality)
  { pointId: 'S1-A', segment: 'SEGMENT_1', category: 'LEG1_START', gate: 'G4', purpose: 'Leg 1 start (teacher point)', anchorConcept: 'teacherPointA', sequenceSize: null },
  { pointId: 'S1-B', segment: 'SEGMENT_1', category: 'LEG1_END', gate: 'G4', purpose: 'Leg 1 end (spike extreme?)', anchorConcept: 'teacherPointB', sequenceSize: null },
  { pointId: 'S1-C', segment: 'SEGMENT_1', category: 'CORRECTION', gate: 'G5', purpose: 'Correction extreme', anchorConcept: 'correctionExtreme', sequenceSize: null },
  { pointId: 'S1-D', segment: 'SEGMENT_1', category: 'LEG2_END', gate: 'G6', purpose: 'Leg 2 completion / target', anchorConcept: 'leg2End', sequenceSize: null },

  // Segment 2 — 1:02:41-1:03:32 (outer leg vs nested leg; deep correction)
  { pointId: 'S2-1', segment: 'SEGMENT_2', category: 'STRUCTURAL_SEQUENCE', gate: 'G1', purpose: 'Four lower-high points', anchorConcept: null, sequenceSize: 4 },
  { pointId: 'S2-2', segment: 'SEGMENT_2', category: 'LEG1_START', gate: 'G4', purpose: 'Parent Leg 1 start', anchorConcept: 'teacherPointA', sequenceSize: null },
  { pointId: 'S2-3', segment: 'SEGMENT_2', category: 'LEG1_END', gate: 'G4', purpose: 'Parent Leg 1 end', anchorConcept: 'teacherPointB', sequenceSize: null },
  { pointId: 'S2-4', segment: 'SEGMENT_2', category: 'CORRECTION', gate: 'G5', purpose: '"از اینجا" Leg 2 start', anchorConcept: 'otherVisualPoint', sequenceSize: null },
  { pointId: 'S2-5', segment: 'SEGMENT_2', category: 'CORRECTION', gate: 'G5', purpose: 'Deep-correction origin', anchorConcept: 'correctionExtreme', sequenceSize: null },
  { pointId: 'S2-6', segment: 'SEGMENT_2', category: 'LEG2_END', gate: 'G6', purpose: 'Parent Leg 2 end', anchorConcept: 'leg2End', sequenceSize: null },
  { pointId: 'S2-7', segment: 'SEGMENT_2', category: 'LEG2_END', gate: 'NESTED_LEG', purpose: 'Nested 2Leg TP', anchorConcept: null, sequenceSize: null },

  // Segment 3 — 1:04:00-1:04:32 (deep leg, order placement, Leg 1, TP1)
  { pointId: 'S3-A', segment: 'SEGMENT_3', category: 'CORRECTION', gate: 'G5', purpose: 'Deep leg start (decisive C)', anchorConcept: 'otherVisualPoint', sequenceSize: null },
  { pointId: 'S3-1', segment: 'SEGMENT_3', category: 'STRUCTURAL_SEQUENCE', gate: 'G1', purpose: 'Seven lower-high points', anchorConcept: null, sequenceSize: 7 },
  { pointId: 'S3-B', segment: 'SEGMENT_3', category: 'LEG1_START', gate: 'G4', purpose: 'Leg 1 start', anchorConcept: 'teacherPointA', sequenceSize: null },
  { pointId: 'S3-C', segment: 'SEGMENT_3', category: 'LEG1_END', gate: 'G4', purpose: 'Leg 1 end', anchorConcept: 'teacherPointB', sequenceSize: null },
  { pointId: 'S3-D', segment: 'SEGMENT_3', category: 'EXECUTION', gate: 'G2', purpose: 'Pending-limit placement', anchorConcept: 'pendingLimit', sequenceSize: null },
  { pointId: 'S3-E', segment: 'SEGMENT_3', category: 'EXECUTION', gate: 'G2', purpose: 'Activation level', anchorConcept: 'fill', sequenceSize: null },
  { pointId: 'S3-F', segment: 'SEGMENT_3', category: 'LEG2_END', gate: 'G6', purpose: 'TP1', anchorConcept: 'leg2End', sequenceSize: null },
];

export interface ExtractedSourcePoint {
  pointId: string;
  videoTime: string;
  candleTimestamp: string | null;
  price: number | null;
  ohlcElement: ExtractionOhlcElement;
  chartTimeframe: ExtractionTimeframe;
  direction: ExtractionDirection;
  notes: string | null;
}

export interface G4G5SourceExtraction {
  schemaVersion: 1;
  video: { url: string; lesson: string };
  points: ExtractedSourcePoint[];
}

export const G4G5_EXTRACTION_SCHEMA_VERSION = 1;

const SEGMENT_ORDER: Record<SourceSegment, number> = { SEGMENT_1: 0, SEGMENT_2: 1, SEGMENT_3: 2 };
const ALLOWED_OHLC_ELEMENTS: readonly ExtractionOhlcElement[] = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'LEVEL', 'UNREADABLE'];
const ALLOWED_TIMEFRAMES: readonly ExtractionTimeframe[] = ['M1', 'M5', 'UNKNOWN'];
const ALLOWED_DIRECTIONS: readonly ExtractionDirection[] = ['BUY', 'SELL', 'UNKNOWN'];
const VIDEO_TIME_PATTERN = /^\d{1,2}:\d{2}(:\d{2})?$/;

const REGISTRY_BY_ID = new Map(G4G5_SOURCE_POINT_REGISTRY.map((s) => [s.pointId, s]));

export function validateExtraction(extraction: G4G5SourceExtraction): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (extraction.schemaVersion !== G4G5_EXTRACTION_SCHEMA_VERSION) {
    errors.push('EXTRACTION_SCHEMA_VERSION_MUST_BE_1');
  }
  if (typeof extraction.video?.url !== 'string' || extraction.video.url.length === 0) {
    errors.push('EXTRACTION_VIDEO_URL_REQUIRED');
  }
  if (!Array.isArray(extraction.points) || extraction.points.length === 0) {
    errors.push('EXTRACTION_POINTS_REQUIRED');
    return { valid: false, errors };
  }

  for (const p of extraction.points) {
    const tag = `:${p.pointId}`;
    const spec = REGISTRY_BY_ID.get(p.pointId);
    if (!spec) {
      errors.push(`EXTRACTION_UNKNOWN_POINT_ID${tag}`);
      continue;
    }
    if (typeof p.videoTime !== 'string' || !VIDEO_TIME_PATTERN.test(p.videoTime)) {
      errors.push(`EXTRACTION_INVALID_VIDEO_TIME${tag}`);
    }
    if (p.price !== null && !Number.isFinite(p.price)) {
      errors.push(`EXTRACTION_INVALID_PRICE${tag}`);
    }
    if (p.price !== null && p.ohlcElement === 'UNREADABLE') {
      errors.push(`EXTRACTION_UNREADABLE_WITH_PRICE${tag}`);
    }
    if (!ALLOWED_OHLC_ELEMENTS.includes(p.ohlcElement)) {
      errors.push(`EXTRACTION_INVALID_OHLC_ELEMENT${tag}`);
    }
    if (!ALLOWED_TIMEFRAMES.includes(p.chartTimeframe)) {
      errors.push(`EXTRACTION_INVALID_TIMEFRAME${tag}`);
    }
    if (!ALLOWED_DIRECTIONS.includes(p.direction)) {
      errors.push(`EXTRACTION_INVALID_DIRECTION${tag}`);
    }
  }

  return { valid: errors.length === 0, errors };
}

export function assertValidExtraction(extraction: G4G5SourceExtraction): void {
  const { valid, errors } = validateExtraction(extraction);
  if (!valid) {
    throw new Error(errors[0] ?? 'EXTRACTION_INVALID');
  }
}

export function pointsForSegment(
  extraction: G4G5SourceExtraction,
  segment: SourceSegment,
): ExtractedSourcePoint[] {
  return extraction.points.filter((p) => REGISTRY_BY_ID.get(p.pointId)?.segment === segment);
}

export function unreadablePointIds(
  extraction: G4G5SourceExtraction,
  segment: SourceSegment,
): string[] {
  return pointsForSegment(extraction, segment)
    .filter((p) => p.price === null)
    .map((p) => p.pointId);
}

/**
 * Builds a measurement-ready chart from a validated extraction segment.
 * Anchors come only from readable points; indices are the deterministic
 * registry/video-time order within the segment. `correctionStartIndex` is the
 * first CORRECTION-category anchor, or 0 if the segment has none.
 */
export function extractionToChart(
  extraction: G4G5SourceExtraction,
  segment: SourceSegment,
): G4G5FixtureChart {
  assertValidExtraction(extraction);

  const segmentPoints = pointsForSegment(extraction, segment);
  const readable = segmentPoints
    .filter((p) => p.price !== null)
    .sort((a, b) => {
      const sa = REGISTRY_BY_ID.get(a.pointId)!;
      const sb = REGISTRY_BY_ID.get(b.pointId)!;
      const bySegment = SEGMENT_ORDER[sa.segment] - SEGMENT_ORDER[sb.segment];
      if (bySegment !== 0) return bySegment;
      const byTime = a.videoTime.localeCompare(b.videoTime);
      if (byTime !== 0) return byTime;
      return sa.pointId.localeCompare(sb.pointId);
    });

  const anchors = readable.flatMap((p, index) => {
    const concept = REGISTRY_BY_ID.get(p.pointId)!.anchorConcept;
    if (concept === null) return [];
    return [{
      index,
      price: p.price as number,
      element: p.ohlcElement as OhlcElement,
      concept,
    }];
  });

  const correctionAnchors = readable
    .map((p, index) => ({ p, index }))
    .filter(({ p }) => REGISTRY_BY_ID.get(p.pointId)!.category === 'CORRECTION');
  const correctionStartIndex = correctionAnchors.length > 0 ? correctionAnchors[0]!.index : 0;

  return {
    id: `EXTRACTION_${segment}`,
    direction: segmentDirection(readable),
    candles: [],
    anchors,
    correctionStartIndex,
    rangePresent: true,
  };
}

export function segmentDirection(points: readonly ExtractedSourcePoint[]): 'BULLISH' | 'BEARISH' {
  const known = points.find((p) => p.direction === 'BUY' || p.direction === 'SELL');
  return known?.direction === 'SELL' ? 'BEARISH' : 'BULLISH';
}

export interface ExtractionCandidateResult {
  id: string;
  magnitude: number | null;
  status: 'MEASURED' | 'MISSING_EVIDENCE' | 'INVALID_ORDER';
  detail: string | null;
}

export interface ExtractionCandidateReport {
  segment: SourceSegment;
  direction: 'BULLISH' | 'BEARISH';
  unreadablePointIds: string[];
  leg1: ExtractionCandidateResult[];
  leg2: ExtractionCandidateResult[];
  notes: string[];
}

function runCandidate(
  id: string,
  measure: () => number,
): ExtractionCandidateResult {
  try {
    return { id, magnitude: measure(), status: 'MEASURED', detail: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'UNKNOWN_ERROR';
    if (message.startsWith('ANCHOR_MISSING_')) {
      return { id, magnitude: null, status: 'MISSING_EVIDENCE', detail: message };
    }
    return { id, magnitude: null, status: 'INVALID_ORDER', detail: message };
  }
}

/**
 * Runs the Phase 38 G4/G5 measurements on one extraction segment and reports
 * every family/candidate with its status. Missing anchors in a segment are
 * normal (e.g. Segment 3 exposes no correction extreme) and are reported as
 * MISSING_EVIDENCE rather than errors.
 */
export function reportExtractionCandidates(
  extraction: G4G5SourceExtraction,
  segment: SourceSegment,
): ExtractionCandidateReport {
  const chart = extractionToChart(extraction, segment);
  const unreadable = unreadablePointIds(extraction, segment);

  const leg1: ExtractionCandidateResult[] = G4_ENDPOINT_FAMILIES.map((family: G4EndpointFamily) =>
    runCandidate(family, () => measureLeg1(chart, family)),
  );

  const leg2: ExtractionCandidateResult[] = G5_ORIGIN_CANDIDATES.map((candidate: G5OriginCandidate) =>
    runCandidate(candidate, () => measureLeg2(chart, candidate)),
  );

  return {
    segment,
    direction: chart.direction,
    unreadablePointIds: unreadable,
    leg1,
    leg2,
    notes: [
      'No canonical G4/G5 selection is made by this tool; source-visual evidence decides.',
      'MISSING_EVIDENCE means the segment did not expose that anchor (or the point is UNREADABLE).',
      'PENDING_LIMIT and ACTUAL_FILL are execution concepts and are excluded from canonical C candidates.',
      'No Leg 2 equality tolerance is fitted; G6 remains separate.',
    ],
  };
}

/** Non-teacher anchors a user may supply from the frames for G4 discrimination. */
export type ExtraAnchorConcept =
  | 'spikeExtreme'
  | 'firstStructuralLow'
  | 'breakoutLevel'
  | 'relevantCandleOpen'
  | 'spikeStart';

export interface SourceFitItem<T extends string> {
  id: T;
  computed: number | null;
  /** true = exact match with the teacher's implied magnitude; null = cannot judge. */
  fit: boolean | null;
}

export interface SourceFitReport {
  segment: SourceSegment;
  /** |teacher Leg 1 end - teacher Leg 1 start| measured from the frames. */
  impliedLeg1: number | null;
  /** Teacher TP1 price (Leg 2 end) from the frames. */
  impliedTp1: number | null;
  g4: SourceFitItem<G4EndpointFamily>[];
  g5: Array<SourceFitItem<G5OriginCandidate> & { canonicalStatus: 'ALIVE' | 'EXCLUDED_NON_CANONICAL' }>;
  g4Identified: G4EndpointFamily | null;
  g5Identified: G5OriginCandidate | null;
  g4Ambiguous: boolean;
  g5Ambiguous: boolean;
  unresolvedReasons: string[];
}

/**
 * Source-fit checker: identifies which G4 family and which G5 candidate
 * reproduce the teacher's implied magnitudes on a filled extraction record.
 *
 * Teacher's implied Leg 1 = |S*-B end - S*-A start| (the segment the teacher
 * points to). Each G4 family is compared against that magnitude with exact
 * equality (no tolerance fitted). Each G5 candidate origin C is compared via
 * |TP1 - C| == impliedLeg1 (the source-established Leg2 ~= Leg1 relationship
 * tested at exact equality only). PENDING_LIMIT and ACTUAL_FILL can never be
 * identified as canonical C.
 *
 * `extraAnchors` accepts non-teacher structural points (spike extreme,
 * breakout level, ...) when they are visible in the frames, so the non-teacher
 * G4 families can actually be computed and discriminated.
 */
export function checkSourceFit(
  extraction: G4G5SourceExtraction,
  segment: SourceSegment,
  extraAnchors: Partial<Record<ExtraAnchorConcept, number>> = {},
): SourceFitReport {
  const chart = extractionToChart(extraction, segment);
  const unresolvedReasons: string[] = [];

  const teacherA = chart.anchors.find((a) => a.concept === 'teacherPointA');
  const teacherB = chart.anchors.find((a) => a.concept === 'teacherPointB');
  const leg2End = chart.anchors.find((a) => a.concept === 'leg2End');

  if (!teacherA || !teacherB) unresolvedReasons.push('TEACHER_LEG1_NOT_EXTRACTED');
  if (!leg2End) unresolvedReasons.push('TP1_NOT_EXTRACTED');

  const impliedLeg1 = teacherA && teacherB ? Math.abs(teacherB.price - teacherA.price) : null;
  const impliedTp1 = leg2End?.price ?? null;

  const anchors = [...chart.anchors];
  let extraIndex = 100;
  for (const [concept, price] of Object.entries(extraAnchors) as [ExtraAnchorConcept, number][]) {
    if (Number.isFinite(price)) {
      anchors.push({ index: extraIndex++, price, element: 'LEVEL', concept });
    }
  }
  const chartWithExtras: G4G5FixtureChart = { ...chart, anchors };

  const g4: SourceFitReport['g4'] = G4_ENDPOINT_FAMILIES.map((family) => {
    try {
      const computed = measureLeg1(chartWithExtras, family);
      return { id: family, computed, fit: impliedLeg1 !== null ? computed === impliedLeg1 : null };
    } catch {
      return { id: family, computed: null, fit: null };
    }
  });

  const g5: SourceFitReport['g5'] = G5_ORIGIN_CANDIDATES.map((candidate) => {
    try {
      const computed = measureLeg2(chartWithExtras, candidate);
      return {
        id: candidate,
        canonicalStatus: NON_CANONICAL_G5_CANDIDATES.includes(candidate) ? 'EXCLUDED_NON_CANONICAL' : 'ALIVE',
        computed,
        fit: impliedLeg1 !== null ? computed === impliedLeg1 : null,
      };
    } catch {
      return {
        id: candidate,
        canonicalStatus: NON_CANONICAL_G5_CANDIDATES.includes(candidate) ? 'EXCLUDED_NON_CANONICAL' : 'ALIVE',
        computed: null,
        fit: null,
      };
    }
  });

  const g4Fits = g4.filter((r) => r.fit === true);
  const g5AliveFits = g5.filter((r) => r.fit === true && r.canonicalStatus === 'ALIVE');

  return {
    segment,
    impliedLeg1,
    impliedTp1,
    g4,
    g5,
    g4Identified: g4Fits.length === 1 ? g4Fits[0]!.id : null,
    g5Identified: g5AliveFits.length === 1 ? g5AliveFits[0]!.id : null,
    g4Ambiguous: g4Fits.length > 1,
    g5Ambiguous: g5AliveFits.length > 1,
    unresolvedReasons,
  };
}

export interface AllSegmentsSourceFitReport {
  segments: Partial<Record<SourceSegment, SourceFitReport>>;
}

/** Runs the source-fit checker over all three source segments. */
export function checkAllSegmentsSourceFit(
  extraction: G4G5SourceExtraction,
  extraAnchors: Partial<Record<ExtraAnchorConcept, number>> = {},
): AllSegmentsSourceFitReport {
  return {
    segments: {
      SEGMENT_1: checkSourceFit(extraction, 'SEGMENT_1', extraAnchors),
      SEGMENT_2: checkSourceFit(extraction, 'SEGMENT_2', extraAnchors),
      SEGMENT_3: checkSourceFit(extraction, 'SEGMENT_3', extraAnchors),
    },
  };
}

/** Blank fill-in template matching the frame-request delivery sheet. */
export const G4G5_EXTRACTION_TEMPLATE: G4G5SourceExtraction = {
  schemaVersion: 1,
  video: { url: 'https://youtu.be/7HEC5mO3d3U', lesson: 'SP2L' },
  points: G4G5_SOURCE_POINT_REGISTRY.map((spec) => ({
    pointId: spec.pointId,
    videoTime: spec.segment === 'SEGMENT_1' ? '37:00' : spec.segment === 'SEGMENT_2' ? '1:03:00' : '1:04:00',
    candleTimestamp: null,
    price: null,
    ohlcElement: 'UNREADABLE',
    chartTimeframe: 'UNKNOWN',
    direction: 'UNKNOWN',
    notes: null,
  })),
};