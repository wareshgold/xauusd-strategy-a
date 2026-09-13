export type ResultClass = 'DISTINCT' | 'EQUIVALENT' | 'SOURCE-CONFLICT' | 'UNDERDETERMINED';

export interface G376Fixture {
  id: string;
  family: 'PGAP' | 'ABCD' | 'ENTRY' | 'SL' | 'TP';
  changedVariable: string;
  hypothesisA: string;
  hypothesisB: string;
  expected: ResultClass;
  canonical: false;
  rationale: string;
}

export const G376_FIXTURES: readonly G376Fixture[] = [
  { id:'PG-MP-01', family:'PGAP', changedVariable:'gap endpoint indexing', hypothesisA:'PG-H01', hypothesisB:'PG-H02', expected:'DISTINCT', canonical:false, rationale:'Endpoint interpretation can change gap qualification; source does not resolve executable endpoints.' },
  { id:'PG-MP-02', family:'PGAP', changedVariable:'wick/body overlap', hypothesisA:'PG-H01', hypothesisB:'PG-H02', expected:'UNDERDETERMINED', canonical:false, rationale:'Source distinguishes Pressure Gap semantically but does not define wick/body overlap rules.' },
  { id:'PG-MP-03', family:'PGAP', changedVariable:'pressure context', hypothesisA:'PG-H01', hypothesisB:'PG-H02', expected:'DISTINCT', canonical:false, rationale:'Generic gap and pressure-context interpretations classify the same gap differently.' },
  { id:'PG-MP-04', family:'PGAP', changedVariable:'timing sequence', hypothesisA:'PG-H03', hypothesisB:'PG-H04', expected:'DISTINCT', canonical:false, rationale:'Both timing variants are source-described; they are distinct candidate sequences.' },
  { id:'AB-MP-01', family:'ABCD', changedVariable:'anchor type', hypothesisA:'ABCD-H01', hypothesisB:'ABCD-H02', expected:'DISTINCT', canonical:false, rationale:'Swing extremes and candle boundaries can yield different Leg 1 magnitude.' },
  { id:'AB-MP-02', family:'ABCD', changedVariable:'wick/body field', hypothesisA:'ABCD-H01', hypothesisB:'ABCD-H03', expected:'DISTINCT', canonical:false, rationale:'Wick extreme and body/close endpoints can produce different measurements.' },
  { id:'AB-MP-03', family:'ABCD', changedVariable:'correction depth', hypothesisA:'ABCD-H01', hypothesisB:'ABCD-H05', expected:'DISTINCT', canonical:false, rationale:'Shallow and deep parent corrections can select different first-leg scales.' },
  { id:'AB-MP-04', family:'ABCD', changedVariable:'leg scale', hypothesisA:'ABCD-H05', hypothesisB:'ABCD-H06', expected:'DISTINCT', canonical:false, rationale:'Parent and nested/deeper legs are explicitly separate research scales.' },
  { id:'EN-MP-01', family:'ENTRY', changedVariable:'trigger versus fill', hypothesisA:'EN-H01', hypothesisB:'EN-H04', expected:'DISTINCT', canonical:false, rationale:'A corrective trigger can occur before a later pending-limit fill.' },
  { id:'EN-MP-02', family:'ENTRY', changedVariable:'C timing', hypothesisA:'EN-H03', hypothesisB:'EN-H04', expected:'UNDERDETERMINED', canonical:false, rationale:'Source does not establish whether geometric C equals, precedes, or follows fill.' },
  { id:'EN-MP-03', family:'ENTRY', changedVariable:'pending order state', hypothesisA:'EN-H01', hypothesisB:'EN-H04', expected:'DISTINCT', canonical:false, rationale:'A trigger event does not imply that a pending order was filled.' },
  { id:'SL-MP-01', family:'SL', changedVariable:'origin wick versus body', hypothesisA:'SL-H01', hypothesisB:'SL-H02', expected:'DISTINCT', canonical:false, rationale:'Origin structural boundary and origin extreme can differ when wick extends beyond body.' },
  { id:'SL-MP-02', family:'SL', changedVariable:'invalidation boundary', hypothesisA:'SL-H02', hypothesisB:'SL-H03', expected:'DISTINCT', canonical:false, rationale:'Structural invalidation may differ from the raw origin extreme; exact boundary remains unresolved.' },
  { id:'TP-MP-01', family:'TP', changedVariable:'target construction', hypothesisA:'TP-H01', hypothesisB:'TP-H04', expected:'SOURCE-CONFLICT', canonical:false, rationale:'AB=CD is source-supported in the lesson while the official page states default TP 1:1; reconciliation is unresolved.' },
  { id:'TP-MP-02', family:'TP', changedVariable:'target hierarchy', hypothesisA:'TP-H02', hypothesisB:'TP-H03', expected:'DISTINCT', canonical:false, rationale:'Lesson distinguishes first and second reward targets, but mapping is not frozen.' },
  { id:'TP-MP-03', family:'TP', changedVariable:'C/fill price', hypothesisA:'TP-H01', hypothesisB:'EN-H04', expected:'UNDERDETERMINED', canonical:false, rationale:'Leg projection can vary with candidate C or actual fill; source forbids assuming they are identical.' }
];

export function runG376(): readonly G376Fixture[] {
  return G376_FIXTURES;
}

export function g376AllNonCanonical(): boolean {
  return G376_FIXTURES.every((fixture) => fixture.canonical === false);
}
