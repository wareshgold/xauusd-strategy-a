# SP2L G267 — Measurement Label / Price Map

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `VOCABULARY_STRONGLY_CORRELATED__CONSTRUCTION_UNRESOLVED`

## Objective

Separate what the recurring labels mean as measurement vocabulary from what they do not prove as strategy construction rules.

## Reconstructed map

| Label | Strongest supported interpretation | What remains unknown |
|---|---|---|
| `0.0` | stop-side reference of the displayed measurement | exact source boundary used to generate S/L |
| `E` | Entry reference | exact OHLC anchor for pending order |
| `2x` | midpoint marker between `0.0` and `E` | whether/where it participates in Entry/TP construction |
| `1` | first target-side measurement level | whether it is TP1, an intermediate reference, or another source-defined level |
| `2` | second target-side measurement level | whether it is terminal TP, projection endpoint, or another reference |

## Numerical cross-check

Example A:

- `S/L = 3237.12`
- `E/Entry = 3229.08`
- midpoint = `3233.10`

This gives the exact arithmetic relation:

`2x = (0.0 + E) / 2`

for the displayed practical example.

Example B:

- `S/L = 3235.50`
- `E/Entry = 3223.84`
- midpoint = `3229.67`

Again the same midpoint construction is numerically available and visually consistent with the `2x` marker.

## Important boundary

The labels are useful source evidence for a measurement tool/convention. They are **not independently sufficient** to define the Strategy A executable geometry.

In particular, no canonical rule is created for:

- Entry anchor;
- stop buffer;
- TP1/TP2 execution;
- AB=CD anchors;
- target selection;
- intrabar execution.

## Gate decision

Promote the label meanings only to the source-ledger/measurement-vocabulary layer. Keep executable construction unresolved and fail-closed.
