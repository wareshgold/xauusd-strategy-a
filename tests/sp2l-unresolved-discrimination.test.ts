import { SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES } from "../research/fixtures/sp2l_unresolved_discrimination_v1.js";

const families = new Set(SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES.map((x: { family: string }) => x.family));
const expectedFamilies = ["F08","F09","F10","F11","F12","F13","F14","F15","PGAP"];

if (JSON.stringify([...families].sort()) !== JSON.stringify(expectedFamilies)) throw new Error("Unresolved fixture family coverage mismatch");
if (SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES.length !== 18) throw new Error("Expected exactly 18 unresolved discrimination fixtures");

for (const c of SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES) {
  if (c.expectedStatus !== "UNRESOLVED" || c.canonicalEligible !== false) throw new Error(`Fixture ${c.id} violated unresolved/canonicalization guard`);
  if (c.hypothesisA === c.hypothesisB) throw new Error(`Fixture ${c.id} does not distinguish competing hypotheses`);
}

export const SP2L_UNRESOLVED_DISCRIMINATION_TEST_PASSED = true;
