# SP2L Batch 5A — Regression Execution Checkpoint — 2026-09-16

## Scope

This checkpoint records the engineering execution gate for Batch 5A. It does not promote any unresolved source geometry into the canonical rule set.

## Completed in this pass

1. Audited the existing forensic workflow.
2. Confirmed the existing forensic workflow is `workflow_dispatch`-only and checks out `main`; it is therefore not a valid Batch 5A branch-regression gate.
3. Added `.github/workflows/research-sp2l-batch5a-regression.yml` on `research/sp2l-batch5-source-boundary-2026-09-16`.
4. The new workflow is scoped to the Batch 5A branch and runs:
   - dependency installation;
   - TypeScript build;
   - full deterministic `npm test` suite;
   - explicit source-boundary assertions;
   - explicit F8-F15 synthetic fixture registry tests;
   - a fail-closed gate summary with production OFF.

## Execution status

The workflow definition was committed as:

`18ddec4c1274a361d6658903a164f2ccecc12840`

A GitHub Actions run for this exact Batch 5A workflow/commit has not yet been independently observed through the available workflow-run interface in this session. Therefore:

**Batch 5A regression execution = NOT VERIFIED**

No PASS is claimed from the workflow definition alone.

## Source-boundary status

- C01 P-Gap: unresolved exact executable geometry.
- C02 SL geometry: unresolved exact structural OHLC/wick-body/buffer semantics.
- C03 AB=CD: unresolved exact A/B/C/D anchors and tolerance.
- C04 TP/2X: unresolved exact numeric semantics.
- C05 context: unresolved canonical filter semantics/parameters.
- C06 pending refresh: unresolved exact replacement condition.
- C07 trigger: unresolved exact classifier.
- C08 correction/invalidation: unresolved exact swing/OHLC/breach semantics.
- F08, F10, F11, F12, F13, F14, F15: unresolved.
- F09: source-discriminated boundary only; not frozen geometry.

## Guardrails preserved

- No profitability/backtest selection used to resolve source ambiguity.
- No minimum-risk filter introduced.
- No stop buffer introduced.
- No wick/body substitution introduced.
- No alternate swing anchor introduced.
- No P-Gap formula invented.
- No AB=CD tolerance invented.
- No pending-order replacement threshold invented.
- The documented 125R forensic case remains preserved.
- Production remains OFF.

## Next gate sequence

A. Obtain/verify an actual Batch 5A Actions run for the exact branch state.
B. Inspect its job/step evidence and record PASS/FAIL/NOT VERIFIED truthfully.
C. If deterministic regression passes, perform Freeze Reassessment only against source-discriminated semantics.
D. If source geometry remains unresolved, keep Frozen Geometry BLOCKED and continue Batch 6 source-discrimination work for F12/F14/F13 rather than freezing by performance.
