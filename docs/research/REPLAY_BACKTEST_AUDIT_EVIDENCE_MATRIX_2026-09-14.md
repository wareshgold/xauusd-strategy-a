# Replay/Backtest Audit — Evidence Matrix — 2026-09-14

## Status

**AUDIT-CLOSED — infrastructure/research-governance audit only.**

Audited commit: `c455df8da3b8103578d5bff66f957b1f117c0575`

This matrix maps each finite Replay/Backtest Audit exit criterion to concrete implementation and test evidence. It does not canonicalize Strategy A geometry and does not authorize validation or production.

| # | Criterion | Evidence | Status |
|---|---|---|---|
| 1 | Chronology | CSV replay rejects duplicate/backward timestamps; deterministic engine rejects non-monotonic input. | PASS |
| 2 | Look-ahead | Backtest fixtures cover history lengths `[1,2,3]`, prevent same-candle pending fill, and prevent same-candle post-fill exit. | PASS |
| 3 | Signal accounting | Backtest fixtures cover SIGNAL/BLOCKED/NO_SIGNAL accounting and ensure blocked decisions are not submitted. | PASS |
| 4 | Identity | Duplicate execution identities are rejected while pending, active, and after closure. | PASS |
| 5 | Pending lifecycle | Creation, next-candle fill, cancellation, and unresolved end-of-series pending state are tested. | PASS |
| 6 | Intrabar ambiguity | Stop+target touched on the same candle is represented as `AMBIGUOUS`; no ordering is invented. | PASS |
| 7 | Input integrity | CSV tests cover required columns, column count, finite OHLC, OHLC validity, timezone, ordering, configured timeframe, and gap preservation. | PASS |
| 8 | Ledger/metrics | Finite-value invariants, cancellation handling, deterministic realized-R metrics, and ledger behavior are tested; no optimization path is part of the audit. | PASS |
| 9 | Manifest | Deterministic run-manifest serialization is covered by focused tests. | PASS |
| 10 | Scope Guard | Replay/backtest scope guard completed successfully with no guarded Strategy A geometry hit requiring manual review. | PASS |
| 11 | Fixture coverage | Focused synthetic fixtures cover deterministic engine, backtest runner, execution simulator, CSV replay, metrics, and manifest behavior. | PASS |
| 12 | CI | Foundation CI run #65 (`34822931373`) on audited commit `c455df8...`: typecheck and focused tests succeeded. | PASS |
| 13 | Clean boundary | Final diff review from baseline `f56e73a...` to audited commit found infrastructure/tests/governance only; no new P-Gap, AB=CD, fill, stop/target, or Strategy A geometry rule. | PASS |
| 14 | Documentation | Exit criteria, evidence matrix, closure template, scope guard, and governance records are present; this matrix identifies the exact audited commit and unresolved semantics. | PASS |

## Known unresolved semantics

The following remain explicitly unresolved and are not inferred from the replay audit:

- P-Gap geometry/formula
- A/B/C/D anchors
- AB=CD tolerance
- canonical pending-limit fill-price semantics
- canonical stop/target geometry
- Strategy A session/time constraints unless separately source-confirmed

`TOUCH_ENTRY` remains a research execution hypothesis only. `UNRESOLVED` remains the safe default until source meaning is frozen.

## Audit boundary

This closure is infrastructure/research governance only. It does not establish that Strategy A is canonical, profitable, validation-ready, Fresh-Holdout-ready, or production-ready.

## Next gate

Proceed only to the next explicitly authorized research gate: **source resolution / geometry freeze readiness**. No Strategy A geometry may become canonical without source evidence and explicit manual approval by Ali.
