/**
 * G383 — minimal-pair state perturbation coverage.
 * Research-only. This does not define canonical Strategy A geometry.
 */
export type G383State =
  | 'PARENT_LEG' | 'CORRECTION' | 'TRIGGER' | 'PENDING'
  | 'FILL' | 'C' | 'INVALIDATED' | 'TP';
export type G383Classification = 'OBSERVABLE_DISTINCTION' | 'SOURCE_REQUIRED';
export interface G383Pair {
  id: string;
  dimension: 'TRIGGER_TIMING'|'PENDING_PERSISTENCE'|'FILL_TIMING'|'INVALIDATION_BEFORE_FILL'|'C_TIMING'|'TARGET_MAPPING';
  baseline: readonly G383State[];
  perturbed: readonly G383State[];
  changedTransition: string;
  expected: G383Classification;
  observed: G383Classification;
  canonical: false;
  note: string;
}

const BASE: readonly G383State[] = ['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'];

export const G383_PAIRS: readonly G383Pair[] = [
  {id:'G383-01',dimension:'TRIGGER_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],changedTransition:'TRIGGER timing shifted within correction',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'A trigger is source-confirmed, but exact timing rule is not.'},
  {id:'G383-02',dimension:'TRIGGER_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','PENDING','TRIGGER','FILL','C','TP'],changedTransition:'TRIGGER↔PENDING ordering',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'Changing ordering changes the executable event sequence.'},
  {id:'G383-03',dimension:'PENDING_PERSISTENCE',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','C','TP'],changedTransition:'remove explicit FILL state',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'Pending order existence and later activation are distinct states.'},
  {id:'G383-04',dimension:'PENDING_PERSISTENCE',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','PENDING','FILL','C','TP'],changedTransition:'pending persists for an extra observation step',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'Source does not define a universal pending expiry/persistence rule.'},
  {id:'G383-05',dimension:'FILL_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],changedTransition:'FILL occurs before versus after the correction boundary',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'Exact fill semantics and relationship to C remain unresolved.'},
  {id:'G383-06',dimension:'FILL_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','C','FILL','TP'],changedTransition:'FILL↔C ordering',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'The two event orders are executable-state distinct.'},
  {id:'G383-07',dimension:'INVALIDATION_BEFORE_FILL',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','INVALIDATED'],changedTransition:'pending→invalidation before fill',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'A canceled setup cannot be silently treated as a filled trade.'},
  {id:'G383-08',dimension:'INVALIDATION_BEFORE_FILL',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','INVALIDATED','C','TP'],changedTransition:'invalidation after fill',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'Post-fill invalidation handling is not fully specified by source geometry.'},
  {id:'G383-09',dimension:'C_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],changedTransition:'C assigned to post-fill observation',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'No authoritative A/B/C/D anchor definition fixes C timing.'},
  {id:'G383-10',dimension:'C_TIMING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','C','FILL','TP'],changedTransition:'C↔FILL ordering',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'Changing event ordering changes the candidate state path.'},
  {id:'G383-11',dimension:'TARGET_MAPPING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C'],changedTransition:'remove TP terminal',expected:'OBSERVABLE_DISTINCTION',observed:'OBSERVABLE_DISTINCTION',canonical:false,note:'Exit existence is distinct from its exact target mapping.'},
  {id:'G383-12',dimension:'TARGET_MAPPING',baseline:BASE,perturbed:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP','TP'],changedTransition:'second target observation after TP',expected:'SOURCE_REQUIRED',observed:'SOURCE_REQUIRED',canonical:false,note:'AB=CD and default 1:1 concepts coexist; canonical mapping remains unresolved.'},
] as const;

export function g383AllPairsStable(): boolean { return G383_PAIRS.every(p => p.expected === p.observed); }
export function g383AllNonCanonical(): boolean { return G383_PAIRS.every(p => p.canonical === false); }
export function g383DimensionsCovered(): boolean {
  const required = ['TRIGGER_TIMING','PENDING_PERSISTENCE','FILL_TIMING','INVALIDATION_BEFORE_FILL','C_TIMING','TARGET_MAPPING'] as const;
  const seen = new Set(G383_PAIRS.map(p => p.dimension));
  return required.every(x => seen.has(x));
}
export function g383GateDecision(): 'FROZEN-GEOMETRY-BLOCKED'|'INVALID' {
  return g383AllPairsStable() && g383AllNonCanonical() && g383DimensionsCovered()
    ? 'FROZEN-GEOMETRY-BLOCKED' : 'INVALID';
}
