# Replay/Backtest Audit — Evidence Matrix — 2026-09-14

## Status

**AUDIT-OPEN — evidence pass in progress.**

This matrix maps each finite Replay/Backtest Audit exit criterion to concrete implementation and test evidence. It does not canonicalize Strategy A geometry and does not authorize validation or production.

| # | Criterion | Evidence | Status | Remaining action |
|---|---|---|---|---|
| 1 | Chronology | `tests/csv-replay.test.ts`: duplicate/backward timestamp rejection; `tests/deterministic-engine.test.ts`: non-monotonic engine input rejection | PASS | None identified |
| 2 | Look-ahead | `tests/backtest-runner.test.ts`: history lengths `[1,2,3]`; signal-candle pending fill prevented; fill-candle exit prevented | PASS | None identified |
| 3 | Signal accounting | `tests/backtest-runner.test.ts`: blocked decisions are not submitted; SIGNAL/NO_SIGNAL/blocked counters exercised | PASS | None identified |
| 4 | Identity | `tests/backtest-runner.test.ts`: duplicate IDs rejected while pending, active, and after closure | PASS | None identified |
| 5 | Pending lifecycle | `tests/backtest-runner.test.ts`: pending creation, next-candle fill, cancellation, and end-of-series pending state | PASS | None identified |
| 6 | Intrabar ambiguity | `tests/backtest-runner.test.ts`: both stop and target touched => `AMBIGUOUS`, trade remains open | PASS | None identified |
| 7 | Input integrity | `tests/csv-replay.test.ts`: required OHLC parsing, finite values, OHLC geometry, explicit timezone, source ordering, configured timeframe, and gap preservation | PASS | None identified |
| 8 | Ledger/metrics | `tests/backtest-runner.test.ts`: finite-value rejection, cancellation metrics, deterministic realized-R metrics; no optimization path in audit scope | PASS | None identified |
| 9 | Manifest | `tests/backtest-runner.test.ts`: deterministic manifest serialization; `src/replay/run-manifest.ts` is included in foundation scope | PASS | Final audited commit must retain manifest evidence |
| 10 | Scope Guard | Workflow run `34822520311`, run #4: scope guard completed successfully; manual-review warning step skipped because no guarded hit occurred | PASS | None identified |
| 11 | Fixture coverage | Focused synthetic fixtures exist across deterministic engine, backtest runner, execution simulator, CSV replay, metrics and manifest behavior | PASS* | Perform final source/test inventory before closure |
| 12 | CI | Foundation CI run `34822520368`, run #62: typecheck and focused tests passed | PASS | Re-run on final audited commit if any audit evidence changes |
| 13 | Clean boundary | Scope Guard covers replay/backtest/execution paths for Strategy A geometry terms; current audit changes are governance/infrastructure only | PASS* | Final diff review required before closure |
| 14 | Documentation | Exit criteria and closure template exist; this evidence matrix is the working audit record | PASS* | Produce final closure record only after final diff/CI review |

## Known unresolved semantics

The following remain explicitly unresolved and are not to be inferred from the replay audit:

- P-Gap geometry/formula
- A/B/C/D anchors
- AB=CD tolerance
- canonical pending-limit fill-price semantics
- canonical stop/target geometry
- Strategy A session/time constraints unless separately source-confirmed

`TOUCH_ENTRY` is a research execution hypothesis only. `UNRESOLVED` remains the safe default until source meaning is frozen.

## Audit boundary

This evidence matrix is infrastructure/research governance only. It does not establish that Strategy A is canonical, profitable, validation-ready, or production-ready.

## Closure rule

The matrix may be promoted from `AUDIT-OPEN` to `AUDIT-CLOSED` only after the final audited commit has direct evidence for all 14 criteria, the final scoped CI passes, the final diff is reviewed for Strategy A geometry contamination, and the closure record identifies the exact audited commit SHA.
