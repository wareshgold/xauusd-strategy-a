# SP2L Resolution Coverage Audit — 2026-09-21

| Family | Status | Current blocker |
|---|---|---|
| F08 Swing | COVERED_UNRESOLVED | deterministic swing/pivot + wick/body field |
| F09 Entry | COVERED_UNRESOLVED | exact price field + trigger/activation precedence |
| F10 Stop | COVERED_UNRESOLVED | exact field/buffer/invalidation |
| F11 Lifecycle | COVERED_UNRESOLVED | replacement/delete/timeout/fill semantics |
| F12 Trigger | COVERED_UNRESOLVED | touch/breach/close/fill/activation |
| F13 2X | SOURCE_CONFIRMED_PARTIAL | lifecycle, sizing, shared SL/TP behavior |
| F14 AB=CD | COVERED_UNRESOLVED | A/B/C/D anchors + tolerance |
| F15 Bearish | NOT_INDEPENDENTLY_DEMONSTRATED | independent bearish P-Gap/executable proof |

## Remaining source blockers
1. F08 deterministic swing selection.
2. F10 exact stop field/buffer/invalidation.
3. F09 exact entry geometry and precedence.
4. F14 exact AB=CD anchors/tolerance.
5. F11/F12 execution lifecycle.
6. F15 independent bearish executable evidence.
7. F13 lifecycle/risk aggregation.

**Gate: PASS — coverage audit complete; Frozen Geometry remains BLOCKED.**

No production or forward-test logic changed.