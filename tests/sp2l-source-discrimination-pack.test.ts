import {describe,expect,it} from "vitest";
import {FIXTURES,discriminationPack,assertNoCanonicalSelection} from "../research/harness/sp2l_source_discrimination_pack_v1";
describe("SP2L source discrimination pack",()=>{
it("covers F10/F11/F12/F14",()=>{expect(new Set(FIXTURES.map(f=>f.blocker))).toEqual(new Set(["F10","F11","F12","F14"]));expect(FIXTURES.length).toBe(9);});
it("retains competing interpretations",()=>{assertNoCanonicalSelection(discriminationPack());for(const f of FIXTURES)expect(f.candidateInterpretations.length).toBeGreaterThanOrEqual(2);});
it("contains no canonical or performance selector",()=>{const s=JSON.stringify(FIXTURES);expect(s).not.toContain("CANONICAL");expect(s).not.toContain("SOURCE_CONFIRMED");for(const f of FIXTURES){expect(f.observations).not.toHaveProperty("winRate");expect(f.observations).not.toHaveProperty("profitFactor");}});
});