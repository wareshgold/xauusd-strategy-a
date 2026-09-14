export type G405EvidenceStatus = 'UNRESOLVED' | 'SOURCE-EVIDENCE-REQUIRED';

export type G405Dimension =
  | 'TARGET_REFERENCE'
  | 'TARGET_LEVEL'
  | 'TARGET_COUNT'
  | 'PRICE_FIELD'
  | 'LEG_RELATION'
  | 'EXECUTABLE_TARGET';

export interface G405Hypothesis {
  readonly id: string;
  readonly dimension: G405Dimension;
  readonly description: string;
  readonly canonical: false;
}

export const G405_HYPOTHESES: readonly G405Hypothesis[] = [
  { id: 'TARGET-H1', dimension: 'TARGET_REFERENCE', description: 'source-defined second-leg endpoint', canonical: false },
  { id: 'TARGET-H2', dimension: 'TARGET_REFERENCE', description: 'AB=CD projected endpoint', canonical: false },
  { id: 'TARGET-H3', dimension: 'TARGET_REFERENCE', description: 'source-defined structural target reference', canonical: false },
  { id: 'TARGET-H4', dimension: 'TARGET_LEVEL', description: 'single target at the second-leg endpoint', canonical: false },
  { id: 'TARGET-H5', dimension: 'TARGET_LEVEL', description: 'two staged targets with source-defined TP1/TP2 mapping', canonical: false },
  { id: 'TARGET-H6', dimension: 'TARGET_LEVEL', description: 'target levels derived from entry-to-stop risk multiples', canonical: false },
  { id: 'TARGET-H7', dimension: 'TARGET_COUNT', description: 'one executable target', canonical: false },
  { id: 'TARGET-H8', dimension: 'TARGET_COUNT', description: 'two executable targets', canonical: false },
  { id: 'TARGET-H9', dimension: 'PRICE_FIELD', description: 'geometric endpoint price field', canonical: false },
  { id: 'TARGET-H10', dimension: 'PRICE_FIELD', description: 'source-defined candle high/low or body field', canonical: false },
  { id: 'TARGET-H11', dimension: 'LEG_RELATION', description: 'AB=CD translation determines target endpoint', canonical: false },
  { id: 'TARGET-H12', dimension: 'LEG_RELATION', description: 'Leg2 approximately equals Leg1 without exact executable equality', canonical: false },
  { id: 'TARGET-H13', dimension: 'EXECUTABLE_TARGET', description: 'geometric target equals executable take-profit price', canonical: false },
  { id: 'TARGET-H14', dimension: 'EXECUTABLE_TARGET', description: 'executable take-profit is offset from geometric target', canonical: false }
] as const;

export const G405_MINIMAL_PAIRS = [
  'TARGET-MP-01:second-leg-endpoint-vs-abcd-projection',
  'TARGET-MP-02:single-vs-two-target-mapping',
  'TARGET-MP-03:geometric-endpoint-vs-risk-multiple',
  'TARGET-MP-04:high-low-vs-body-price-field',
  'TARGET-MP-05:ab-equals-cd-vs-approximate-leg-equality',
  'TARGET-MP-06:geometric-target-vs-executable-take-profit',
  'TARGET-MP-07:bullish-vs-bearish-mirror'
] as const;

export const G405_STATUS = {
  gate: 'G405',
  subject: 'TP1/TP2 target mapping source resolution',
  status: 'UNRESOLVED' as G405EvidenceStatus,
  canonicalReference: null,
  canonicalTargetLevel: null,
  canonicalTargetCount: null,
  canonicalPriceField: null,
  canonicalLegRelation: null,
  canonicalExecutableTarget: null
} as const;

export function g405AllHypothesesRemainNonCanonical(): boolean {
  return G405_HYPOTHESES.every((item) => item.canonical === false);
}

export function g405DoesNotInventExecutableTargetGeometry(): boolean {
  return G405_STATUS.canonicalReference === null
    && G405_STATUS.canonicalTargetLevel === null
    && G405_STATUS.canonicalTargetCount === null
    && G405_STATUS.canonicalPriceField === null
    && G405_STATUS.canonicalLegRelation === null
    && G405_STATUS.canonicalExecutableTarget === null;
}
