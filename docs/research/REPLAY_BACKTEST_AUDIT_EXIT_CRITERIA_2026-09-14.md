# Replay/Backtest Audit — Finite Exit Criteria

## Purpose
Close the Replay/Backtest Audit only when the deterministic replay/backtest infrastructure has a finite, reviewable evidence set. This gate does not freeze Strategy A geometry and does not authorize validation, Fresh Holdout, or production.

## Scope
The audit covers only:
- chronological candle processing and no look-ahead;
- deterministic signal/blocked/no-signal accounting;
- deterministic pending-order lifecycle;
- duplicate identity rejection;
- end-of-series behavior;
- explicit ambiguous intrabar behavior;
- CSV timestamp/timezone/OHLC integrity;
- deterministic trade ledger and descriptive metrics;
- deterministic run-manifest fields/serialization;
- replay/backtest scope protection;
- focused unit/synthetic fixtures and CI reproducibility.

It must not add or select Strategy A geometry, P-Gap formulas, A/B/C/D anchors, AB=CD tolerances, fill-price semantics, stop/target geometry, or session rules.

## Required Exit Conditions
All conditions below must be satisfied on the audited branch:

1. **Chronology:** non-monotonic/duplicate candle timestamps are rejected; processing is strictly chronological.
2. **Look-ahead:** engine decisions use only history available through the current candle; same-candle pending fills and same-candle post-fill exits are explicitly prevented by the execution contract.
3. **Signal accounting:** SIGNAL, BLOCKED, and NO_SIGNAL paths are mutually accounted for and blocked decisions never reach execution.
4. **Identity:** duplicate signal/execution identities are rejected deterministically, including reuse after closure where applicable.
5. **Pending lifecycle:** creation, pending state, fill, cancellation, and unresolved end-of-series state are deterministic and tested.
6. **Intrabar ambiguity:** a candle touching both stop and target does not receive an invented ordering; the result is explicitly AMBIGUOUS/unresolved.
7. **Input integrity:** CSV parsing enforces required fields, finite OHLC values, valid candle geometry, explicit timezone, and source ordering without synthesizing missing candles.
8. **Ledger/metrics:** ledger invariants and descriptive metrics are deterministic; no parameter optimization or strategy selection is performed by the audit.
9. **Manifest:** run metadata has deterministic serialization and enough identifiers to reproduce the dataset/run context.
10. **Scope Guard:** guarded replay/execution paths are automatically scanned for sensitive Strategy A geometry terms; hits require manual review and do not auto-canonicalize anything.
11. **Fixture coverage:** each audit condition has at least one focused deterministic test or synthetic fixture demonstrating pass/rejection behavior where applicable.
12. **CI:** scoped typecheck and focused tests pass on the final audited commit.
13. **Clean boundary:** the final audit diff contains no new Strategy A geometry or source-meaning decision without explicit manual approval.
14. **Documentation:** the final audit result records commit SHA, tests, known unresolved semantics, and any accepted limitations.

## Closure Decision
The audit may be marked **AUDIT-CLOSED** only when conditions 1–14 are evidenced. If any condition is missing, status remains **AUDIT-OPEN**.

Closure is an infrastructure/research-governance decision only. It does not mean Strategy A is canonical, profitable, validation-ready, or production-ready.

## Required Final Record
The closure record must state:
- audited commit SHA;
- scope covered;
- tests/CI run identifiers;
- PASS/FAIL result for conditions 1–14;
- unresolved execution/source semantics;
- confirmation that no Strategy A geometry was canonicalized;
- next gate in the project workflow.

## Next Gate
After AUDIT-CLOSED, work may proceed to the next explicitly authorized research gate. Strategy geometry remains governed by source evidence and manual canonicalization.
