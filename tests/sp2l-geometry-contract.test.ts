import {
  assertCanonicalGeometryFrozen,
  createResearchCandidate,
} from '../research/harness/sp2l_geometry_contract_v1';

function expectThrow(fn: () => void): void {
  let threw = false;
  try {
    fn();
  } catch {
    threw = true;
  }
  if (!threw) throw new Error('Expected function to throw');
}

const candidate = createResearchCandidate();
expectThrow(() => assertCanonicalGeometryFrozen(candidate));

const resolved = createResearchCandidate();
for (const key of Object.keys(resolved) as Array<keyof typeof resolved>) {
  resolved[key] = { provenance: 'SOURCE_CONFIRMED' };
}
assertCanonicalGeometryFrozen(resolved);
