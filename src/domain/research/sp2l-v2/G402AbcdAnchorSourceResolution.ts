export type G402EvidenceStatus = 'UNRESOLVED' | 'SOURCE-EVIDENCE-REQUIRED';

export type G402Dimension =
  | 'A_ANCHOR'
  | 'B_ANCHOR'
  | 'C_ANCHOR'
  | 'D_ANCHOR'
  | 'PRICE_FIELD'
  | 'WICK_BODY_SEMANTICS'
  | 'ABCD_TOLERANCE';

export interface G402Hypothesis {
  readonly id: string;
  readonly dimension: G402Dimension;
  readonly description: string;
  readonly canonical: false;
}

/**
 * G402 resolves source evidence for the AB=CD geometry without selecting a
 * profitable or conventional anchor model. The relationship is source-
 * confirmed; the executable anchors and tolerance are not.
 */
export const G402_HYPOTHESES: readonly G402Hypothesis[] = [
  { id: 'ABCD-A-H1', dimension: 'A_ANCHOR', description: 'source-defined deep/origin event', canonical: false },
  { id: 'ABCD-A-H2', dimension: 'A_ANCHOR', description: 'first breakout event', canonical: false },
  { id: 'ABCD-A-H3', dimension: 'A_ANCHOR', description: 'nearest structural swing', canonical: false },
  { id: 'ABCD-B-H1', dimension: 'B_ANCHOR', description: 'source-defined parent B event', canonical: false },
  { id: 'ABCD-B-H2', dimension: 'B_ANCHOR', description: 'nested B event', canonical: false },
  { id: 'ABCD-C-H1', dimension: 'C_ANCHOR', description: 'source correction reference', canonical: false },
  { id: 'ABCD-C-H2', dimension: 'C_ANCHOR', description: 'pending-order fill treated as C for negative-control research only', canonical: false },
  { id: 'ABCD-D-H1', dimension: 'D_ANCHOR', description: 'source-described second-leg endpoint', canonical: false },
  { id: 'ABCD-D-H2', dimension: 'D_ANCHOR', description: 'AB=CD projected endpoint for research comparison only', canonical: false },
  { id: 'ABCD-P-H1', dimension: 'PRICE_FIELD', description: 'HIGH/LOW extrema', canonical: false },
  { id: 'ABCD-P-H2', dimension: 'PRICE_FIELD', description: 'OPEN/CLOSE body fields', canonical: false },
  { id: 'ABCD-P-H3', dimension: 'PRICE_FIELD', description: 'source-specific price field', canonical: false },
  { id: 'ABCD-WB-H1', dimension: 'WICK_BODY_SEMANTICS', description: 'wick-based structural measurement', canonical: false },
  { id: 'ABCD-WB-H2', dimension: 'WICK_BODY_SEMANTICS', description: 'body-based structural measurement', canonical: false },
  { id: 'ABCD-WB-H3', dimension: 'WICK_BODY_SEMANTICS', description: 'source-specific wick/body semantics', canonical: false },
  { id: 'ABCD-T-H1', dimension: 'ABCD_TOLERANCE', description: 'exact equality', canonical: false },
  { id: 'ABCD-T-H2', dimension: 'ABCD_TOLERANCE', description: 'non-zero tolerance', canonical: false }
] as const;

export const G402_MINIMAL_PAIRS = [
  'ABCD-MP-01:A-anchor-only divergence',
  'ABCD-MP-02:B-anchor-only divergence',
  'ABCD-MP-03:C-anchor-vs-fill divergence',
  'ABCD-MP-04:wick-vs-body divergence',
  'ABCD-MP-05:price-field divergence',
  'ABCD-MP-06:D-endpoint divergence',
  'ABCD-MP-07:tolerance divergence'
] as const;

export const G402_STATUS = {
  gate: 'G402',
  subject: 'AB=CD anchor source resolution',
  status: 'UNRESOLVED' as G402EvidenceStatus,
  relationship: 'SOURCE-CONFIRMED' as const,
  canonicalAnchors: null,
  canonicalPriceField: null,
  canonicalWickBodySemantics: null,
  canonicalTolerance: null
} as const;

export function g402AllHypothesesRemainNonCanonical(): boolean {
  return G402_HYPOTHESES.every((hypothesis) => hypothesis.canonical === false);
}

export function g402DoesNotInventExecutableGeometry(): boolean {
  return (
    G402_STATUS.canonicalAnchors === null &&
    G402_STATUS.canonicalPriceField === null &&
    G402_STATUS.canonicalWickBodySemantics === null &&
    G402_STATUS.canonicalTolerance === null
  );
}
