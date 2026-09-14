export type G404EvidenceStatus = 'UNRESOLVED' | 'SOURCE-EVIDENCE-REQUIRED';

export type G404Dimension =
  | 'STOP_REFERENCE'
  | 'STOP_BOUNDARY'
  | 'PRICE_FIELD'
  | 'BUFFER'
  | 'INVALIDATION_TIMING'
  | 'EXECUTABLE_STOP';

export interface G404Hypothesis {
  readonly id: string;
  readonly dimension: G404Dimension;
  readonly description: string;
  readonly canonical: false;
}

export const G404_HYPOTHESES: readonly G404Hypothesis[] = [
  { id: 'STOP-H1', dimension: 'STOP_REFERENCE', description: 'spike-origin structural event', canonical: false },
  { id: 'STOP-H2', dimension: 'STOP_REFERENCE', description: 'source-defined structural A/B/C setup boundary', canonical: false },
  { id: 'STOP-H3', dimension: 'STOP_REFERENCE', description: 'correction or entry reference boundary', canonical: false },
  { id: 'STOP-H4', dimension: 'STOP_BOUNDARY', description: 'full wick extreme', canonical: false },
  { id: 'STOP-H5', dimension: 'STOP_BOUNDARY', description: 'candle-body boundary', canonical: false },
  { id: 'STOP-H6', dimension: 'STOP_BOUNDARY', description: 'source-specific structural boundary', canonical: false },
  { id: 'STOP-H7', dimension: 'PRICE_FIELD', description: 'HIGH/LOW extreme', canonical: false },
  { id: 'STOP-H8', dimension: 'PRICE_FIELD', description: 'OPEN/CLOSE body field', canonical: false },
  { id: 'STOP-H9', dimension: 'PRICE_FIELD', description: 'source-specific executable price field', canonical: false },
  { id: 'STOP-H10', dimension: 'BUFFER', description: 'no additional buffer', canonical: false },
  { id: 'STOP-H11', dimension: 'BUFFER', description: 'source-defined positive buffer', canonical: false },
  { id: 'STOP-H12', dimension: 'BUFFER', description: 'source-defined point/tick buffer', canonical: false },
  { id: 'STOP-H13', dimension: 'INVALIDATION_TIMING', description: 'structural invalidation may cancel setup before fill', canonical: false },
  { id: 'STOP-H14', dimension: 'INVALIDATION_TIMING', description: 'invalidation applies only after fill', canonical: false },
  { id: 'STOP-H15', dimension: 'EXECUTABLE_STOP', description: 'structural boundary equals executable stop', canonical: false },
  { id: 'STOP-H16', dimension: 'EXECUTABLE_STOP', description: 'executable stop is offset from structural boundary', canonical: false }
] as const;

export const G404_MINIMAL_PAIRS = [
  'STOP-MP-01:spike-origin-vs-setup-boundary',
  'STOP-MP-02:wick-vs-body-boundary',
  'STOP-MP-03:high-low-vs-open-close-price-field',
  'STOP-MP-04:zero-vs-positive-buffer',
  'STOP-MP-05:pre-fill-vs-post-fill-invalidation',
  'STOP-MP-06:structural-boundary-vs-executable-stop',
  'STOP-MP-07:bullish-vs-bearish-mirror'
] as const;

export const G404_STATUS = {
  gate: 'G404',
  subject: 'structural stop boundary source resolution',
  status: 'UNRESOLVED' as G404EvidenceStatus,
  canonicalReference: null,
  canonicalBoundary: null,
  canonicalPriceField: null,
  canonicalBuffer: null,
  canonicalInvalidationTiming: null,
  canonicalExecutableStop: null
} as const;

export function g404AllHypothesesRemainNonCanonical(): boolean {
  return G404_HYPOTHESES.every((item) => item.canonical === false);
}

export function g404DoesNotInventExecutableStopGeometry(): boolean {
  return G404_STATUS.canonicalReference === null
    && G404_STATUS.canonicalBoundary === null
    && G404_STATUS.canonicalPriceField === null
    && G404_STATUS.canonicalBuffer === null
    && G404_STATUS.canonicalInvalidationTiming === null
    && G404_STATUS.canonicalExecutableStop === null;
}
