# SP2L G264 — Source Geometry Candidate Matrix

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `PARTIAL_FREEZE__FULL_EXECUTABLE_GEOMETRY_BLOCKED`

## Purpose

Consolidate G261–G263 and prior source audits into one fail-closed matrix. A candidate is promoted only when the source evidence independently establishes the required construction. Visual compatibility alone is insufficient.

## Candidate matrix

| Component | Candidate | Evidence status | Production admissible? |
|---|---|---|---|
| Entry | explicit pending BuyLimit/SellLimit reference | directly repeated | **YES semantic / NO price formula** |
| Entry | correction extreme | visually possible | **NO** |
| Entry | correction candle Low/High | plausible | **NO** |
| Entry | P-Gap boundary | plausible | **NO** |
| Entry | spike-origin extreme | plausible | **NO** |
| Entry | `E` measurement coordinate | strongly correlated with practical examples | **NO as construction rule** |
| SL | structural level behind Spike-origin candle | directly repeated/source-confirmed | **YES semantic / NO exact OHLC** |
| SL | exact bullish `Low(origin)` | visually compatible | **NO** |
| SL | exact bearish `High(origin)` | mirror hypothesis only | **NO** |
| SL | wick/body/buffer variant | unresolved | **NO** |
| Measurement | `0.0` = stop-side reference | repeated practical correlation | **YES as vocabulary** |
| Measurement | `E` = Entry reference | repeated practical correlation | **YES as vocabulary** |
| Measurement | `2x` = midpoint between stop and Entry | strong numerical/visual correlation | **YES as vocabulary; not a separate rule** |
| Measurement | `1`, `2` = successive target-side levels | repeated schematic/practical correlation | **YES as vocabulary** |
| TP | TP1 = 1 risk interval in clean schematic | strong schematic geometry | **NO terminal execution rule** |
| TP | TP2 = 2 risk intervals in clean schematic | strong schematic geometry | **NO terminal execution rule** |
| TP | terminal TP = TP2 | not established | **NO** |
| TP | terminal TP = exact 2R | contradicted by at least one practical numeric example unless another construction variable is known | **NO** |
| TP | terminal TP = AB=CD endpoint | AB=CD semantic confirmed, identity with TP not confirmed | **NO** |
| TP | terminal TP = round level | round-level concept confirmed, selector not confirmed | **NO** |
| AB=CD | explicit AB=CD relationship | directly source-confirmed | **YES semantic / NO anchors** |
| AB=CD | D = TP | not established | **NO** |
| AB=CD | C = Entry/fill | not established | **NO** |

## Cross-example consistency findings

### Entry

The source repeatedly distinguishes an Entry/BuyLimit level from the structural SL and later presents a clean schematic with an explicit `Entry` label. This confirms the **existence and role** of the Entry reference, but no independently labeled OHLC anchor survives the cross-reference.

### Structural SL

Bullish examples repeatedly place SL beneath the origin portion of the Spike. This strongly supports the source semantic “behind the candle from which the Spike originated.” The drawings do not resolve whether the executable value is the exact wick Low, body boundary, or Low plus/minus a buffer, and the bearish mirror is not independently frozen by this batch.

### Measurement labels

The practical order panel and clean schematic provide a coherent reusable measurement vocabulary. In the ~21:40 example, Entry `3229.08` and SL `3237.12` give a midpoint of `3233.10`, matching the visual location of `2x`. This is evidence for the measurement convention, not evidence that `2x` determines Entry.

### Target geometry

The clean schematic strongly depicts TP1 at roughly 1 Entry→SL risk interval and TP2 at roughly 2 intervals. The practical order example has T/P `3213.44` versus a simple 2R value of `3213.00` from Entry `3229.08` and SL `3237.12`. The discrepancy is retained as unresolved evidence rather than assigned a tolerance or execution adjustment. Other visible order rows further prevent a one-to-one mapping from a single target label to every order.

## Source-resolution gate decision

### Frozen / safe to carry forward

1. SP2L uses a pending-limit entry mechanism.
2. Entry is a distinct source-defined reference from structural SL.
3. Structural SL is placed behind the Spike-origin candle.
4. `0.0 / 2x / E / 1 / 2` are source-correlated measurement labels.
5. AB=CD is an explicit source relationship.
6. TP1 and TP2 are explicit source target references.

### Still blocked

1. Exact Entry OHLC anchor.
2. Exact SL OHLC boundary and buffer.
3. Bearish executable mirror for Entry/SL.
4. A/B/C/D anchors for AB=CD.
5. AB=CD tolerance/equality semantics.
6. Leg 1 executable endpoints.
7. Leg 2 projection equation.
8. Terminal TP selection.
9. Rounding/spread/partial-close semantics.
10. Intrabar versus close-based invalidation/target semantics.

## Gate result

`SOURCE RESOLUTION: PASS_PARTIAL`  
`SYNTHETIC FIXTURES: ALLOWED FOR COMPETING HYPOTHESES ONLY`  
`FROZEN GEOMETRY: BLOCKED_FOR_FULL_EXECUTION`  
`DEV: BLOCKED_FOR_CANONICAL_ENGINE`  
`UNTOUCHED VALIDATION: PROTECTED`  
`FRESH HOLDOUT: PROTECTED`  
`PRODUCTION: BLOCKED`

## Next highest-value source task

The remaining ambiguity is now sharply bounded. The next source pass should seek a **single continuous example in which the teacher identifies the Entry price numerically or with an unambiguous OHLC anchor and then carries the same construction through SL, AB=CD, and terminal TP**. Until that evidence exists, do not choose among the candidate formulas by backtest performance.
