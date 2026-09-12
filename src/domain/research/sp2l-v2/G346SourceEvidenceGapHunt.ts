export type G346EvidenceStatus =
  | 'SOURCE_CONFIRMED'
  | 'SOURCE_SUPPORTED'
  | 'UNRESOLVED'
  | 'EXPLICITLY_REJECTED';

export type G346Gap = {
  id: string;
  status: G346EvidenceStatus;
  existingEvidence: string;
  resolutionRequirement: string;
  resolvedByCurrentSource: boolean;
};

export const G346_GAPS: G346Gap[] = [
  { id: 'A_ANCHOR', status: 'UNRESOLVED', existingEvidence: 'Deep-leg origin is source-supported.', resolutionRequirement: 'Explicit A label or unambiguous endpoint convention.', resolvedByCurrentSource: false },
  { id: 'B_ANCHOR', status: 'UNRESOLVED', existingEvidence: 'Parent Leg-1 endpoint is visually discussed.', resolutionRequirement: 'Explicit B label or unambiguous endpoint convention.', resolvedByCurrentSource: false },
  { id: 'PRICE_FIELD', status: 'UNRESOLVED', existingEvidence: 'Visual ruler endpoints exist.', resolutionRequirement: 'Explicit high/low/open/close/body/wick convention.', resolvedByCurrentSource: false },
  { id: 'C_ANCHOR', status: 'UNRESOLVED', existingEvidence: 'Correction precedes pending-limit activation.', resolutionRequirement: 'Explicit correction event/price independent of fill.', resolvedByCurrentSource: false },
  { id: 'WICK_BODY', status: 'UNRESOLVED', existingEvidence: 'Examples are visually suggestive but unlabeled.', resolutionRequirement: 'Explicit wording or repeated unambiguous convention.', resolvedByCurrentSource: false },
  { id: 'PARENT_SCALE', status: 'SOURCE_SUPPORTED', existingEvidence: 'Parent and nested structures coexist.', resolutionRequirement: 'Explicit executable parent-scale selection rule.', resolvedByCurrentSource: false },
  { id: 'D_FORMULA', status: 'UNRESOLVED', existingEvidence: 'AB=CD is explicitly taught.', resolutionRequirement: 'Explicit executable A/B/C to D equation.', resolvedByCurrentSource: false },
  { id: 'ABCD_TOLERANCE', status: 'UNRESOLVED', existingEvidence: 'Equality relationship is taught.', resolutionRequirement: 'Explicit tolerance/acceptance band or exact-equality rule.', resolvedByCurrentSource: false },
  { id: 'TP_MAPPING', status: 'UNRESOLVED', existingEvidence: 'TP1/TP2 and R outcomes are labelled.', resolutionRequirement: 'Explicit D-to-TP1/TP2 mapping.', resolvedByCurrentSource: false },
  { id: 'P_GAP_FORMULA', status: 'UNRESOLVED', existingEvidence: 'Valid BO = P-Gap is explicitly shown.', resolutionRequirement: 'Explicit endpoints, candle count, fields, and minimum/overlap rule.', resolvedByCurrentSource: false },
  { id: 'FILL_AS_C', status: 'EXPLICITLY_REJECTED', existingEvidence: 'Pending activation is distinct from later parent-leg measurement.', resolutionRequirement: 'No canonicalization of fill as geometric C.', resolvedByCurrentSource: false },
];

export function g346UnresolvedHaveRequirements(): boolean {
  return G346_GAPS.filter((gap) => gap.status === 'UNRESOLVED').every(
    (gap) => gap.resolutionRequirement.length > 0 && gap.resolvedByCurrentSource === false,
  );
}

export function g346NoNewResolvingEvidenceFound(): boolean {
  return G346_GAPS.every((gap) => gap.resolvedByCurrentSource === false);
}

export function g346SourceConfirmedConceptsRemain(): string[] {
  return ['AB=CD', 'Leg2≈Leg1', 'Pending-limit', 'Parent/nested hierarchy'];
}
