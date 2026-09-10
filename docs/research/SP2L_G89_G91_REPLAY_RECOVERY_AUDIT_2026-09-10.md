# SP2L G89–G91 — Replay, Recovery & Audit — 2026-09-10

## Scope
Infrastructure-only continuation after G86–G88 CI green. No Strategy A geometry or signal decision logic is introduced.

## G89 — Deterministic replay audit
Journal events are replayed strictly by authoritative sequence. Sequence gaps fail closed. Timestamps remain metadata/validation fields and do not override sequence authority.

## G90 — Recovery audit
Restart reconstruction is audited from persisted journal events. The resulting order status is explicit and traceable to the replayed event stream.

## G91 — Empty/unknown recovery
An empty journal or unknown order cannot be treated as a successful recovered order. Recovery remains fail-closed until sufficient evidence exists.

## Invariants
- Sequence is authoritative for replay.
- Sequence gaps are invalid.
- Unknown recovery state is never success.
- No live venue or broker connectivity is introduced.
- Strategy A remains production-blocked while source geometry is unresolved.

## Validation
Fixtures cover deterministic sequence replay, sequence-gap rejection, filled-state reconstruction, and empty-journal non-success.
