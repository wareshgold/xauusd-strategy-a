# SP2L MT5 Reproducibility Stage Checkpoint — 2026-09-21

## Completed in this stage
- inspected direct MT5 API acquisition runner;
- inspected committed export replay runner;
- inspected interval/boundary validation harness;
- defined same-window API-vs-export comparison contract;
- preserved raw timestamp/provenance requirements;
- prevented silent timezone shifting;
- kept Strategy A geometry isolated from acquisition comparison.

## Current status
- Direct MT5 runner: READY
- Export replay: READY
- Comparison contract: READY
- Local terminal execution: REQUIRED
- API-vs-export equivalence: NOT YET VERIFIED
- Timestamp basis: UNRESOLVED
- Session normalization: BLOCKED
- Frozen Geometry: BLOCKED
- Production: DISABLED

## Required local execution
Run the direct API runner and compare its artifact against the same-window committed export. Do not alter PGAP, spike multiplier, SL, TP, entry, or geometry parameters to make the datasets agree.

## Decision
No equivalence or production-data claim is made until the local terminal produces the comparison evidence.
