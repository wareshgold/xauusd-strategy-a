# V2 Forward Runtime Coverage Audit Checkpoint — 2026-09-29

## Status

Research-only forensic infrastructure. Canonical Strategy A geometry, execution
semantics, and production authorization are unchanged.

## Evidence preceding this audit

For the 2026-09-28 UTC window, the exact V2 backtest contained 24 signals.
The backtest/forward reconciler found 4 matched forward signal IDs and 20
missing signal IDs.

The deterministic missing-signal detector then reconstructed all 20 missing
signals from MT5 history and classified all 20 as:

- VISIBLE_AT_TRIGGER: 20

This proves historical detector visibility only. It does not prove that the
live process was polling at each trigger.

## New audit

Script:

`scripts/audit_v2_forward_runtime_coverage.py`

Commit:

`6f24bb2cc62f50be620cccfb9af21c0cda9f01bd`

Purpose:

- inspect HEARTBEAT telemetry already emitted by the forward runner;
- determine whether each missing signal has demonstrable runtime coverage;
- distinguish process coverage from candidate-event emission;
- avoid changing detector or execution logic.

Classification:

- `PROCESS_COVERED_BUT_NO_CANDIDATE_EVENT`: a heartbeat recorded a bar at or
  after the target trigger within the configured tolerance. This is evidence
  of process/runtime coverage, not proof of exact polling or candidate
  selection.
- `PROCESS_NOT_COVERED`: heartbeat telemetry exists nearby, but none
  demonstrates a recorded bar reaching the target trigger within tolerance.
- `INSUFFICIENT_RUNTIME_TELEMETRY`: no usable heartbeat evidence is available.

Default tolerance: 180 seconds.

## Next gate

Pull the commit and run the audit against the same Monday backtest/event
artifacts. Interpret the classifications before changing the forward runner.

Do not promote any classification into canonical Strategy A rules.
