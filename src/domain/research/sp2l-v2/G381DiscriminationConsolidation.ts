export type G381Status = 'SOURCE-RESOLVED' | 'SOURCE-UNDERDETERMINED' | 'IMPLEMENTATION-DISTINCT' | 'SOURCE-CONFLICT';

export interface G381Dimension {
  id: string;
  family: 'PGAP' | 'ABCD' | 'ENTRY' | 'SL' | 'TP';
  status: G381Status;
  sourceCanonical: false;
  evidence: readonly string[];
}

export const G381_DIMENSIONS: readonly G381Dimension[] = [
  { id:'PGAP-ENDPOINTS', family:'PGAP', status:'SOURCE-UNDERDETERMINED', sourceCanonical:false, evidence:['G376 PG-MP-01 DISTINCT','G380 PG counterfactuals'] },
  { id:'PGAP-PRESSURE', family:'PGAP', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 PG-MP-03 DISTINCT','Pressure Gap semantics source-confirmed'] },
  { id:'PGAP-TIMING', family:'PGAP', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 PG-MP-04 DISTINCT','G380 PG-03 DISTINCT'] },
  { id:'ABCD-ANCHOR-FIELD', family:'ABCD', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 AB-MP-01 DISTINCT','G376 AB-MP-02 DISTINCT','G380 AB-01/02 DISTINCT'] },
  { id:'ABCD-PARENT-NESTED', family:'ABCD', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 AB-MP-03 DISTINCT','G376 AB-MP-04 DISTINCT'] },
  { id:'ENTRY-PRICE-FILL', family:'ENTRY', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 EN-MP-01 DISTINCT','G376 EN-MP-03 DISTINCT','G380 EN-01/02 DISTINCT'] },
  { id:'ENTRY-C-TIMING', family:'ENTRY', status:'SOURCE-UNDERDETERMINED', sourceCanonical:false, evidence:['G376 EN-MP-02 UNDERDETERMINED'] },
  { id:'SL-BOUNDARY', family:'SL', status:'IMPLEMENTATION-DISTINCT', sourceCanonical:false, evidence:['G376 SL-MP-01 DISTINCT','G376 SL-MP-02 DISTINCT','G380 SL-01 DISTINCT'] },
  { id:'TP-MAPPING', family:'TP', status:'SOURCE-CONFLICT', sourceCanonical:false, evidence:['G376 TP-MP-01 SOURCE-CONFLICT','G380 TP-01 DISTINCT','G380 TP-02 EQUIVALENT'] },
];

export function g381AllNonCanonical(): boolean {
  return G381_DIMENSIONS.every((d) => d.sourceCanonical === false);
}

export function g381HasSourceUnderDetermination(): boolean {
  return G381_DIMENSIONS.some((d) => d.status === 'SOURCE-UNDERDETERMINED');
}

export function g381HasSourceConflict(): boolean {
  return G381_DIMENSIONS.some((d) => d.status === 'SOURCE-CONFLICT');
}

export function g381GateDecision(): 'FROZEN-GEOMETRY-BLOCKED' | 'INVALID' {
  if (!g381AllNonCanonical() || !g381HasSourceUnderDetermination() || !g381HasSourceConflict()) return 'INVALID';
  return 'FROZEN-GEOMETRY-BLOCKED';
}
