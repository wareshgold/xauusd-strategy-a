# V2 Forward Missing-Signal Audit Checkpoint — 2026-09-29

## Scope

Branch: `research/sp2l-legacy-mirror-backtest-20260929`

Previous reconciler commit: `11f2cfa60b390aca62c15efe04328469730f60c2`

Audit commit: `8d7c44ebd239d54b117abe68b96f6127751cca31`

This checkpoint adds deterministic forensic infrastructure only. It does not
change Strategy A geometry, canonical status, execution semantics, or the
forward runner.

## Observed mismatch being audited

For the 2026-09-28T00:00:00Z through 2026-09-29T00:00:00Z XAUUSD.ecn window:

- Backtest signals: 24
- Forward candidate/order-result unique signals: 5
- Exact population matches: 4
- Missing from forward: 20
- Extra forward signal: 1, outside the requested window
- All 4 matched forward orders were accepted by MT5

The unresolved question is why the 20 in-window backtest signals did not
produce corresponding forward events.

## Audit method

`scripts/audit_v2_forward_missing_signals.py` reconstructs the exact
research runner detector and its `rates(..., count=10)` lookback against
current MT5 M1 history.

For every missing backtest signal it evaluates:

1. Whether the signal is visible when the trigger bar is the latest completed
   bar in the runner's 10-bar window.
2. Whether it becomes visible after the trigger.
3. Whether a later candidate replaces it under the runner's
   `find_latest_candidate()` rule.
4. Whether the complete available MT5 history reproduces the signal at all.

The audit deliberately does **not** infer live-process polling failure from
historical visibility. Runtime process coverage requires forward telemetry.

## Interpretation boundary

The most important distinction is:

- `VISIBLE_AT_TRIGGER` proves detector visibility under the runner's exact
  historical lookback.
- It does **not** prove the live process was running/polling at that instant.
- `VISIBLE_BUT_LATER_CANDIDATE_REPLACES` is direct evidence supporting a
  latest-candidate/polling-population mechanism.
- `NOT_REPRODUCED_FROM_MT5_HISTORY` indicates a data/geometry mismatch that
  must be investigated before attributing the miss to polling.

No canonical Strategy A rule is promoted by this audit.
