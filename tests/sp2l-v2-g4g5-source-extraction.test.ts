import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import {
  G4G5_37_22_FRAME_EVIDENCE,
  G4G5_EXTRACTION_TEMPLATE,
  G4G5_SOURCE_POINT_REGISTRY,
  assertValidExtraction,
  checkAllSegmentsSourceFit,
  checkSourceFit,
  extractionToChart,
  pointsForSegment,
  reportExtractionCandidates,
  unreadablePointIds,
  validateExtraction,
  validateFrameEvidence,
  type ExtractedSourcePoint,
  type G4G5SourceExtraction,
  type SourceFrameEvidence,
} from '../src/domain/research/sp2l-v2/G4G5SourceExtraction.js';
import { measureLeg1, measureLeg2 } from '../src/domain/research/sp2l-v2/G4G5CandidateMeasurement.js';

function pt(
  pointId: string,
  price: number | null,
  overrides: Partial<ExtractedSourcePoint> = {},
): ExtractedSourcePoint {
  return {
    pointId,
    videoTime: '1:04:00',
    candleTimestamp: null,
    price,
    ohlcElement: price === null ? 'UNREADABLE' : 'LEVEL',
    chartTimeframe: 'M5',
    direction: 'BUY',
    notes: null,
    ...overrides,
  };
}

/** Segment 3 extraction with prices that mirror the bull fixture magnitudes. */
const SEGMENT_3_EXTRACTION: G4G5SourceExtraction = {
  schemaVersion: 1,
  video: { url: 'https://youtu.be/7HEC5mO3d3U', lesson: 'SP2L' },
  points: [
    pt('S3-A', 2502, { videoTime: '1:04:00', ohlcElement: 'LEVEL' }),
    pt('S3-1', null, { videoTime: '1:04:10' }),
    pt('S3-B', 2501, { videoTime: '1:04:19', ohlcElement: 'LOW' }),
    pt('S3-C', 2518, { videoTime: '1:04:19', ohlcElement: 'HIGH' }),
    pt('S3-D', 2500, { videoTime: '1:04:19' }),
    pt('S3-E', 2500, { videoTime: '1:04:19' }),
    pt('S3-F', 2519, { videoTime: '1:04:32', ohlcElement: 'HIGH' }),
  ],
};

