export type SemanticEvidenceStatus = 'SOURCE-CONFIRMED' | 'SOURCE-SUPPORTED';

export interface SemanticCoreRule {
  readonly id: string;
  readonly concept: string;
  readonly statement: string;
  readonly evidence: SemanticEvidenceStatus;
}

export interface UnresolvedDimension {
  readonly id: string;
  readonly description: string;
}

/**
 * G399 freezes only the source-confirmed semantic layer.
 * It deliberately contains no executable geometry, prices, tolerances,
 * anchors, or execution shortcuts.
 */
export const SP2L_SEMANTIC_CORE = {
  version: 'SP2L-SEMANTIC-CORE-G399',
  canonical: true,
  rules: [
    {
      id: 'SEM-SP2L-01',
      concept: 'SP2L',
      statement: 'Strategy A is the Spike → 2 Leg structure.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-02',
      concept: 'BREAKOUT',
      statement: 'The first directional movement is associated with breakout and follow-through.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-03',
      concept: 'P-GAP',
      statement: 'A valid breakout is associated with P-Gap.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-04',
      concept: 'CORRECTION',
      statement: 'A correction follows the first leg/spike structure.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-05',
      concept: 'PENDING-LIMIT',
      statement: 'Entry is represented by a pending-limit order during the correction until activation.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-06',
      concept: 'INVALIDATION',
      statement: 'The setup has structural invalidation/stop semantics.',
      evidence: 'SOURCE-SUPPORTED'
    },
    {
      id: 'SEM-SP2L-07',
      concept: 'SECOND-LEG',
      statement: 'The setup seeks continuation as a second leg.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-08',
      concept: 'AB-CD',
      statement: 'The source explicitly defines an AB = CD relationship between the legs.',
      evidence: 'SOURCE-CONFIRMED'
    },
    {
      id: 'SEM-SP2L-09',
      concept: 'TP1-TP2',
      statement: 'TP1/TP2 and R1/R2 are source-defined outcome terminology.',
      evidence: 'SOURCE-CONFIRMED'
    }
  ] as readonly SemanticCoreRule[],
  unresolved: [
    { id: 'UNRES-PGAP-GEOMETRY', description: 'Executable P-Gap OHLC geometry and formula.' },
    { id: 'UNRES-ABCD-ANCHORS', description: 'Exact A/B/C anchors, wick/body semantics, and D construction.' },
    { id: 'UNRES-ABCD-TOLERANCE', description: 'Executable AB=CD equality tolerance.' },
    { id: 'UNRES-ENTRY-PRICE', description: 'Exact pending-limit price semantics and fill price.' },
    { id: 'UNRES-ENTRY-TIMING', description: 'Trigger, persistence, activation, and invalidation-before-fill semantics.' },
    { id: 'UNRES-STOP-BOUNDARY', description: 'Exact structural invalidation boundary and executable stop price.' },
    { id: 'UNRES-TARGET-MAPPING', description: 'Executable mapping from source TP1/TP2 terminology to prices.' }
  ] as readonly UnresolvedDimension[]
} as const;

export function isSemanticCoreFrozen(): true {
  return true;
}

/** Semantic knowledge cannot manufacture an executable canonical candidate. */
export function assertExecutableGeometryResolved(): never {
  throw new Error(
    'G399 canonical geometry guard: semantic core is frozen, but executable geometry remains unresolved.'
  );
}
