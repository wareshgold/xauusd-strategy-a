# SP2L Test Failure Fixes Checkpoint

Date: 2026-09-26

## Scope

This checkpoint addresses two deterministic reconciliation failures identified in the previously reported Python test run.

No Strategy A geometry, P-Gap rule, detector rule, fill semantics, order execution rule, or canonical rule is changed.

## Fix 1 — raw trigger identity

Commit: `7cb8d42d883b732ee99f9c33bad91d32ca88f883`

File:

`scripts/sp2l_forward_backtest_reconciliation.py`

Previous behavior allowed an exact `signal_id` match to select an event even when the event's embedded raw `candidate.trigger_time` disagreed with the historical candidate timestamp.

This violated the fail-closed identity boundary.

New behavior:

- `signal_id` remains only an index key.
- An ID-selected event is accepted only when its embedded raw trigger timestamp exactly matches the historical raw trigger timestamp.
- Otherwise the code falls through to the exact raw-trigger search.
- No timezone normalization or fuzzy matching is introduced.

This preserves the intended invariant:

**A signal ID cannot override a mismatched raw trigger time.**

## Fix 2 — reconciliation test expectation

Commit: `bb69150f6e73e04ace06f976e44544392bcbc4f7`

File:

`tests/test_sp2l_forward_backtest_reconciliation_v1.py`

The test `test_exact_candidate_with_order_placed_is_match` contained one historical candidate with a forward candidate and order placement, plus a second historical candidate with no exact forward timestamp match.

Under the current fail-closed semantics, the second candidate is:

`TIMESTAMP_UNRESOLVED`

rather than `DATA_GAP`, because the supplied forward log contains candidate evidence but no exact raw timestamp identity for that historical candidate.

The test expectation was corrected accordingly.

## Remaining reported failures

The earlier full-suite run also reported four Telegram/session-infrastructure failures. Those are not changed blindly in this checkpoint because they are environment/configuration-sensitive and the repository snapshot alone does not establish their exact local failure state.

They must be re-run after pulling these deterministic fixes. If they reproduce, the next step is to diagnose their exact failure output before modifying code or tests.

## Validation boundary

These fixes are harness/test semantics only. They do not establish Strategy A geometry or trading validity.

Next validation step:

1. pull the two commits on the local branch;
2. run the focused reconciliation tests;
3. run the full Python suite;
4. separately run the requested two-week XAUUSD MT5 backtest for the latest completed two-week window;
5. record the backtest artifact and statistics without promoting any research rule to canonical status.
