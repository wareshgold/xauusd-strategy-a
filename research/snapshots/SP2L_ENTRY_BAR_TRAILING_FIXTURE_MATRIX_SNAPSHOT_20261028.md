# Follow-up Snapshot — Entry-Bar Trailing Synthetic Fixture Matrix

- Snapshot ID: `SP2L-ENTRY-BAR-TRAILING-FIXTURE-MATRIX-20261028`
- Recorded: 2026-10-28
- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/position-64500649-m1-boundary-audit-20261028`
- Snapshot commit parent / tested code commit: `aed6f02e8d5d338b16fba04d62391babb1f614c0`
- Original incident evidence snapshot: `research/snapshots/SP2L_POSITION_64500649_ENTRY_BAR_AUDIT_SNAPSHOT_20261028.md`
- Related PR: [#363](https://github.com/wareshgold/xauusd-strategy-a/pull/363), still Draft and unmerged.

## Additional offline cases

The diagnostic helper now permits a supplied bar-low timestamp anywhere inside the specified M1 bar and keeps the contamination label conditional on the timestamps and movements. Added deterministic cases:

1. **Incident contamination:** full-bar favorable move 0.67 passes the 0.40 activation threshold, but the bar low occurred before entry and the post-entry favorable move is only 0.05.
2. **Clean exact-boundary case:** low occurs after entry; both full-bar and post-entry favorable movement equal exactly 0.40; contamination is false.
3. **Below-threshold case:** low occurs after entry; favorable movement is 0.21; activation test is false.
4. **Input validation:** reject a bar that does not contain the entry timestamp and reject a claimed post-entry minimum timestamp that precedes entry.

## Validation

GitHub Actions completed successfully on code commit `aed6f02e8d5d338b16fba04d62391babb1f614c0`:
- SP2L forensic deterministic checks — run 624 — success.
- Factory Research Tests — run 1066 — success.

## Boundaries

- Offline tests only; no MT5 connection or order actions.
- No live runner, live configuration, forward-test log, or canonical Strategy A rules were changed.
- These are diagnostic fixtures, not an endorsed trailing rule or evidence of strategy-wide edge.
- The incident snapshot above remains the immutable baseline for the original observed facts; this follow-up records the added test coverage separately.
