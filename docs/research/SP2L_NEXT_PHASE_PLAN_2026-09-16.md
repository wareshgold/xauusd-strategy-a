# SP2L Next Phase Plan — 2026-09-16

## Objective

Continue source resolution in bounded batches without promoting unresolved geometry.

## Planned sequence

### Batch 1 — Completed
1. F10 source boundary.
2. F11 pending-limit semantics.
3. F12 trigger-family semantics.
4. F13 2X boundary.
5. F14 AB=CD boundary.

### Batch 2 — Completed
6. F15 bearish fixture/source boundary.
7. P-Gap source-evidence cross-reference.
8. Gate impact documentation.

### Batch 3 — Next
9. Reconcile all source records into one blocker matrix.
10. Identify which unresolved questions can be discriminated by additional source frames/transcript evidence rather than by backtest.
11. Verify the full synthetic fixture suite locally/CI; do not claim CI success until an actual run exists.
12. Audit baseline implementation for any rule that is currently stronger than its source status.
13. Freeze only source-discriminated semantics; leave exact geometry blocked where evidence remains insufficient.

## Non-negotiable controls

- No performance-driven geometry selection.
- No invented P-Gap formula.
- No invented AB=CD anchors or tolerance.
- No invented 2X formula.
- No minimum-risk filter to suppress extreme-R observations.
- No production BUY/SELL generation.

## Current gate

Source Resolution: `PARTIAL PASS`

Synthetic Fixtures: `PASS`

Frozen Geometry: `BLOCKED`

Untouched Validation: `LOCKED`

Robustness/Stability: `LOCKED`

Fresh Holdout: `LOCKED`

Production: `OFF`
