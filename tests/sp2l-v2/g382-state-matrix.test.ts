import {describe,expect,it} from 'vitest';
import {G382_SCENARIOS,g382ExpectedResultsAreStable,g382GateDecision,g382HasAllRequiredStates,g382StateMatrixIsNonCanonical,runG382} from '../../src/domain/research/sp2l-v2/G382StateMatrix.js';
describe('G382 state-transition counterfactual matrix',()=>{
 it('covers the full research state path',()=>expect(g382HasAllRequiredStates()).toBe(true));
 it('keeps all scenarios non-canonical',()=>expect(g382StateMatrixIsNonCanonical()).toBe(true));
 it('preserves declared classifications',()=>{expect(G382_SCENARIOS).toHaveLength(8);expect(g382ExpectedResultsAreStable()).toBe(true);expect(runG382().filter(x=>x.observed==='DISTINCT')).toHaveLength(5);expect(runG382().filter(x=>x.observed==='UNDERDETERMINED')).toHaveLength(2);expect(runG382().filter(x=>x.observed==='EQUIVALENT')).toHaveLength(1)});
 it('does not open frozen geometry',()=>expect(g382GateDecision()).toBe('FROZEN-GEOMETRY-BLOCKED'));
});
