# SP2L G101–G103 — Recovery Guard — 2026-09-10

## Scope
Infrastructure-only. These gates protect demo recovery and do not define or modify Strategy A geometry.

## G101 — Valid recovery
Journal integrity, sequence integrity, state recovery, and reconciliation match are all required before recovery may continue.

## G102 — Integrity failure
Journal or sequence failure produces `BLOCK`.

## G103 — Uncertain recovery
Missing recovered state or failed reconciliation produces `REQUIRE_REVIEW`, never implicit continuation.

## Production boundary
The guard does not authorize production. Existing source-geometry and production-gate blockers remain authoritative.
