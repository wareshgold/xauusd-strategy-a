export type G355FixtureFamily =
  | 'GENERIC_GAP'
  | 'TAXONOMY'
  | 'TIMING'
  | 'ENDPOINT'
  | 'THRESHOLD'
  | 'TOLERANCE'
  | 'CONTEXT'
  | 'ANCHORS';

export type G355Fixture = {
  id: string;
  family: G355FixtureFamily;
  condition: string;
  expected: string;
  canonical: false;
};

export const G355_FIXTURES: readonly G355Fixture[] = [
  { id: 'PG-01', family: 'GENERIC_GAP', condition: 'High[i-2] < Low[i]', expected: 'GENERIC_GAP_ONLY', canonical: false },
  { id: 'PG-02', family: 'GENERIC_GAP', condition: 'bearish mirrored separation', expected: 'CANDIDATE_ONLY', canonical: false },
  { id: 'PG-03', family: 'TAXONOMY', condition: 'movement-origin gap without sustained pressure', expected: 'BREAKOUT_GAP_CANDIDATE', canonical: false },
  { id: 'PG-04', family: 'TAXONOMY', condition: 'sustained pressure -> pause -> trend bar + gap', expected: 'PRESSURE_GAP_CANDIDATE', canonical: false },
  { id: 'PG-05', family: 'TIMING', condition: 'breakout -> FT -> P-GAP', expected: 'SP2L_VARIANT_A', canonical: false },
  { id: 'PG-06', family: 'TIMING', condition: 'higher-lows -> P-GAP', expected: 'SP2L_VARIANT_B', canonical: false },
  { id: 'PG-07', family: 'ENDPOINT', condition: 'wick overlap; body separation', expected: 'WICK_BODY_DISCRIMINATOR', canonical: false },
  { id: 'PG-08', family: 'ENDPOINT', condition: 'body overlap; wick separation', expected: 'WICK_BODY_DISCRIMINATOR', canonical: false },
  { id: 'PG-09', family: 'THRESHOLD', condition: 'very small positive gap', expected: 'MIN_SIZE_UNRESOLVED', canonical: false },
  { id: 'PG-10', family: 'TOLERANCE', condition: 'varying overlap', expected: 'TOLERANCE_UNRESOLVED', canonical: false },
  { id: 'PG-11', family: 'CONTEXT', condition: 'pressure-like sequence near resistance + reversal', expected: 'PRESSURE_EXHAUSTION_DISCRIMINATOR', canonical: false },
  { id: 'PG-12', family: 'CONTEXT', condition: 'range gap with weak follow-through', expected: 'COMMON_GAP_CANDIDATE', canonical: false },
  { id: 'PG-13', family: 'CONTEXT', condition: 'P-GAP adjacent to E-GAP', expected: 'CLASSIFICATION_BOUNDARY', canonical: false },
  { id: 'PG-14', family: 'ANCHORS', condition: 'same candles with alternate A/B/C/D labels', expected: 'ANCHOR_HYPOTHESES_ONLY', canonical: false },
];

export function g355AllFixturesRemainNonCanonical(fixtures: readonly G355Fixture[] = G355_FIXTURES): boolean {
  return fixtures.every((fixture) => fixture.canonical === false);
}

export function g355GenericGapEvidenceIsNotPgapPromotion(fixture: G355Fixture): boolean {
  return fixture.id === 'PG-01' && fixture.expected === 'GENERIC_GAP_ONLY' && fixture.canonical === false;
}

export function g355HasBothSourceSupportedTimingVariants(fixtures: readonly G355Fixture[] = G355_FIXTURES): boolean {
  const ids = new Set(fixtures.filter((fixture) => fixture.family === 'TIMING').map((fixture) => fixture.id));
  return ids.has('PG-05') && ids.has('PG-06');
}

export function g355KeepsTaxonomySeparated(fixtures: readonly G355Fixture[] = G355_FIXTURES): boolean {
  const breakout = fixtures.find((fixture) => fixture.id === 'PG-03');
  const pressure = fixtures.find((fixture) => fixture.id === 'PG-04');
  return breakout?.expected === 'BREAKOUT_GAP_CANDIDATE'
    && pressure?.expected === 'PRESSURE_GAP_CANDIDATE'
    && breakout?.expected !== pressure?.expected;
}
