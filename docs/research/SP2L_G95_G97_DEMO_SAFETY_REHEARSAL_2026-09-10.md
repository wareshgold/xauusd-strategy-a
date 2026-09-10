# SP2L G95–G97 — Demo Safety Rehearsal — 2026-09-10

## Scope
Infrastructure-only rehearsal. No Strategy A signal rule, geometry interpretation, production authorization, or broker execution is introduced.

## G95 — Healthy rehearsal
A fully healthy demo environment produces an explicit `PASS` rehearsal result.

## G96 — Degraded rehearsal
Disconnect or failed reconciliation prerequisites produce `BLOCK`.

## G97 — Integrity failure
Journal integrity failure produces `BLOCK`.

## Safety boundary
A rehearsal PASS is evidence that the demo safety prerequisites behave deterministically; it is not evidence that Strategy A is production-ready.