describe('SP2L V2 G4/G5 source-extraction schema (non-production)', () => {
  it('accepts a valid extraction record', () => {
    expect(validateExtraction(SEGMENT_3_EXTRACTION)).toEqual({ valid: true, errors: [] });
    expect(() => assertValidExtraction(SEGMENT_3_EXTRACTION)).not.toThrow();
  });

  it('rejects unknown point IDs, invalid prices, and inconsistent fields', () => {
    const cases: Array<{ label: string; error: string; points: ExtractedSourcePoint[] }> = [
      {
        label: 'unknown point ID',
        error: 'EXTRACTION_UNKNOWN_POINT_ID',
        points: [pt('S9-Z', 2500)],
      },
      {
        label: 'non-finite price',
        error: 'EXTRACTION_INVALID_PRICE',
        points: [pt('S3-A', Number.NaN)],
      },
      {
        label: 'price set while marked UNREADABLE',
        error: 'EXTRACTION_UNREADABLE_WITH_PRICE',
        points: [pt('S3-A', 2500, { ohlcElement: 'UNREADABLE' })],
      },
      {
        label: 'invalid video time',
        error: 'EXTRACTION_INVALID_VIDEO_TIME',
        points: [pt('S3-A', 2500, { videoTime: 'wrong' })],
      },
      {
        label: 'invalid timeframe',
        error: 'EXTRACTION_INVALID_TIMEFRAME',
        points: [pt('S3-A', 2500, { chartTimeframe: 'H1' as never })],
      },
      {
        label: 'invalid direction',
        error: 'EXTRACTION_INVALID_DIRECTION',
        points: [pt('S3-A', 2500, { direction: 'LONG' as never })],
      },
    ];

    for (const c of cases) {
      const result = validateExtraction({ ...SEGMENT_3_EXTRACTION, points: c.points });
      expect(result.valid).toBe(false);
      expect(result.errors.some((e) => e.startsWith(c.error))).toBe(true);
    }
  });

  it('rejects records with a missing video URL', () => {
    const result = validateExtraction({ ...SEGMENT_3_EXTRACTION, video: { url: '', lesson: 'SP2L' } });
    expect(result.errors).toContain('EXTRACTION_VIDEO_URL_REQUIRED');
  });

  it('has a canonical registry with unique point IDs and the declared sequence sizes', () => {
    const ids = G4G5_SOURCE_POINT_REGISTRY.map((s) => s.pointId);
    expect(new Set(ids).size).toBe(ids.length);
    expect(G4G5_SOURCE_POINT_REGISTRY.find((s) => s.pointId === 'S2-1')?.sequenceSize).toBe(4);
    expect(G4G5_SOURCE_POINT_REGISTRY.find((s) => s.pointId === 'S3-1')?.sequenceSize).toBe(7);
    expect(G4G5_SOURCE_POINT_REGISTRY.find((s) => s.pointId === 'S2-7')?.anchorConcept).toBeNull();
  });

  it('converts a segment into a chart whose anchors map point IDs to concepts', () => {
    const chart = extractionToChart(SEGMENT_3_EXTRACTION, 'SEGMENT_3');
    expect(chart.id).toBe('EXTRACTION_SEGMENT_3');
    expect(chart.direction).toBe('BULLISH');
    expect(chart.anchors.map((a) => [a.concept, a.price])).toEqual([
      ['otherVisualPoint', 2502],
      ['teacherPointA', 2501],
      ['teacherPointB', 2518],
      ['pendingLimit', 2500],
      ['fill', 2500],
      ['leg2End', 2519],
    ]);
    expect(chart.anchors.some((a) => a.concept === 'correctionExtreme')).toBe(false);
  });

  it('feeds the Phase 38 helpers and reproduces the hand-computed magnitudes', () => {
    const chart = extractionToChart(SEGMENT_3_EXTRACTION, 'SEGMENT_3');
    expect(measureLeg1(chart, 'STRUCTURAL_POINT_TO_STRUCTURAL_POINT')).toBe(17);
    expect(measureLeg2(chart, 'OTHER_VISUAL_POINT')).toBe(17);
    expect(measureLeg2(chart, 'PENDING_LIMIT')).toBe(19);
    expect(measureLeg2(chart, 'ACTUAL_FILL')).toBe(19);
  });

  it('reports MISSING_EVIDENCE for anchors a segment did not expose', () => {
    const report = reportExtractionCandidates(SEGMENT_3_EXTRACTION, 'SEGMENT_3');

    const leg1ById = Object.fromEntries(report.leg1.map((r) => [r.id, r]));
    expect(leg1ById.STRUCTURAL_POINT_TO_STRUCTURAL_POINT).toMatchObject({ status: 'MEASURED', magnitude: 17 });
    expect(leg1ById.STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME!.status).toBe('MISSING_EVIDENCE');
    expect(leg1ById.BREAKOUT_LEVEL_TO_SPIKE_EXTREME!.status).toBe('MISSING_EVIDENCE');

    const leg2ById = Object.fromEntries(report.leg2.map((r) => [r.id, r]));
    expect(leg2ById.OTHER_VISUAL_POINT).toMatchObject({ status: 'MEASURED', magnitude: 17 });
    expect(leg2ById.CORRECTION_EXTREME!.status).toBe('MISSING_EVIDENCE');
    expect(leg2ById.STRUCTURAL_HL_LH!.status).toBe('MISSING_EVIDENCE');
    expect(leg2ById.PENDING_LIMIT).toMatchObject({ status: 'MEASURED', magnitude: 19 });
    expect(leg2ById.ACTUAL_FILL).toMatchObject({ status: 'MEASURED', magnitude: 19 });
  });

  it('excludes UNREADABLE points from measurement but keeps them in provenance', () => {
    const unreadable = unreadablePointIds(SEGMENT_3_EXTRACTION, 'SEGMENT_3');
    expect(unreadable).toContain('S3-1');

    const withUnreadableA = {
      ...SEGMENT_3_EXTRACTION,
      points: SEGMENT_3_EXTRACTION.points.map((p) => (p.pointId === 'S3-A' ? pt('S3-A', null) : p)),
    };
    const report = reportExtractionCandidates(withUnreadableA, 'SEGMENT_3');
    expect(report.unreadablePointIds).toContain('S3-A');
    expect(Object.fromEntries(report.leg2.map((r) => [r.id, r])).OTHER_VISUAL_POINT!.status).toBe('MISSING_EVIDENCE');
  });

  it('maps SELL extraction direction to a BEARISH chart', () => {
    const extraction: G4G5SourceExtraction = {
      schemaVersion: 1,
      video: { url: 'https://youtu.be/7HEC5mO3d3U', lesson: 'SP2L' },
      points: [
        pt('S1-A', 2700, { videoTime: '37:00', direction: 'SELL' }),
        pt('S1-B', 2630, { videoTime: '37:05', direction: 'SELL' }),
        pt('S1-C', 2658, { videoTime: '37:06', direction: 'SELL' }),
        pt('S1-D', 2588, { videoTime: '37:08', direction: 'SELL' }),
      ],
    };
    const chart = extractionToChart(extraction, 'SEGMENT_1');
    expect(chart.direction).toBe('BEARISH');
  });

  it('round-trips through JSON without losing provenance fields', () => {
    const copy = JSON.parse(JSON.stringify(SEGMENT_3_EXTRACTION)) as G4G5SourceExtraction;
    expect(copy).toEqual(SEGMENT_3_EXTRACTION);
    expect(validateExtraction(copy).valid).toBe(true);
  });

  it('template validates clean and is ready to fill in', () => {
    expect(validateExtraction(G4G5_EXTRACTION_TEMPLATE).valid).toBe(true);
    expect(pointsForSegment(G4G5_EXTRACTION_TEMPLATE, 'SEGMENT_3').length).toBe(7);
  });
});

