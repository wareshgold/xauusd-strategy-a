# SP2L Coding Test 1 — Continuous Poll Forensics Test Checkpoint

Date: 2026-09-26

## Checkpoint

- Branch: `research/sp2l-pgap-source-aligned-2026-09-26`
- Previous checkpoint: `9e4ddd6`
- Coding-test commit: `ddcf62b`
- Scope: research/forensics only

## Change

Added:

`tests/test_sp2l_continuous_poll_forensics.py`

The test module covers the existing deterministic `serialize_bar()` helper only.

Assertions cover:

1. Preservation of the raw MT5 timestamp.
2. Deterministic UTC interpretation of the timestamp.
3. Preservation of OHLC values.
4. Integer normalization of tick volume, spread, and real volume.
5. Deterministic repeated serialization.

No production code was changed.

## Test result

Focused test:

```
4 passed in 0.27s
```

Full Python test suite at checkpoint time:

```
139 passed
6 failed
```

The six failures are in pre-existing/unrelated areas:

- `tests/test_live_report_telegram.py` — 2 failures
- `tests/test_live_session_infra.py` — 2 failures
- `tests/test_sp2l_forward_backtest_reconciliation_invariants.py` — 1 failure
- `tests/test_sp2l_forward_backtest_reconciliation_v1.py` — 1 failure

The full-suite failures are not attributed to Coding Test 1 because the diff from the pre-test checkpoint contains only the new test file.

## Diff isolation

`git diff --stat 9e4ddd6..HEAD` reported only:

```
tests/test_sp2l_continuous_poll_forensics.py | 62 ++++++++++++++++++++++++++++
1 file changed, 62 insertions(+)
```

Therefore no runner, Strategy A geometry, P-Gap, detector, execution, Telegram production, or canonical rule was changed by this coding test.

## Safety boundary

This checkpoint does not establish or change:

- canonical P-Gap geometry
- candle-role mapping
- trigger acceptance semantics
- entry/fill semantics
- stop-loss anchor
- AB=CD anchors or tolerance
- pending-order lifecycle
- production BUY/SELL logic

The continuous polling forensic runner remains detector-independent and research-only.

## Interpretation

Coding Test 1 is a successful deterministic test addition, but it is not a claim that the entire repository test suite is green.

The six unrelated full-suite failures remain separately tracked and must not be silently folded into this forensic test result.

## Next controlled step

Review the continuous polling runner's record/coverage semantics and determine whether additional deterministic tests can be added without changing polling behavior or Strategy A semantics.

No live trading, Telegram sending, or canonical promotion is part of this step.
