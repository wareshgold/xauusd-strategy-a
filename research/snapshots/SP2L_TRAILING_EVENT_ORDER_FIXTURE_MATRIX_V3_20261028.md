# Follow-up Snapshot — Trailing Event-Order Fixture Matrix v3

- Snapshot ID: `SP2L-TRAILING-EVENT-ORDER-FIXTURE-MATRIX-V3-20261028`
- Recorded: 2026-10-28
- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/position-64500649-m1-boundary-audit-20261028`
- Code/test commit: `5e1805784ac0b6f5e3c1e7ff4ebf4ee63f06d804`
- Related PR: [#363](https://github.com/wareshgold/xauusd-strategy-a/pull/363), open, Draft, unmerged.
- Prior baseline: `SP2L-TRAILING-DIAGNOSTIC-BOUNDARIES-V2-20261028.md`

## Added offline diagnostic

Added `scripts/audit_trailing_event_sequence.py` and `tests/test_audit_trailing_event_sequence.py`.

The helper labels supplied timestamps relative to the M1 interval, position entry, and decision time, then reports the inspected SELL arithmetic and guards separately. It is a fixture diagnostic, not a full live-runner emulator.

## Fixture coverage

1. Incident-shaped mid-bar entry where the supplied bar low predates entry; reports full-bar movement, candidate SL, monotonic improvement check, and Ask-distance guard independently.
2. Low timestamp after entry within the entry bar.
3. A bar that completed before the position entry, distinguished from the entry bar.
4. Favorable movement below the supplied activation threshold.
5. SELL Ask-distance guard at exact equality.
6. Candidate that does not improve the existing SELL SL.
7. Reject decision timestamps before bar completion.
8. Reject bar-low timestamps outside the M1 interval.
9. Reject BUY fixtures because its corresponding high/geometry has not been modeled in this SELL-only helper.

## Validation status

At snapshot time, GitHub's combined-status and workflow-run queries returned no status entries for commit `5e1805784ac0b6f5e3c1e7ff4ebf4ee63f06d804`. Therefore this snapshot does **not** claim that the new tests or the latest commit passed CI. Re-check CI before treating the addition as validated.

## Boundaries

- No production/live runner, MT5 session, event log, or trading configuration was changed.
- No live order action or BUY/SELL recommendation is produced.
- No canonical Strategy A geometry or execution rule is defined.
- The tests assert only diagnostic timestamp/arithmetic labels and observed guard conditions; they do not establish correct strategy semantics, tick coverage, polling cadence, or broker outcomes.
- This snapshot is additive. Earlier snapshots remain unchanged.
