# SP2L G98–G100 — Integrity Boundary — 2026-09-10

## Scope
Infrastructure-only. No Strategy A geometry, signal generation, or production authorization is introduced.

## G98 — Integrity gate
A journal-valid, sequence-valid, successfully recovered state is explicitly eligible to continue the demo lifecycle.

## G99 — Fail-closed integrity
Journal or sequence corruption blocks progression.

## G100 — Unknown recovery
A state that has not been successfully recovered is `UNKNOWN`, never implicit success.

## Production boundary
These demo integrity decisions do not override the existing production gate. Strategy A remains blocked while source geometry is unresolved.
