/**
 * G327 target-geometry fixtures (research-only).
 *
 * These fixtures encode the source-observed level labels and numeric annotations
 * without selecting a canonical interpretation. They are intentionally synthetic:
 * no historical XAUUSD data and no profitability criterion are involved.
 *
 * Source evidence represented here:
 *   TP2 > TP1 > Entry > SL (bullish schematic)
 *   numeric annotations: 250 point, 500 point, 1000
 *
 * Candidate mappings are kept separate so a test can prove that an
 * interpretation is inspectable and does not silently fall back to another.
 */

export type TargetGeometryCandidate = 'C1' | 'C2' | 'C3' | 'C4';

export interface TargetGeometryFixture {
  id: string;
  direction: 'BULLISH';
  entry: number;
  sl: number | null;
  tp1: number | null;
  tp2: number | null;
  annotation250: number;
  annotation500: number;
  annotation1000: number;
  mappingStatus: 'DETERMINISTIC_CANDIDATE' | 'NON_MAPPABLE';
}

const ENTRY = 3000;
const P250 = 250;
const P500 = 500;
const P1000 = 1000;

/** C1: equal-ladder hypothesis from G315/G316, explicitly NOT frozen. */
export const C1_EQUAL_LADDER: TargetGeometryFixture = {
  id: 'G327_C1_EQUAL_LADDER',
  direction: 'BULLISH',
  entry: ENTRY,
  sl: ENTRY - P500,
  tp1: ENTRY + P250,
  tp2: ENTRY + P500,
  annotation250: P250,
  annotation500: P500,
  annotation1000: P1000,
  mappingStatus: 'DETERMINISTIC_CANDIDATE',
};

/** C2: sequential-interval reading: 250 then 500 as adjacent intervals. */
export const C2_SEQUENTIAL_INTERVALS: TargetGeometryFixture = {
  id: 'G327_C2_SEQUENTIAL_INTERVALS',
  direction: 'BULLISH',
  entry: ENTRY,
  sl: ENTRY - P250,
  tp1: ENTRY + P250,
  tp2: ENTRY + P750,
  annotation250: P250,
  annotation500: P500,
  annotation1000: P1000,
  mappingStatus: 'DETERMINISTIC_CANDIDATE',
};

/** C3: shifted-anchor reading: 250 risk-side, 500 first target, 1000 terminal. */
export const C3_SHIFTED_ANCHORS: TargetGeometryFixture = {
  id: 'G327_C3_SHIFTED_ANCHORS',
  direction: 'BULLISH',
  entry: ENTRY,
  sl: ENTRY - P250,
  tp1: ENTRY + P500,
  tp2: ENTRY + P1000,
  annotation250: P250,
  annotation500: P500,
  annotation1000: P1000,
  mappingStatus: 'DETERMINISTIC_CANDIDATE',
};

/**
 * C4 is deliberately non-mappable. The source frames permit the possibility
 * that the handwritten numbers are examples rather than interval assignments.
 * It must never silently become C1/C2/C3.
 */
export const C4_EXAMPLE_ONLY: TargetGeometryFixture = {
  id: 'G327_C4_EXAMPLE_ONLY',
  direction: 'BULLISH',
  entry: ENTRY,
  sl: null,
  tp1: null,
  tp2: null,
  annotation250: P250,
  annotation500: P500,
  annotation1000: P1000,
  mappingStatus: 'NON_MAPPABLE',
};

export const G327_TARGET_FIXTURES: Record<TargetGeometryCandidate, TargetGeometryFixture> = {
  C1: C1_EQUAL_LADDER,
  C2: C2_SEQUENTIAL_INTERVALS,
  C3: C3_SHIFTED_ANCHORS,
  C4: C4_EXAMPLE_ONLY,
};

export function targetDistance(fixture: TargetGeometryFixture, target: 'SL_TO_ENTRY' | 'ENTRY_TO_TP1' | 'ENTRY_TO_TP2' | 'SL_TO_TP2'): number | null {
  const { entry, sl, tp1, tp2 } = fixture;
  if (target === 'SL_TO_ENTRY') return sl === null ? null : Math.abs(entry - sl);
  if (target === 'ENTRY_TO_TP1') return tp1 === null ? null : Math.abs(tp1 - entry);
  if (target === 'ENTRY_TO_TP2') return tp2 === null ? null : Math.abs(tp2 - entry);
  return sl === null || tp2 === null ? null : Math.abs(tp2 - sl);
}
