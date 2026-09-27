# XAUUSD Raw-Bar Boundary Forensics — Aggregate Checkpoint

Date: 2026-09-27  
Branch: `research/sp2l-strategy-a-v2-2026-09-27`

## Evidence

Input forensic population: 58 unique unresolved non-weekend XAUUSD gaps.

Observed raw-bar boundary classification:

- `EXACT_23:59_TO_01:00`: 21
- `23:58_TO_01:00`: 36
- `23:59_TO_00:59`: 0
- `OTHER`: 1

The single known `OTHER` observation is:

`2026-09-07T21:37:00+00:00 -> 2026-09-08T00:59:00+00:00`

with raw boundary:

`2026-09-07T21:36:00+00:00 -> 2026-09-08T01:00:00+00:00`

## Interpretation boundary

These observations establish a recurring raw M1 boundary pattern in the sampled XAUUSD data. They do **not** establish broker session closure, maintenance, or any other causal explanation.

Therefore:

- `SESSION_CAUSE=UNRESOLVED`
- `SESSION_APPROVAL=NOT_ESTABLISHED`
- no session closure is promoted to a canonical data rule
- the 2026-09-07 observation remains an isolated outlier

## Next deterministic aggregation

Run:

`scripts/sp2l_xauusd_raw_bar_forensic_aggregate.py`

against the unique raw-bar forensic artifact to calculate weekday counts, monthly recurrence, observed boundary-minute distribution, and the isolated outlier in one machine-readable report.

This remains research-only and cannot promote Strategy A geometry or execution semantics.
