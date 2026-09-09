# SP2L G74–G76 — Demo Reconciliation & Emergency Safety — 2026-09-09

## G74 — Reconciliation
A deterministic reconciliation helper compares expected local order state with the broker adapter snapshot and reports `MATCH`, `MISMATCH`, or `UNKNOWN`. Unknown broker state is never treated as success.

## G75 — Event Simulation
A strategy-neutral event vocabulary supports deterministic simulation of submit acknowledgement, fill, cancel acknowledgement, replace acknowledgement, rejection, timeout, and disconnect events. This does not create Strategy A signals.

## G76 — Emergency Disconnect
The demo connection control defaults to `DISCONNECTED`. Requests are allowed only after explicit connection and are blocked again immediately after disconnect.

## Tests
Fixtures cover reconciliation match/mismatch/unknown, event preservation, and disconnect/reconnect/disconnect behavior.

## Safety boundary
- No real broker endpoint.
- No credentials.
- No Strategy A detector.
- No candidate geometry execution.
- Unknown reconciliation state does not pass.
- Disconnect is fail-closed.
- Demo infrastructure remains separate from strategy validation.

## Gate interpretation
G74: infrastructure PASS when tests pass.
G75: infrastructure PASS when tests pass.
G76: infrastructure PASS when tests pass.
Strategy A execution remains LOCKED until source geometry is frozen and DEV, untouched VAL, robustness/stability, and Fresh Holdout gates pass.
