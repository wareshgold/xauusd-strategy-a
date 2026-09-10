# SP2L G86–G88 — Demo Journal Integrity, Event Ordering, Restart Recovery

## Scope
Infrastructure-only. No Strategy A geometry or production signal authorization is introduced.

## G86 — Journal Integrity
Recovery events carry contiguous sequence numbers and a hash-chain predecessor. Verification fails on sequence, timestamp, predecessor, or event-content inconsistency.

## G87 — Event Ordering
Sequence is authoritative for replay order. Events must be contiguous and their UTC timestamps must not move backwards.

## G88 — Restart Recovery
Restart recovery reconstructs an order state from the persisted recovery journal rather than assuming the in-memory state survived the process restart.

## Safety boundary
Invalid journal state, invalid ordering, or failed reconstruction must fail closed. This layer does not decide BUY/SELL and cannot authorize production execution while source geometry remains unresolved.

## Validation
Fixtures cover journal integrity/tamper detection, backward timestamps, strict sequence ordering, and deterministic order-state reconstruction after restart.
