export type HypothesisEvidenceStatus = 'SOURCE-CONFIRMED' | 'SOURCE-SUPPORTED' | 'UNRESOLVED';

export interface HypothesisProvenance {
  id: string;
  component: 'P-GAP' | 'AB=CD' | 'ENTRY' | 'STOP' | 'TP';
  status: HypothesisEvidenceStatus;
  sourceRuleIds: readonly string[];
  canonicalEligible: false;
}

export const G395_HYPOTHESES: readonly HypothesisProvenance[] = [
  { id: 'PG-H01', component: 'P-GAP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'PG-H02', component: 'P-GAP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'PG-H03', component: 'P-GAP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'PG-H04', component: 'P-GAP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'ABCD-H01', component: 'AB=CD', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'ABCD-H02', component: 'AB=CD', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'ABCD-H03', component: 'AB=CD', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'EN-H01', component: 'ENTRY', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'EN-H02', component: 'ENTRY', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'EN-H03', component: 'ENTRY', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'SL-H01', component: 'STOP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'SL-H02', component: 'STOP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'TP-H01', component: 'TP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false },
  { id: 'TP-H04', component: 'TP', status: 'UNRESOLVED', sourceRuleIds: [], canonicalEligible: false }
];

export function getHypothesisProvenance(id: string): HypothesisProvenance | undefined {
  return G395_HYPOTHESES.find((hypothesis) => hypothesis.id === id);
}

export function assertResearchOnly(hypothesis: HypothesisProvenance): void {
  if (hypothesis.canonicalEligible !== false || hypothesis.status === 'SOURCE-CONFIRMED') {
    throw new Error(`G396 research guard violation: ${hypothesis.id}`);
  }
}