describe('SP2L V2 G4/G5 source-fit checker (non-production)', () => {
  it('identifies the structural-point family and the visual C candidate on segment 3', () => {
    const report = checkSourceFit(SEGMENT_3_EXTRACTION, 'SEGMENT_3');

    expect(report.impliedLeg1).toBe(17);
    expect(report.impliedTp1).toBe(2519);

    const g4ById = Object.fromEntries(report.g4.map((r) => [r.id, r]));
    expect(g4ById.STRUCTURAL_POINT_TO_STRUCTURAL_POINT).toMatchObject({ computed: 17, fit: true });
    expect(g4ById.STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME!.fit).toBeNull();
    expect(report.g4Identified).toBe('STRUCTURAL_POINT_TO_STRUCTURAL_POINT');
    expect(report.g4Ambiguous).toBe(false);

    const g5ById = Object.fromEntries(report.g5.map((r) => [r.id, r]));
    expect(g5ById.OTHER_VISUAL_POINT).toMatchObject({ computed: 17, fit: true });
    expect(g5ById.CORRECTION_EXTREME!.fit).toBeNull();
    expect(report.g5Identified).toBe('OTHER_VISUAL_POINT');
    expect(report.g5Ambiguous).toBe(false);
  });

  it('discriminates non-teacher G4 families when extra anchors are supplied', () => {
    const report = checkSourceFit(SEGMENT_3_EXTRACTION, 'SEGMENT_3', {
      spikeExtreme: 2518,
      firstStructuralLow: 2497,
      breakoutLevel: 2500,
      relevantCandleOpen: 2510,
      spikeStart: 2504,
    });

    const g4ById = Object.fromEntries(report.g4.map((r) => [r.id, r]));
    expect(g4ById.STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME!).toMatchObject({ computed: 21, fit: false });
    expect(g4ById.BREAKOUT_LEVEL_TO_SPIKE_EXTREME).toMatchObject({ computed: 18, fit: false });
    expect(g4ById.SPIKE_START_TO_SPIKE_END).toMatchObject({ computed: 14, fit: false });
    expect(g4ById.RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME).toMatchObject({ computed: 8, fit: false });
    expect(g4ById.STRUCTURAL_POINT_TO_STRUCTURAL_POINT).toMatchObject({ computed: 17, fit: true });
    expect(report.g4Identified).toBe('STRUCTURAL_POINT_TO_STRUCTURAL_POINT');
    expect(report.g4Ambiguous).toBe(false);
  });

  it('flags ambiguity instead of picking when more than one family fits', () => {
    const extraction: G4G5SourceExtraction = {
      ...SEGMENT_3_EXTRACTION,
      points: SEGMENT_3_EXTRACTION.points.map((p) =>
        p.pointId === 'S3-B' ? pt('S3-B', 2500, { videoTime: '1:04:19' }) : p,
      ),
    };
    // teacher Leg 1 now 2500 -> 2518 (implied 18); breakout level 2500 also reproduces 18.
    const report = checkSourceFit(extraction, 'SEGMENT_3', {
      spikeExtreme: 2518,
      breakoutLevel: 2500,
    });

    expect(report.impliedLeg1).toBe(18);
    const g4ById = Object.fromEntries(report.g4.map((r) => [r.id, r]));
    expect(g4ById.BREAKOUT_LEVEL_TO_SPIKE_EXTREME!.fit).toBe(true);
    expect(g4ById.STRUCTURAL_POINT_TO_STRUCTURAL_POINT!.fit).toBe(true);
    expect(report.g4Identified).toBeNull();
    expect(report.g4Ambiguous).toBe(true);
  });

  it('never identifies a non-canonical execution candidate as C', () => {
    // teacher Leg 1 2501 -> 2520 (implied 19) matches the pending/fill distance 19.
    const extraction: G4G5SourceExtraction = {
      ...SEGMENT_3_EXTRACTION,
      points: SEGMENT_3_EXTRACTION.points.map((p) =>
        p.pointId === 'S3-C' ? pt('S3-C', 2520, { videoTime: '1:04:19', ohlcElement: 'HIGH' }) : p,
      ),
    };
    const report = checkSourceFit(extraction, 'SEGMENT_3');

    const g5ById = Object.fromEntries(report.g5.map((r) => [r.id, r]));
    expect(g5ById.PENDING_LIMIT).toMatchObject({ computed: 19, fit: true, canonicalStatus: 'EXCLUDED_NON_CANONICAL' });
    expect(g5ById.ACTUAL_FILL).toMatchObject({ computed: 19, fit: true, canonicalStatus: 'EXCLUDED_NON_CANONICAL' });
    expect(report.g5Identified).toBeNull();
    expect(report.g5Ambiguous).toBe(false);
  });

  it('reports unresolved reasons when the teacher Leg 1 is not extracted', () => {
    const extraction: G4G5SourceExtraction = {
      ...SEGMENT_3_EXTRACTION,
      points: SEGMENT_3_EXTRACTION.points.map((p) => (p.pointId === 'S3-B' ? pt('S3-B', null) : p)),
    };
    const report = checkSourceFit(extraction, 'SEGMENT_3');

    expect(report.impliedLeg1).toBeNull();
    expect(report.unresolvedReasons).toContain('TEACHER_LEG1_NOT_EXTRACTED');
    expect(report.g4.every((r) => r.fit === null)).toBe(true);
    expect(report.g4Identified).toBeNull();
  });

  it('can identify the correction-extreme candidate on segment 1 when the numbers agree', () => {
    const extraction: G4G5SourceExtraction = {
      schemaVersion: 1,
      video: { url: 'https://youtu.be/7HEC5mO3d3U', lesson: 'SP2L' },
      points: [
        pt('S1-A', 2700, { videoTime: '37:00', direction: 'SELL' }),
        pt('S1-B', 2630, { videoTime: '37:05', direction: 'SELL' }),
        pt('S1-C', 2658, { videoTime: '37:06', direction: 'SELL' }),
        pt('S1-D', 2588, { videoTime: '37:08', direction: 'SELL' }),
      ],
    };
    const report = checkSourceFit(extraction, 'SEGMENT_1');

    expect(report.impliedLeg1).toBe(70);
    const g5ById = Object.fromEntries(report.g5.map((r) => [r.id, r]));
    expect(g5ById.CORRECTION_EXTREME!).toMatchObject({ computed: 70, fit: true });
    expect(report.g5Identified).toBe('CORRECTION_EXTREME');
  });

  it('runs the fit checker across all three segments', () => {
    const all = checkAllSegmentsSourceFit(SEGMENT_3_EXTRACTION);
    expect(Object.keys(all.segments)).toEqual(['SEGMENT_1', 'SEGMENT_2', 'SEGMENT_3']);
    expect(all.segments.SEGMENT_3!.impliedLeg1).toBe(17);
    expect(all.segments.SEGMENT_1!.unresolvedReasons).toContain('TEACHER_LEG1_NOT_EXTRACTED');
  });
});

