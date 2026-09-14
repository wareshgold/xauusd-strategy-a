export type G403EvidenceStatus = 'UNRESOLVED' | 'SOURCE-EVIDENCE-REQUIRED';

export type G403EntryHypothesis = {
  readonly id: string;
  readonly interpretation: string;
  readonly canonical: false;
};

export type G403MinimalPair = {
  readonly id: string;
  readonly changedDimension: string;
  readonly fixtureA: string;
  readonly fixtureB: string;
  readonly expectedResearchQuestion: string;
};

/**
 * G403 resolves source semantics around the pending-limit entry execution.
 * It deliberately does not choose an entry price, trigger rule, fill model,
 * persistence rule, or pre-fill invalidation rule.
 */
export const G403_ENTRY_HYPOTHESES: readonly G403EntryHypothesis[] = [
  { id: 'ENTRY-H1', interpretation: 'pending limit is placed at a source-defined correction/reference price', canonical: false },
  { id: 'ENTRY-H2', interpretation: 'pending limit is placed at geometric C', canonical: false },
  { id: 'ENTRY-H3', interpretation: 'pending limit uses a source-defined level distinct from geometric C', canonical: false },
  { id: 'ENTRY-H4', interpretation: 'entry activation/fill requires a source-defined temporal or persistence condition', canonical: false }
];

export const G403_MINIMAL_PAIRS: readonly G403MinimalPair[] = [
  {
    id: 'ENTRY-MP-01',
    changedDimension: 'limit price versus geometric C',
    fixtureA: 'pending limit at candidate geometric C',
    fixtureB: 'pending limit at a distinct source-described correction/reference level',
    expectedResearchQuestion: 'Does the source equate the executable limit price with C or distinguish them?'
  },
  {
    id: 'ENTRY-MP-02',
    changedDimension: 'touch versus close-through activation',
    fixtureA: 'price touches the pending-limit level intrabar',
    fixtureB: 'price closes through the pending-limit level after touching it',
    expectedResearchQuestion: 'What event does the source require for entry activation/fill?'
  },
  {
    id: 'ENTRY-MP-03',
    changedDimension: 'order persistence',
    fixtureA: 'level is touched after the correction begins and order remains active',
    fixtureB: 'same touch occurs after a source-described invalidating event',
    expectedResearchQuestion: 'Does the source define when a pending order remains valid or must be cancelled?'
  },
  {
    id: 'ENTRY-MP-04',
    changedDimension: 'pre-fill invalidation',
    fixtureA: 'structural invalidation occurs before the pending order is touched',
    fixtureB: 'same structural invalidation occurs only after the order is filled',
    expectedResearchQuestion: 'What is the source-defined relationship between invalidation and pending-order activation?'
  },
  {
    id: 'ENTRY-MP-05',
    changedDimension: 'overshoot through limit',
    fixtureA: 'price touches the level and reverses without materially exceeding it',
    fixtureB: 'price traverses through the level before reversing',
    expectedResearchQuestion: 'Does source material define a specific fill/touch semantics or boundary?'
  }
];

export const G403_STATUS = {
  gate: 'G403',
  subject: 'Pending-limit entry execution source resolution',
  status: 'UNRESOLVED' as G403EvidenceStatus,
  canonicalEntryPrice: null,
  canonicalTrigger: null,
  canonicalPersistenceRule: null,
  canonicalFillSemantics: null,
  canonicalPreFillInvalidation: null,
  hypotheses: G403_ENTRY_HYPOTHESES,
  minimalPairs: G403_MINIMAL_PAIRS
} as const;

export function g403AllHypothesesRemainNonCanonical(): boolean {
  return G403_ENTRY_HYPOTHESES.every((item) => item.canonical === false);
}

export function g403DoesNotInventExecutableEntryGeometry(): boolean {
  return G403_STATUS.canonicalEntryPrice === null
    && G403_STATUS.canonicalTrigger === null
    && G403_STATUS.canonicalPersistenceRule === null
    && G403_STATUS.canonicalFillSemantics === null
    && G403_STATUS.canonicalPreFillInvalidation === null;
}
