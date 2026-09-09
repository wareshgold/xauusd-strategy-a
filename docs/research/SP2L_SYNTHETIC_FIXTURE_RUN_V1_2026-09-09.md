# SP2L Synthetic Fixture Run v1 — 2026-09-09

## Scope

This run validates the research fixture layer only. It does not backtest Strategy A and does not choose unresolved source geometry.

## Implemented

- F02: first Low vs relevant/current higher-Low candidates
- F03: entry vs Leg-2 start separation
- F05: wick extreme vs body edge separation
- F06: structural invalidation / pending-order replacement state space
- deterministic serialization and invariant tests

## Expected invariants

1. Candidate anchors remain explicit and separate.
2. Entry and Leg-2 start are independently representable.
3. Wick and body anchors are not silently aliased.
4. KEEP/DELETE/REPLACE order states are representable without inventing the replacement threshold.
5. Fixture generation is deterministic.

## Deliberately deferred

F01 P-Gap vs generic imbalance, F04 A/B/C/D alternatives, F07 overextension, and F08 range-context discrimination remain design-level fixtures pending the next source-resolution pass. No production classifier is derived from them.

## Gate assessment

**SYNTHETIC FIXTURE DESIGN: PASS**

**SYNTHETIC FIXTURE IMPLEMENTATION: PARTIAL PASS** — the first discrimination-critical fixtures and tests are implemented; unresolved geometry remains intentionally unresolved.

**FROZEN GEOMETRY: NOT PASSED**

No historical optimization is authorized by this run.
