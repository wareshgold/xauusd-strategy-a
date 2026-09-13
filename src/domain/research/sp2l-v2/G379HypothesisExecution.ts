export type HypothesisFamily = 'PGAP' | 'ABCD' | 'ENTRY' | 'SL' | 'TP';
export type HypothesisStatus = 'SOURCE-SUPPORTED-CONCEPT' | 'SOURCE-CONSISTENT' | 'SOURCE-UNRESOLVED';

export interface G379Hypothesis {
  id: string;
  family: HypothesisFamily;
  status: HypothesisStatus;
  canonical: false;
  unresolvedDimensions: readonly string[];
}

export const G379_HYPOTHESES: readonly G379Hypothesis[] = [
  { id:'PG-H01', family:'PGAP', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['P-Gap endpoint relation','wick/body treatment','overlap','minimum size'] },
  { id:'PG-H02', family:'PGAP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['exact endpoints','wick/body treatment','overlap','minimum size'] },
  { id:'PG-H03', family:'PGAP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['exact endpoints','exact sequence boundary'] },
  { id:'PG-H04', family:'PGAP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['exact endpoints','exact sequence boundary'] },
  { id:'ABCD-H01', family:'ABCD', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['A/B/C/D anchor definition'] },
  { id:'ABCD-H02', family:'ABCD', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['A/B/C/D anchor definition'] },
  { id:'ABCD-H03', family:'ABCD', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['A/B/C/D anchor definition','wick/body field'] },
  { id:'ABCD-H04', family:'ABCD', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['A/B/C/D anchor definition'] },
  { id:'ABCD-H05', family:'ABCD', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['parent-leg selection rule'] },
  { id:'ABCD-H06', family:'ABCD', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['nested/deeper-leg selection rule'] },
  { id:'EN-H01', family:'ENTRY', status:'SOURCE-SUPPORTED-CONCEPT', canonical:false, unresolvedDimensions:['exact limit price'] },
  { id:'EN-H02', family:'ENTRY', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['exact structural correction point'] },
  { id:'EN-H03', family:'ENTRY', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['candidate C definition','exact limit price'] },
  { id:'EN-H04', family:'ENTRY', status:'SOURCE-SUPPORTED-CONCEPT', canonical:false, unresolvedDimensions:['fill semantics','relationship between trigger/fill and C'] },
  { id:'SL-H01', family:'SL', status:'SOURCE-SUPPORTED-CONCEPT', canonical:false, unresolvedDimensions:['exact OHLC boundary'] },
  { id:'SL-H02', family:'SL', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['wick/body boundary'] },
  { id:'SL-H03', family:'SL', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['exact invalidation boundary'] },
  { id:'SL-H04', family:'SL', status:'SOURCE-UNRESOLVED', canonical:false, unresolvedDimensions:['offset definition'] },
  { id:'TP-H01', family:'TP', status:'SOURCE-SUPPORTED-CONCEPT', canonical:false, unresolvedDimensions:['A/B/C/D anchors','projection execution'] },
  { id:'TP-H02', family:'TP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['TP1/R1 mapping'] },
  { id:'TP-H03', family:'TP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['TP2/R2 mapping'] },
  { id:'TP-H04', family:'TP', status:'SOURCE-SUPPORTED-CONCEPT', canonical:false, unresolvedDimensions:['mapping to AB=CD/TP1/TP2'] },
  { id:'TP-H05', family:'TP', status:'SOURCE-CONSISTENT', canonical:false, unresolvedDimensions:['whether example outcomes are selectable or fixed'] },
] as const;

export const G379_REQUIRED_IDS = [
  'PG-H01','PG-H02','PG-H03','PG-H04',
  'ABCD-H01','ABCD-H02','ABCD-H03','ABCD-H04','ABCD-H05','ABCD-H06',
  'EN-H01','EN-H02','EN-H03','EN-H04',
  'SL-H01','SL-H02','SL-H03','SL-H04',
  'TP-H01','TP-H02','TP-H03','TP-H04','TP-H05',
] as const;

export function g379HypothesisRegistryIsComplete(): boolean {
  const ids = G379_HYPOTHESES.map((h) => h.id);
  return G379_REQUIRED_IDS.every((id) => ids.includes(id))
    && new Set(ids).size === ids.length
    && ids.length === G379_REQUIRED_IDS.length;
}

export function g379AllNonCanonical(): boolean {
  return G379_HYPOTHESES.every((h) => h.canonical === false);
}

export function g379HasUnresolvedGeometry(): boolean {
  return G379_HYPOTHESES.some((h) => h.unresolvedDimensions.length > 0);
}

export function g379GateDecision(): 'FROZEN-GEOMETRY-BLOCKED' | 'INVALID-REGISTRY' {
  if (!g379HypothesisRegistryIsComplete() || !g379AllNonCanonical()) return 'INVALID-REGISTRY';
  return 'FROZEN-GEOMETRY-BLOCKED';
}
