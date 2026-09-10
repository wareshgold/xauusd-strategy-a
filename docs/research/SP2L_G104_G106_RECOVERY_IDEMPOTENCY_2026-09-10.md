# SP2L G104–G106 — Recovery Idempotency — 2026-09-10

## Scope
Infrastructure-only. No Strategy A geometry, entry, target, or production signal rule is introduced.

## G104 — Stable recovery fingerprint
The same recovered order state produces the same deterministic fingerprint.

## G105 — State mutation detection
A recovered state change produces a different fingerprint.

## G106 — Sequence mutation detection
A sequence change produces a different fingerprint.

## Safety boundary
Fingerprints are integrity/audit evidence only. They do not authorize production execution and do not alter the existing fail-closed production gate.
