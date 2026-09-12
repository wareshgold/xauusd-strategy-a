export type G345EvidenceStatus =
  | 'SOURCE_CONFIRMED'
  | 'SOURCE_SUPPORTED'
  | 'UNRESOLVED'
  | 'EXPLICITLY_REJECTED';

export type G345ResolutionOutcome =
  | 'RESOLVED'
  | 'NOT_RESOLVED'
  | 'SOURCE_REJECTED';

export type G345EvidenceRow = {
  id: string;
  dimension: string;
  status: G345EvidenceStatus;
  outcome: G345ResolutionOutcome;
  authoritativeReferences: string[];
  sufficientEvidenceRequirement: string;
};

export const G345_SOURCE_EVIDENCE_MATRIX: G345EvidenceRow[] = [
  {
    id: 'A_SELECTOR',
    dimension: 'Exact A anchor/candle',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['01:02:41–01:04:32 worked example', 'G338 structural anchor audit'],
    sufficientEvidenceRequirement: 'An authoritative source label or unambiguous chart convention identifying the exact A event/candle and its price endpoint.',
  },
  {
    id: 'B_SELECTOR',
    dimension: 'Exact B anchor/candle',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['01:02:41–01:04:32 worked example', 'G338 structural anchor audit'],
    sufficientEvidenceRequirement: 'An authoritative source label or unambiguous chart convention identifying the exact B event/candle and its price endpoint.',
  },
  {
    id: 'PRICE_FIELDS',
    dimension: 'A/B/C price field',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['01:04:00–01:04:32 parent-leg measurement', 'G337 wick/body audit'],
    sufficientEvidenceRequirement: 'Explicit source instruction or unambiguous repeated convention selecting high, low, open, close, or a defined body endpoint.',
  },
  {
    id: 'C_ANCHOR',
    dimension: 'Exact C structural anchor',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['38:38–39:48 pending-limit correction entry', '01:02:41–01:04:32 worked example', 'G336 anchor semantics audit'],
    sufficientEvidenceRequirement: 'An authoritative definition tying C to a uniquely identifiable correction event/price, independently of the eventual fill marker.',
  },
  {
    id: 'WICK_BODY',
    dimension: 'Wick/body convention',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['01:04:19–01:04:32 measurement example', 'G337 wick/body audit'],
    sufficientEvidenceRequirement: 'Explicit source wording or a chart convention that unambiguously distinguishes wick endpoint from candle-body endpoint for the relevant anchors.',
  },
  {
    id: 'SCALE',
    dimension: 'Parent vs nested structural scale selection',
    status: 'SOURCE_SUPPORTED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['01:02:52–01:04:32 worked example', 'G338 structural anchor audit'],
    sufficientEvidenceRequirement: 'An authoritative rule for selecting the executable parent scale when multiple nested 2-leg structures coexist.',
  },
  {
    id: 'D_FORMULA',
    dimension: 'Executable D formula',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['36:59–37:08 AB=CD slide', '01:02:52–01:04:32 worked example'],
    sufficientEvidenceRequirement: 'An explicit source equation or unambiguous labelled chart mapping A/B/C to D in executable price terms.',
  },
  {
    id: 'TOLERANCE',
    dimension: 'AB=CD equality tolerance',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['36:59–37:08 AB=CD slide'],
    sufficientEvidenceRequirement: 'An explicit source tolerance, acceptance band, or exact-equality convention for determining whether AB equals CD.',
  },
  {
    id: 'TP_MAPPING',
    dimension: 'TP1/TP2 relationship to D',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['41:26–42:37 TP1/TP2 and R terminology', '43:27–44:29 round/trend-level spacing', 'G335 risk-reward audit'],
    sufficientEvidenceRequirement: 'An explicit source mapping from D to TP1 and/or TP2, including any partial/extension rule.',
  },
  {
    id: 'P_GAP',
    dimension: 'Executable P-Gap formula',
    status: 'UNRESOLVED',
    outcome: 'NOT_RESOLVED',
    authoritativeReferences: ['36:59–37:08 Valid BO = P-Gap slide', 'G329 visual audit'],
    sufficientEvidenceRequirement: 'An explicit source definition or unambiguous annotated example specifying P-Gap endpoints, candle count, price fields, and any minimum/overlap condition.',
  },
  {
    id: 'AB_EQ_CD_SEMANTIC',
    dimension: 'AB=CD semantic relationship',
    status: 'SOURCE_CONFIRMED',
    outcome: 'RESOLVED',
    authoritativeReferences: ['36:59–37:08 explicit AB=CD slide'],
    sufficientEvidenceRequirement: 'Already satisfied by explicit source teaching; executable anchor mapping remains a separate unresolved dimension.',
  },
  {
    id: 'FILL_AS_C',
    dimension: 'Fill price as geometric C',
    status: 'EXPLICITLY_REJECTED',
    outcome: 'SOURCE_REJECTED',
    authoritativeReferences: ['01:04:19–01:04:32 pending-limit movement/activation and later parent-leg measurement', 'G333/G336 audits'],
    sufficientEvidenceRequirement: 'No further evidence required to keep the research negative control; source evidence must not be used to promote fill-as-C.',
  },
];

export const G345_UNRESOLVED_IDS = G345_SOURCE_EVIDENCE_MATRIX
  .filter((row) => row.outcome === 'NOT_RESOLVED')
  .map((row) => row.id);

export function g345EveryUnresolvedDimensionHasEvidenceRequirement(): boolean {
  return G345_SOURCE_EVIDENCE_MATRIX
    .filter((row) => row.outcome === 'NOT_RESOLVED')
    .every((row) => row.sufficientEvidenceRequirement.trim().length > 0);
}

export function g345NoUnresolvedDimensionIsMarkedResolved(): boolean {
  return G345_SOURCE_EVIDENCE_MATRIX
    .filter((row) => row.outcome === 'NOT_RESOLVED')
    .every((row) => row.status === 'UNRESOLVED' || row.status === 'SOURCE_SUPPORTED');
}
