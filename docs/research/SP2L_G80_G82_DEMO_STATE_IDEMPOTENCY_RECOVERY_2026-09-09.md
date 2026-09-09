# SP2L G80–G82 — Demo Order State Machine, Idempotency & Recovery — 2026-09-09

## Scope
Infrastructure-only work. No Strategy A geometry, signal generation, broker connectivity, or execution authorization is introduced.

## G80 — Order State Machine
`PENDING` may transition deterministically to `FILLED`, `CANCELLED`, or `EXPIRED`. Terminal states have no further valid transitions. Invalid transitions raise explicitly.

## G81 — Idempotency
Demo submission is deduplicated by the immutable local `order_id`. A repeated submission returns the original broker receipt and is marked as a duplicate rather than creating another order.

## G82 — Recovery / Reconciliation Loop
A reconciliation result is evaluated before automated continuation. `MATCH` can continue only when the existing demo safety gate allows execution. `MISMATCH` and `UNKNOWN` require review and always produce `BLOCK` execution.

## Safety invariants
- Unknown broker state is never success.
- Repeated submit retries do not create duplicate demo orders.
- Kill/disconnect remains fail-closed.
- Strategy intent remains data; infrastructure does not derive BUY/SELL decisions.
- Production remains blocked while source geometry is unresolved.

## Validation
Unit fixtures cover valid/invalid state transitions, duplicate submit behavior, reconciliation MATCH continuation, and MISMATCH/UNKNOWN recovery blocking.
