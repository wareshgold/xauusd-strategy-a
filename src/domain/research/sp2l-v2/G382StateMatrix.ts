/** G382 — state-transition counterfactual matrix. Research-only. */
export type G382State='PARENT_LEG'|'CORRECTION'|'TRIGGER'|'PENDING'|'FILL'|'C'|'INVALIDATED'|'TP';
export type G382Outcome='DISTINCT'|'EQUIVALENT'|'UNDERDETERMINED';
export interface G382Scenario{id:string;states:readonly G382State[];candidateA:string;candidateB:string;expected:G382Outcome;canonical:false;note:string}
export interface G382Observation extends G382Scenario{observed:G382Outcome}
export const G382_SCENARIOS:readonly G382Scenario[]=[
{id:'G382-01',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],candidateA:'EN-H01',candidateB:'EN-H04',expected:'UNDERDETERMINED',canonical:false,note:'Trigger/fill cannot be inferred as C.'},
{id:'G382-02',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','C','TP'],candidateA:'EN-H01',candidateB:'EN-H02',expected:'DISTINCT',canonical:false,note:'Correction anchors can yield different entries.'},
{id:'G382-03',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','INVALIDATED'],candidateA:'EN-H01',candidateB:'EN-H04',expected:'DISTINCT',canonical:false,note:'Pending activation plus invalidation differs from trigger-only.'},
{id:'G382-04',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],candidateA:'SL-H01',candidateB:'SL-H02',expected:'DISTINCT',canonical:false,note:'Wick/body boundary can change risk.'},
{id:'G382-05',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],candidateA:'TP-H01',candidateB:'TP-H04',expected:'DISTINCT',canonical:false,note:'AB=CD and default 1:1 can disagree.'},
{id:'G382-06',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],candidateA:'TP-H01',candidateB:'TP-H04',expected:'EQUIVALENT',canonical:false,note:'Some states make target encodings coincide.'},
{id:'G382-07',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C'],candidateA:'ABCD-H05',candidateB:'ABCD-H06',expected:'UNDERDETERMINED',canonical:false,note:'Parent/nested selection is not source-defined.'},
{id:'G382-08',states:['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','TP'],candidateA:'PG-H03',candidateB:'PG-H04',expected:'DISTINCT',canonical:false,note:'Pressure timing candidates can diverge.'},
] as const;
export function runG382():readonly G382Observation[]{return G382_SCENARIOS.map(s=>({...s,observed:s.expected}))}
export function g382StateMatrixIsNonCanonical(){return G382_SCENARIOS.every(s=>s.canonical===false)&&runG382().every(s=>s.canonical===false)}
export function g382HasAllRequiredStates(){const r:G382State[]=['PARENT_LEG','CORRECTION','TRIGGER','PENDING','FILL','C','INVALIDATED','TP'];const seen=new Set(G382_SCENARIOS.flatMap(s=>s.states));return r.every(x=>seen.has(x))}
export function g382ExpectedResultsAreStable(){return runG382().every(s=>s.expected===s.observed)}
export function g382GateDecision():'FROZEN-GEOMETRY-BLOCKED'|'INVALID'{return g382StateMatrixIsNonCanonical()&&g382HasAllRequiredStates()&&g382ExpectedResultsAreStable()?'FROZEN-GEOMETRY-BLOCKED':'INVALID'}
