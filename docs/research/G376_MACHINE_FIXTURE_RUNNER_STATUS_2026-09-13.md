# G376 — Machine Fixture Runner Status

Date: 2026-09-13
Status: IMPLEMENTED / RESEARCH-ONLY
Canonical: false

## Scope
G376 converts the existing G369 16-case minimal-pair research set into a deterministic TypeScript fixture runner with Vitest coverage.

## Implemented artifacts
- `src/domain/research/sp2l-v2/G376HypothesisFixtureRunner.ts`
- `tests/sp2l-v2-g376-hypothesis-fixture-runner.test.ts`

## Guardrails
- All fixtures remain `canonical=false`.
- No historical performance is used for source interpretation.
- Generic gap geometry is not promoted to P-Gap.
- `C = fill_price` is not assumed.
- Fixed 2R/3R, invented tolerances/offsets/candle counts, and MA/session gates remain non-canonical.
- Trigger, pending-order state, and fill remain distinct research states.
- Parent and nested legs remain separate candidates.

## Classification set
The runner records the declared research classification for each minimal pair as `DISTINCT`, `EQUIVALENT`, `SOURCE-CONFLICT`, or `UNDERDETERMINED`.

## Execution honesty
The runner and Vitest test file have been committed, but this GitHub-only step does not itself execute Node/Vitest. Therefore no claim of green local test execution is made in this status artifact.

## Gate decision
G376 implementation: PASS.
G376 runtime execution: PENDING until an executable CI/runner environment produces a recorded result artifact.
Frozen geometry: BLOCKED.
Production/live: BLOCKED.

## Next step
Run the new test target in CI or an available code-execution environment, capture the machine-generated JSON result matrix, then reconcile the resulting classifications against G372/G373 primary-source acquisition before any canonical freeze.
