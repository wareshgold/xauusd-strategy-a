# SP2L Frozen-Geometry Readiness Gate — 2026-09-14

## Purpose

This gate determines whether Strategy A executable geometry is ready to be frozen after the source-resolution stop and synthetic-fixture contract.

It is a **readiness gate only**. It does not define, select, infer, or promote executable geometry.

## Governance

Source meaning outranks backtest performance. Only Tier-1/Tier-2 source evidence that uniquely discriminates a rule may support canonicalization, followed by manual adjudication.

No unresolved geometry may be promoted because it performs well in a backtest.

## Source-confirmed semantics currently available

- Breakout / follow-through / P-GAP semantics are source-supported.
- Two observed P-GAP orderings are treated by the source as the same strategy family.
- A 1/2/3-candle trigger family is source-supported, but its deterministic classifier is unresolved.
- Correction precedes the second leg; corrective entry behavior is source-supported.
- Structural invalidation is distinct from risk-stop semantics.
- Pending-limit handling can include delete/replace/retain behavior, but its deterministic condition is unresolved.
- Leg 2 is described as matching Leg 1 in magnitude at the source meaning level.
- Buy/Sell, SL, 2X, TP1 and TP2 concepts are shown/discussed, but their complete executable formulas are unresolved.
- A bearish structural example exists, but a deterministic bearish mirror remains unresolved.

These statements are source semantics, not executable OHLC rules.

## Executable geometry status

All dimensions below remain `BLOCKED` pending a source discriminator and manual adjudication:

| Dimension | Status | Freeze decision |
|---|---|---|
| P-Gap exact formula / candle indices / OHLC boundaries | BLOCKED | NOT READY |
| Entry exact price anchor | BLOCKED | NOT READY |
| Leg-2 start anchor | BLOCKED | NOT READY |
| Structural invalidation exact boundary | BLOCKED | NOT READY |
| Pending refresh deterministic condition | BLOCKED | NOT READY |
| 1/2/3-candle trigger classifier | BLOCKED | NOT READY |
| AB=CD A/B/C/D anchors | BLOCKED | NOT READY |
| AB=CD equality tolerance | BLOCKED | NOT READY |
| 2X / TP1 / TP2 executable construction | BLOCKED | NOT READY |
| Deterministic bearish mirror | BLOCKED | NOT READY |

## Gate criteria

The readiness gate passes only if:

1. Every executable geometry dimension has a unique source-supported interpretation.
2. Required candle indexing and OHLC boundaries are source-discriminated.
3. Entry, invalidation, pending-order, trigger, target and bearish-mirror semantics are executable without invented constants.
4. AB=CD anchors and equality tolerance are source-supported.
5. No geometry is selected by performance optimization.
6. The resulting geometry receives explicit manual adjudication before canonicalization.

Current result: **NOT READY — SOURCE GEOMETRY REMAINS BLOCKED**.

## Explicit non-actions

This gate does not:

- implement a generic P-GAP or imbalance formula;
- assume Fibonacci or percentage retracement semantics;
- invent AB=CD anchors or tolerances;
- invent candle indexing, fill semantics, buffers, refresh thresholds, or target formulas;
- emit BUY/SELL decisions;
- authorize production execution;
- authorize untouched validation or live trading.

## Next admissible transition

The next transition is either:

**NEW TIER-1/TIER-2 DISCRIMINATING SOURCE EVIDENCE → manual adjudication → frozen geometry**, or, if no such evidence exists, maintain the documented source-resolution stop condition.

Synthetic fixtures and deterministic replay plumbing may continue to exercise contracts around unresolved dimensions, but they must not silently resolve them.
