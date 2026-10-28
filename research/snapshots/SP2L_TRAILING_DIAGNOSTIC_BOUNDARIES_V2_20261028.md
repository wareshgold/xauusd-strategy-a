# Follow-up Snapshot — Trailing Diagnostic Boundary Coverage v2

- Snapshot ID: `SP2L-TRAILING-DIAGNOSTIC-BOUNDARIES-V2-20261028`
- Recorded: 2026-10-28
- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/position-64500649-m1-boundary-audit-20261028`
- Code/test commit validated: `e495925c6f22d128f2d27ec53a8c383185e4add7`
- Related PR: [#363](https://github.com/wareshgold/xauusd-strategy-a/pull/363), draft and unmerged.
- Prior snapshots: `SP2L_POSITION_64500649_ENTRY_BAR_AUDIT_SNAPSHOT_20261028.md` and `SP2L_ENTRY_BAR_TRAILING_FIXTURE_MATRIX_SNAPSHOT_20261028.md`.

## Added deterministic cases

- A pre-entry bar low is not labelled the demonstrated contamination pattern if the separately supplied post-entry Bid movement also reaches the activation threshold.
- The SELL Ask-distance guard rejects a candidate at the exact equality boundary `candidate_sl == minimum_ask + broker_distance`, matching the inspected strict greater-than condition.
- Earlier cases remain: the incident contamination case, exact post-entry activation boundary, below-threshold movement, and invalid timestamp relationships.

## Validation results

On commit `e495925c6f22d128f2d27ec53a8c383185e4add7`:
- SP2L forensic deterministic checks — run 626 — success.
- Factory Research Tests — run 1070 — success.

## Scope and interpretation limits

- These tests validate arithmetic and classification of supplied fixtures, not the real runner's polling schedule, all broker rules, or live execution.
- Inputs are synthetic or incident-derived; this is not a performance backtest or evidence of a trading edge.
- No live runner, MT5 session, forward-test log, or trading configuration was changed.
- No canonical Strategy A geometry or execution rule was established.
- Preserve previous snapshots as recorded; new evidence should be added in a new snapshot rather than silently rewriting historical conclusions.