describe('SP2L V2 source-frame evidence (37:22)', () => {
  it('accepts the supplied 37:22 frame as valid provenance evidence', () => {
    expect(validateFrameEvidence(G4G5_37_22_FRAME_EVIDENCE)).toEqual({ valid: true, errors: [] });
    expect(G4G5_37_22_FRAME_EVIDENCE).toMatchObject({
      frameId: 'FRAME_37_22',
      videoTime: '37:22',
      status: 'SUPPLIED',
      semanticFact: 'LEVEL_BREAK_AND_GAP_CAN_OCCUR_IN_SAME_TRANSITION',
    });
  });

  it('rejects malformed frame evidence', () => {
    const base = G4G5_37_22_FRAME_EVIDENCE;
    const cases: Array<{ label: string; error: string; frame: SourceFrameEvidence }> = [
      {
        label: 'unknown frame ID',
        error: 'SOURCE_FRAME_UNKNOWN_ID',
        frame: { ...base, frameId: 'FRAME_99_99' },
      },
      {
        label: 'invalid video time',
        error: 'SOURCE_FRAME_INVALID_VIDEO_TIME',
        frame: { ...base, videoTime: 'later' },
      },
      {
        label: 'missing semantic fact',
        error: 'SOURCE_FRAME_SEMANTIC_FACT_REQUIRED',
        frame: { ...base, semanticFact: '' },
      },
      {
        label: 'invalid status',
        error: 'SOURCE_FRAME_INVALID_STATUS',
        frame: { ...base, status: 'REJECTED' as never },
      },
      {
        label: 'missing source basis',
        error: 'SOURCE_FRAME_SOURCE_BASIS_REQUIRED',
        frame: { ...base, sourceBasis: '' },
      },
    ];

    for (const c of cases) {
      const result = validateFrameEvidence(c.frame);
      expect(result.valid).toBe(false);
      expect(result.errors.some((e) => e.startsWith(c.error))).toBe(true);
    }
  });

  it('stored frames.json matches the typed 37:22 evidence record exactly', () => {
    const path = resolve(
      fileURLToPath(new URL('../data/reports/strategy-a-sp2l-g4g5-source-evidence/frames.json', import.meta.url)),
    );
    const stored = JSON.parse(readFileSync(path, 'utf8')) as {
      schemaVersion: number;
      frames: SourceFrameEvidence[];
    };
    expect(stored.schemaVersion).toBe(1);
    expect(stored.frames).toHaveLength(1);
    expect(stored.frames[0]).toEqual(G4G5_37_22_FRAME_EVIDENCE);
    expect(validateFrameEvidence(stored.frames[0]!).valid).toBe(true);
  });

  it('round-trips the 37:22 frame record through JSON', () => {
    const copy = JSON.parse(JSON.stringify(G4G5_37_22_FRAME_EVIDENCE)) as SourceFrameEvidence;
    expect(copy).toEqual(G4G5_37_22_FRAME_EVIDENCE);
    expect(validateFrameEvidence(copy).valid).toBe(true);
  });
});