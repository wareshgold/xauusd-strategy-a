export type G401EvidenceStatus = 'UNRESOLVED' | 'SOURCE-EVIDENCE-REQUIRED';

export type G401PgapHypothesis = {
  readonly id: string;
  readonly interpretation: string;
  readonly discriminatedBy: string;
  readonly canonical: false;
};

export type G401MinimalPair = {
  readonly id: string;
  readonly changedDimension: string;
  readonly fixtureA: string;
  readonly fixtureB: string;
  readonly expectedResearchQuestion: string;
};

/**
 * G401 is source-resolution research only. It does not define P-Gap geometry.
 * Candidate formulas remain labels until authoritative evidence resolves them.
 */
export const G401_PGAP_HYPOTHESES: readonly G401PgapHypothesis[] = [
  {
    id: 'PGAP-H1',
    interpretation: 'generic three-candle range separation',
    discriminatedBy: 'whether source explicitly defines a three-candle OHLC relation',
    canonical: false
  },
  {
    id: 'PGAP-H2',
    interpretation: 'body-boundary separation',
    discriminatedBy: 'whether source treats candle bodies rather than full wicks as the gap boundary',
    canonical: false
  },
  {
    id: 'PGAP-H3',
    interpretation: 'wick-boundary separation',
    discriminatedBy: 'whether source requires wick endpoint separation',
    canonical: false
  },
  {
    id: 'PGAP-H4',
    interpretation: 'source-specific P-Gap construction distinct from generic gap taxonomy',
    discriminatedBy: 'explicit source wording/diagram that cannot be reduced to a generic gap formula',
    canonical: false
  }
];

export const G401_MINIMAL_PAIRS: readonly G401MinimalPair[] = [
  {
    id: 'PG-MP-01',
    changedDimension: 'wick-versus-body boundary',
    fixtureA: 'full-range separation preserved; body overlap introduced',
    fixtureB: 'full-range separation preserved; body separation introduced',
    expectedResearchQuestion: 'Does the source classify using wick endpoints, body boundaries, or neither?'
  },
  {
    id: 'PG-MP-02',
    changedDimension: 'generic three-candle separation',
    fixtureA: 'generic three-candle range gap only',
    fixtureB: 'same gap plus source-described breakout/follow-through context',
    expectedResearchQuestion: 'Is P-Gap merely a generic gap or context-dependent source construct?'
  },
  {
    id: 'PG-MP-03',
    changedDimension: 'gap magnitude',
    fixtureA: 'positive separation by one price unit',
    fixtureB: 'positive separation by ten price units',
    expectedResearchQuestion: 'Does authoritative source material define a minimum size or threshold?'
  },
  {
    id: 'PG-MP-04',
    changedDimension: 'temporal placement',
    fixtureA: 'breakout -> follow-through -> candidate gap',
    fixtureB: 'candidate gap -> breakout -> follow-through',
    expectedResearchQuestion: 'Which event ordering, if any, is source-required?'
  },
  {
    id: 'PG-MP-05',
    changedDimension: 'context',
    fixtureA: 'candidate gap inside a range with weak continuation',
    fixtureB: 'same candle geometry at a source-described breakout',
    expectedResearchQuestion: 'Does context distinguish P-Gap from an ordinary/common gap?'
  }
];

export const G401_STATUS = {
  gate: 'G401',
  subject: 'P-Gap source resolution',
  status: 'UNRESOLVED' as G401EvidenceStatus,
  canonicalFormula: null,
  canonicalThreshold: null,
  canonicalTolerance: null,
  hypotheses: G401_PGAP_HYPOTHESES,
  minimalPairs: G401_MINIMAL_PAIRS
} as const;

export function g401AllHypothesesRemainNonCanonical(): boolean {
  return G401_PGAP_HYPOTHESES.every((item) => item.canonical === false);
}

export function g401DoesNotInventExecutableGeometry(): boolean {
  return G401_STATUS.canonicalFormula === null
    && G401_STATUS.canonicalThreshold === null
    && G401_STATUS.canonicalTolerance === null;
}
