# SP2L G83–G85 — Demo Recovery Durability — 2026-09-09

## G83 — Recovery Journal
An append-only in-memory journal records monotonically increasing sequence numbers, timestamp, order id, event and detail. This is a demo/research primitive only; it is not a durable external store.

## G84 — Event Ordering
Events are accepted only when their sequence equals the next expected sequence. Gaps and reordering fail explicitly rather than being silently repaired.

## G85 — Crash/Restart Recovery
Order state can be reconstructed deterministically from the journal for known lifecycle events. Unknown events are ignored rather than interpreted as successful execution.

## Safety boundary
- No real broker/network integration.
- No Strategy A geometry or BUY/SELL generation.
- Recovery cannot convert UNKNOWN/MISMATCH into success.
- Production remains fail-closed while source geometry and validation gates remain unresolved.

## Validation
Fixtures cover journal ordering, out-of-order rejection, terminal-state reconstruction, and preservation of unknown-event uncertainty.
