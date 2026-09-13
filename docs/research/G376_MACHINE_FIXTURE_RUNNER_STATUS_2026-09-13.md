# G376 — Machine Fixture Runner Status

Date: 2026-09-13
Status: IMPLEMENTED / CI-EXECUTED / RESEARCH-ONLY
Canonical: false

## Scope
G376 converts the existing G369 16-case minimal-pair research set into a deterministic TypeScript fixture runner with Vitest coverage.

## Implemented artifacts
- `src/domain/research/sp2l-v2/G376HypothesisFixtureRunner.ts`
- `tests/sp2l-v2-g376-hypothesis-fixture-runner.test.ts`
- `.github/workflows/research-sp2l-g376-fixture-runner.yml`

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

## CI execution
GitHub Actions executed the G376 target successfully on commit `cb3e06deb654b2fc2cca263caed8f349be913a11`.

- Workflow: `Research - SP2L G376 Hypothesis Fixture Runner`
- Run: `#3` / run ID `34740570213`
- Conclusion: `success`
- The same commit also passed `Research - SP2L Semantic V2 #40` and `Research - SP2L G4/G5 Fixture Suite #26`.

This establishes CI execution of the TypeScript build/test target. It does not turn the declared fixture classifications into source-confirmed Strategy A rules.

## Gate decision
G376 implementation: PASS.
G376 CI runtime execution: PASS.
Frozen geometry: BLOCKED.
Canonical Strategy A DEV: BLOCKED.
Production/live: BLOCKED.

## Next step
Proceed with G372/G373 primary-source acquisition against the remaining geometry blockers. A machine-generated fixture-result artifact may be added later if needed for auditability; it is not treated as evidence for source interpretation.
